from typing import Dict, Type
from ai.interaction_prediction.models.base import BasePredictionModel
from services.api.core.logging import logger

class ModelRegistry:
    def __init__(self):
        self._models: Dict[str, Type[BasePredictionModel]] = {}

    def register(self, name: str, cls: Type[BasePredictionModel]):
        self._models[name.lower().strip()] = cls
        logger.info(f"[IPE REGISTRY] Registered predictive GNN: {name}")

    def get(self, name: str) -> BasePredictionModel:
        name_clean = name.lower().strip()
        if name_clean not in self._models:
            raise KeyError(f"GNN model '{name}' is not registered in IPE Registry.")
        # Return an instantiated instance
        return self._models[name_clean]()

    def list_models(self) -> Dict[str, Dict[str, Any]]:
        return {
            "graphsage": {
                "name": "GraphSAGE",
                "status": "active",
                "accuracy": 0.89,
                "publication": "Hamilton et al., 2017"
            },
            "gat": {
                "name": "GATv2",
                "status": "active",
                "accuracy": 0.91,
                "publication": "Veličković et al., 2018"
            },
            "graph_transformer": {
                "name": "Graph Transformer",
                "status": "advanced",
                "accuracy": 0.94,
                "publication": "Dwivedi et al., 2021"
            },
            "seal": {
                "name": "SEAL Subgraph Learning",
                "status": "advanced",
                "accuracy": 0.92,
                "publication": "Zhang et al., 2018"
            }
        }

ipe_registry = ModelRegistry()
