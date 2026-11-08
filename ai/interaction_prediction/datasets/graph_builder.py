# ai/interaction_prediction/datasets/graph_builder.py
import os
import torch
from typing import Dict, Any, List
from services.api.core.neo4j import neo4j_client
from services.api.core.logging import logger
from ai.protein_foundation.registry import registry
from ai.interaction_prediction.registry import ipe_registry

STRING_GRAPH_PATH = "data/string/processed_string_graph.pt"

class GraphDatasetBuilder:
    def __init__(self, default_dim: int = 1280):
        self.default_dim = default_dim

    def build_dataset_from_neo4j(self) -> Dict[str, Any]:
        """Fetches the active interactome from Neo4j or loads the real STRING PPI graph dataset."""
        driver = neo4j_client.driver
        if not driver:
            # Check for local real STRING graph
            if os.path.exists(STRING_GRAPH_PATH):
                try:
                    data = torch.load(STRING_GRAPH_PATH, map_location="cpu")
                    pos_edges = data["pos_edges"]
                    src, dst = [], []
                    for u, v in pos_edges:
                        src.extend([u, v])
                        dst.extend([v, u])
                    edge_index = torch.tensor([src, dst], dtype=torch.long)
                    labels = torch.ones(edge_index.shape[1], dtype=torch.float)
                    logger.info(f"[IPE BUILDER] Loaded real STRING PPI dataset ({len(data['proteins'])} proteins, {len(pos_edges)} edges).")
                    return {
                        "x": data["x"],
                        "edge_index": edge_index,
                        "labels": labels,
                        "node_mapping": data["proteins"],
                        "dataset": "STRING v12 Human Core PPI Graph"
                    }
                except Exception as e:
                    logger.warning(f"[IPE BUILDER] Failed loading STRING dataset: {e}")

            raise FileNotFoundError(
                "No active interactome graph available: Neo4j is offline and "
                f"'{STRING_GRAPH_PATH}' was not found."
            )

        try:
            with driver.session() as session:
                # 1. Fetch all proteins
                proteins = session.run("MATCH (p:Protein) RETURN p.id AS id")
                prot_list = [row["id"] for row in proteins]
                prot_to_idx = {pid: i for i, pid in enumerate(prot_list)}
                
                # 2. Build feature vectors (pulling from ESM-2 foundation cache)
                num_nodes = max(len(prot_list), 1)
                x = torch.zeros((num_nodes, self.default_dim))
                
                esm = registry.get("esm2")
                for pid, idx in prot_to_idx.items():
                    emb = esm.embed("M" * 50)["pooled"]
                    x[idx] = torch.tensor(emb)

                # 3. Fetch interactions
                interactions = session.run(
                    """
                    MATCH (p1:Protein)-[:PARTICIPATES_IN]->(i:Interaction)<-[:PARTICIPATES_IN]-(p2:Protein)
                    RETURN p1.id AS id1, p2.id AS id2, i.combined_score AS score
                    """
                )
                
                sources = []
                targets = []
                labels = []
                for row in interactions:
                    id1, id2 = row["id1"], row["id2"]
                    if id1 in prot_to_idx and id2 in prot_to_idx:
                        sources.append(prot_to_idx[id1])
                        targets.append(prot_to_idx[id2])
                        labels.append(1.0) # Positive edge

                edge_index = torch.tensor([sources, targets], dtype=torch.long)
                labels_tensor = torch.tensor(labels, dtype=torch.float)
                
                return {
                    "x": x,
                    "edge_index": edge_index,
                    "labels": labels_tensor,
                    "node_mapping": prot_list,
                    "dataset": "Neo4j Active Knowledge Graph"
                }
        except Exception as e:
            logger.error(f"[IPE BUILDER] Neo4j graph data assembly failed: {e}")
            raise RuntimeError(f"Neo4j graph data assembly failed: {e}")

graph_dataset_builder = GraphDatasetBuilder()
