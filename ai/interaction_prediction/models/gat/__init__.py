# ai/interaction_prediction/models/gat/__init__.py
from ai.interaction_prediction.models.base import BasePredictionModel
from ai.interaction_prediction.registry import ipe_registry
from typing import Dict, Any

class Gatv2Predictor(BasePredictionModel):
    """GATv2 model architecture stub. Uninstantiated pending training on interactome graph."""

    def train(self, data: Any, epochs: int = 10, lr: float = 0.01) -> Dict[str, Any]:
        raise NotImplementedError("GATv2 model architecture is not yet implemented or trained.")

    def predict(self, data: Any) -> Dict[str, Any]:
        raise NotImplementedError("GATv2 is not instantiated. Use 'graphsage' for genuine trained inference.")

    def evaluate(self, data: Any = None) -> Dict[str, float]:
        raise NotImplementedError("GATv2 is not instantiated or trained; cannot evaluate.")

    def save(self, path: str):
        pass

    def load(self, path: str):
        pass

    def export(self, path: str):
        pass

ipe_registry.register("gat", Gatv2Predictor)
ipe_registry.register("gatv2", Gatv2Predictor)
