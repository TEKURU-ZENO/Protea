# ai/interaction_prediction/models/seal/__init__.py
from ai.interaction_prediction.models.base import BasePredictionModel
from ai.interaction_prediction.registry import ipe_registry
from typing import Dict, Any

class SealPredictor(BasePredictionModel):
    """SEAL model stub. Marked as uninstantiated mock until trained on full STRING dataset."""

    def train(self, data: Any, epochs: int = 10, lr: float = 0.01) -> Dict[str, Any]:
        return {"status": "uninstantiated_mock", "is_mock": True}

    def predict(self, data: Any) -> Dict[str, Any]:
        return {
            "link_probability": 0.50,
            "interaction_type_probabilities": {"unknown": 1.0},
            "node_functional_annotations": {},
            "is_mock": True,
            "execution_mode": "mock_uninstantiated",
            "warning": "MOCK STUB: SEAL is uninstantiated and not trained on STRING PPI dataset. Use 'graphsage' for genuine trained inference."
        }

    def evaluate(self, data: Any) -> Dict[str, float]:
        return {
            "is_mock": True,
            "status": "uninstantiated_no_genuine_metrics"
        }

    def save(self, path: str):
        pass

    def load(self, path: str):
        pass

    def export(self, path: str):
        pass

ipe_registry.register("seal", SealPredictor)
