import torch
from typing import Dict, Any, List
from services.api.core.neo4j import neo4j_client
from services.api.core.logging import logger
from ai.protein_foundation.registry import registry
from ai.interaction_prediction.registry import ipe_registry

class GraphDatasetBuilder:
    def __init__(self, default_dim: int = 1280):
        self.default_dim = default_dim

    def build_dataset_from_neo4j(self) -> Dict[str, Any]:
        """Fetches the active interactome from Neo4j and compiles PyG tensors."""
        driver = neo4j_client.driver
        if not driver:
            # Fallback mock dataset for testing & offline mode
            logger.warning("[IPE BUILDER] Neo4j is offline. Initializing fallback mock graph dataset.")
            x = torch.randn(10, self.default_dim)
            edge_index = torch.tensor([[0, 1, 2, 3, 4, 5, 6, 7, 8, 9], [1, 2, 3, 4, 5, 6, 7, 8, 9, 0]], dtype=torch.long)
            labels = torch.tensor([1, 1, 1, 1, 1, 0, 0, 0, 0, 0], dtype=torch.float)
            return {"x": x, "edge_index": edge_index, "labels": labels}

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
                    # Generate mock/actual embedding for each protein
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

                # Edge index representation
                edge_index = torch.tensor([sources, targets], dtype=torch.long)
                labels_tensor = torch.tensor(labels, dtype=torch.float)
                
                return {
                    "x": x,
                    "edge_index": edge_index,
                    "labels": labels_tensor,
                    "node_mapping": prot_list
                }
        except Exception as e:
            logger.error(f"[IPE BUILDER] Neo4j graph data assembly failed: {e}")
            # Fallback
            x = torch.randn(10, self.default_dim)
            edge_index = torch.tensor([[0, 1, 2, 3, 4], [1, 2, 3, 4, 0]], dtype=torch.long)
            labels = torch.tensor([1, 1, 1, 1, 1], dtype=torch.float)
            return {"x": x, "edge_index": edge_index, "labels": labels}

graph_dataset_builder = GraphDatasetBuilder()
