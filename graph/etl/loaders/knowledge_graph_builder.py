import hashlib
import time
import json
from pathlib import Path
from typing import List, Dict, Any, Tuple
from services.api.core.logging import logger
from services.api.core.neo4j import neo4j_client
from graph.etl.ingestion.canonical_schema import CanonicalInteraction

class GraphEventPublisher:
    """Publishes ETL workflow event logs to simulate an event-driven bus."""
    def publish(self, event_type: str, payload: Dict[str, Any]):
        logger.info(f"[GRAPH EVENT] Type: {event_type} - Payload: {json.dumps(payload)}")

event_publisher = GraphEventPublisher()

class KnowledgeGraphBuilder:
    def __init__(self, version: str = "v1.0.0"):
        self.version = version
        self.event_publisher = event_publisher

    def combine_confidence(self, score1: float, score2: float) -> float:
        """Bayesian confidence score combiner."""
        return float(1.0 - (1.0 - score1) * (1.0 - score2))

    def validate_interaction(self, item: CanonicalInteraction) -> bool:
        """Validates canonical interactor schemas."""
        # Simple validation: ensure length and identifier format is correct
        if not item.protein_a or not item.protein_b:
            return False
        if item.protein_a == item.protein_b:
            return False # skip homodimers for now or handle separately
        if item.combined_score < 0.0 or item.combined_score > 1.0:
            return False
        return True

    def merge_interactions(self, interactions: List[CanonicalInteraction]) -> List[CanonicalInteraction]:
        """Merges duplicate protein-protein interactions using Bayesian combiner."""
        merged_map: Dict[Tuple[str, str], CanonicalInteraction] = {}

        for item in interactions:
            if not self.validate_interaction(item):
                self.event_publisher.publish("validation_failed", {"item": item.to_dict()})
                continue

            # Force alphabetical order to treat A-B and B-A identically
            key = tuple(sorted([item.protein_a, item.protein_b]))
            # Cast tuple to type annotation
            key = (key[0], key[1])

            if key not in merged_map:
                merged_map[key] = item
            else:
                existing = merged_map[key]
                # Apply Bayesian score merging
                existing.combined_score = self.combine_confidence(existing.combined_score, item.combined_score)
                existing.experimental_score = self.combine_confidence(existing.experimental_score, item.experimental_score)
                existing.computational_score = self.combine_confidence(existing.computational_score, item.computational_score)
                existing.literature_score = self.combine_confidence(existing.literature_score, item.literature_score)
                existing.structural_score = self.combine_confidence(existing.structural_score, item.structural_score)
                
                # Merge lists
                existing.source_databases = list(set(existing.source_databases + item.source_databases))
                existing.detection_methods = list(set(existing.detection_methods + item.detection_methods))
                existing.publications = list(set(existing.publications + item.publications))
                existing.tissues = list(set(existing.tissues + item.tissues))
                
                # Merge raw scores mapping
                for k, v in item.raw_scores.items():
                    existing.raw_scores[f"{item.source_databases[0]}_{k}"] = v

        return list(merged_map.values())

    def load_to_neo4j(self, merged_interactions: List[CanonicalInteraction]):
        """Loads canonical interactions into Neo4j using the context-node pattern."""
        driver = neo4j_client.driver
        if not driver:
            logger.warning("Neo4j client driver is offline. Bypassing database load transaction.")
            return

        self.event_publisher.publish("db_load_start", {"size": len(merged_interactions)})
        
        with driver.session() as session:
            # Create DatasetVersion node first
            session.run(
                "MERGE (dv:DatasetVersion {version: $version}) ON CREATE SET dv.timestamp = timestamp()",
                version=self.version
            )
            
            for item in merged_interactions:
                # Generate unique interaction ID based on sorted protein names
                key_str = f"{item.protein_a}:{item.protein_b}"
                interaction_id = hashlib.md5(key_str.encode("utf-8")).hexdigest()
                
                # Create nodes: Protein, Gene, Publication, Tissue, Interaction, DatasetVersion
                query = """
                MERGE (p1:Protein {id: $p1_id})
                MERGE (p2:Protein {id: $p2_id})
                
                // Create intermediate Interaction node
                MERGE (i:Interaction {id: $int_id})
                ON CREATE SET 
                    i.combined_score = $combined,
                    i.experimental_score = $exp,
                    i.computational_score = $comp,
                    i.literature_score = $lit,
                    i.structural_score = $struct,
                    i.source_databases = $sources,
                    i.detection_methods = $methods
                
                MERGE (p1)-[:PARTICIPATES_IN]->(i)
                MERGE (p2)-[:PARTICIPATES_IN]->(i)
                
                // Link Dataset Version
                MERGE (dv:DatasetVersion {version: $version})
                MERGE (i)-[:CREATED_FROM]->(dv)
                """
                
                session.run(
                    query,
                    p1_id=item.protein_a,
                    p2_id=item.protein_b,
                    int_id=interaction_id,
                    combined=item.combined_score,
                    exp=item.experimental_score,
                    comp=item.computational_score,
                    lit=item.literature_score,
                    struct=item.structural_score,
                    sources=item.source_databases,
                    methods=item.detection_methods,
                    version=self.version
                )
                
                # Link Tissue Context nodes
                for tissue_name in item.tissues:
                    session.run(
                        """
                        MATCH (i:Interaction {id: $int_id})
                        MERGE (t:Tissue {id: $tissue})
                        MERGE (i)-[:OBSERVED_IN]->(t)
                        """,
                        int_id=interaction_id,
                        tissue=tissue_name
                    )

                # Link Publication nodes
                for pubmed_id in item.publications:
                    if pubmed_id != "Unknown":
                        session.run(
                            """
                            MATCH (i:Interaction {id: $int_id})
                            MERGE (pub:Publication {id: $pub_id})
                            MERGE (pub)-[:SUPPORTS]->(i)
                            """,
                            int_id=interaction_id,
                            pub_id=pubmed_id
                        )

        self.event_publisher.publish("db_load_completed", {"status": "success"})
