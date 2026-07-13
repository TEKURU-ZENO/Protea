from typing import List, Dict, Any, Optional
from services.api.core.neo4j import neo4j_client
from services.api.core.logging import logger

class GraphService:
    def __init__(self):
        self._driver = neo4j_client

    def get_neighbors(self, protein_id: str) -> List[Dict[str, Any]]:
        """Queries Neo4j for immediate neighbors linked through Interaction nodes."""
        driver = self._driver.driver
        if not driver:
            # Fallback mock neighbors
            return [
                {"protein_id": "P01308", "interaction_id": "int_1", "confidence": 0.94, "database": "STRING"},
                {"protein_id": "Q15345", "interaction_id": "int_2", "confidence": 0.82, "database": "BioGRID"}
            ]

        try:
            with driver.session() as session:
                query = """
                MATCH (p:Protein {id: $p_id})-[:PARTICIPATES_IN]->(i:Interaction)<-[:PARTICIPATES_IN]-(neighbor:Protein)
                RETURN neighbor.id AS neighbor_id, i.id AS int_id, i.combined_score AS score, i.source_databases AS databases
                """
                results = session.run(query, p_id=protein_id)
                output = []
                for res in results:
                    output.append({
                        "protein_id": res["neighbor_id"],
                        "interaction_id": res["int_id"],
                        "confidence": float(res["score"]),
                        "databases": res["databases"]
                    })
                return output
        except Exception as e:
            logger.error(f"Neo4j query neighbor fetch failed: {e}")
            return []

    def find_shortest_path(self, p1: str, p2: str) -> List[Dict[str, Any]]:
        """Traces the shortest connection chain between two proteins."""
        driver = self._driver.driver
        if not driver:
            # Fallback mock path
            return [
                {"source": p1, "interaction": "int_123", "target": "P12345"},
                {"source": "P12345", "interaction": "int_456", "target": p2}
            ]

        try:
            with driver.session() as session:
                # Tracing shortest path through the Interaction context nodes
                query = """
                MATCH path = shortestPath((p1:Protein {id: $p1_id})-[:PARTICIPATES_IN|OBSERVED_IN|SUPPORTS*..10]-(p2:Protein {id: $p2_id}))
                RETURN path
                """
                results = session.run(query, p1_id=p1, p2_id=p2).single()
                if not results:
                    return []
                
                # Parse path into node/edge objects for visualization
                path_obj = results["path"]
                nodes = []
                for node in path_obj.nodes:
                    labels = list(node.labels)
                    nodes.append({"id": node.element_id, "label": labels[0] if labels else "Unknown", "properties": dict(node)})
                return nodes
        except Exception as e:
            logger.error(f"Neo4j shortest path query failed: {e}")
            return []

    def get_statistics(self) -> Dict[str, Any]:
        """Calculates graph counts and density statistics."""
        driver = self._driver.driver
        if not driver:
            # Mock stats
            return {
                "proteins": 190531,
                "genes": 45000,
                "interactions": 21813816,
                "pathways": 340,
                "diseases": 12000,
                "drugs": 8500,
                "density": 0.0034
            }

        try:
            with driver.session() as session:
                prot_count = session.run("MATCH (p:Protein) RETURN count(p) AS count").single()["count"]
                int_count = session.run("MATCH (i:Interaction) RETURN count(i) AS count").single()["count"]
                gene_count = session.run("MATCH (g:Gene) RETURN count(g) AS count").single()["count"]
                path_count = session.run("MATCH (pw:Pathway) RETURN count(pw) AS count").single()["count"]
                disease_count = session.run("MATCH (d:Disease) RETURN count(d) AS count").single()["count"]
                drug_count = session.run("MATCH (dr:Drug) RETURN count(dr) AS count").single()["count"]
                
                return {
                    "proteins": prot_count,
                    "genes": gene_count,
                    "interactions": int_count,
                    "pathways": path_count,
                    "diseases": disease_count,
                    "drugs": drug_count,
                    "density": float(int_count / (prot_count * (prot_count - 1))) if prot_count > 1 else 0.0
                }
        except Exception as e:
            logger.error(f"Neo4j stats query failed: {e}")
            return {"status": "degraded"}

    def run_llm_translation(self, natural_language_query: str) -> str:
        """Placeholder translating natural language query into Cypher format."""
        logger.info(f"[LLM TRANSLATOR] Query received: {natural_language_query}")
        # Returns simple template Cypher query
        return "MATCH (p:Protein {id: 'P01308'})-[:PARTICIPATES_IN]->(i:Interaction) RETURN p, i LIMIT 10;"

graph_service = GraphService()
