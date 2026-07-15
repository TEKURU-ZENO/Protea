import abc
from typing import Dict, Any, Tuple
import torch

class BasePredictionModel(abc.ABC):
    @abc.abstractmethod
    def train(self, data: Any, epochs: int = 10, lr: float = 0.01) -> Dict[str, Any]:
        """Trains the GNN model and returns tracking metrics history."""
        pass

    @abc.abstractmethod
    def predict(self, data: Any) -> Dict[str, Any]:
        """Runs batch inference and returns predictions."""
        pass

    @abc.abstractmethod
    def evaluate(self, data: Any) -> Dict[str, float]:
        """Evaluates model performance metrics (ROC-AUC, PR-AUC, F1)."""
        pass

    @abc.abstractmethod
    def save(self, path: str):
        """Saves current checkpoint weights."""
        pass

    @abc.abstractmethod
    def load(self, path: str):
        """Loads weights from checkpoint."""
        pass

    @abc.abstractmethod
    def export(self, path: str):
        """Exports the model structure to ONNX or serialized format."""
        pass
