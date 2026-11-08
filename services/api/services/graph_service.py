from typing import List, Dict, Any, Optional
from services.api.core.neo4j import neo4j_client
from services.api.core.logging import logger

class GraphService:
    def __init__(self):
        self._driver = neo4j_client

    def get_neighbors(self, protein_id: str) -> List[Dict[str, Any]]:
        """Queries Neo4j or local STRING graph for immediate interaction neighbors."""
        driver = self._driver.driver
        if not driver:
            import os, torch
            if os.path.exists("data/string/processed_string_graph.pt"):
                try:
                    data = torch.load("data/string/processed_string_graph.pt", map_location="cpu")
                    proteins = data.get("proteins", [])
                    p_upper = protein_id.upper()
                    if p_upper in proteins:
                        idx = proteins.index(p_upper)
                        pos_edges = data.get("pos_edges", [])
                        neighbors = []
                        for u, v in pos_edges:
                            if u == idx:
                                neighbors.append({
                                    "protein_id": proteins[v],
                                    "interaction_id": f"string_{idx}_{v}",
                                    "confidence": 0.85,
                                    "databases": ["STRING v12"]
                                })
                            elif v == idx:
                                neighbors.append({
                                    "protein_id": proteins[u],
                                    "interaction_id": f"string_{v}_{idx}",
                                    "confidence": 0.85,
                                    "databases": ["STRING v12"]
                                })
                        return neighbors
                except Exception as e:
                    logger.warning(f"Error reading local STRING graph for neighbors: {e}")
            return []

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
            import os, torch
            from collections import defaultdict, deque
            if os.path.exists("data/string/processed_string_graph.pt"):
                try:
                    data = torch.load("data/string/processed_string_graph.pt", map_location="cpu")
                    proteins = data.get("proteins", [])
                    p1_up, p2_up = p1.upper(), p2.upper()
                    if p1_up in proteins and p2_up in proteins:
                        src_idx, dst_idx = proteins.index(p1_up), proteins.index(p2_up)
                        adj = defaultdict(list)
                        for u, v in data.get("pos_edges", []):
                            adj[u].append(v)
                            adj[v].append(u)
                        queue = deque([[src_idx]])
                        visited = {src_idx}
                        while queue:
                            path = queue.popleft()
                            node = path[-1]
                            if node == dst_idx:
                                return [{"id": proteins[n], "label": "Protein", "properties": {"symbol": proteins[n]}} for n in path]
                            for nxt in adj[node]:
                                if nxt not in visited:
                                    visited.add(nxt)
                                    queue.append(path + [nxt])
                except Exception as e:
                    logger.warning(f"Error computing shortest path on local STRING graph: {e}")
            return []

        try:
            with driver.session() as session:
                query = """
                MATCH path = shortestPath((p1:Protein {id: $p1_id})-[:PARTICIPATES_IN|OBSERVED_IN|SUPPORTS*..10]-(p2:Protein {id: $p2_id}))
                RETURN path
                """
                results = session.run(query, p1_id=p1, p2_id=p2).single()
                if not results:
                    return []
                
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
            import os, torch
            if os.path.exists("data/string/processed_string_graph.pt"):
                try:
                    data = torch.load("data/string/processed_string_graph.pt", map_location="cpu")
                    num_proteins = len(data.get("proteins", []))
                    num_edges = len(data.get("pos_edges", []))
                    density = round(2.0 * num_edges / (num_proteins * (num_proteins - 1)), 4) if num_proteins > 1 else 0.0
                    return {
                        "proteins": num_proteins,
                        "interactions": num_edges,
                        "density": density,
                        "dataset": "STRING v12 Human Core PPI Graph",
                        "status": "active_local_graph"
                    }
                except Exception:
                    pass
            return {"proteins": 0, "interactions": 0, "status": "neo4j_offline"}

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
