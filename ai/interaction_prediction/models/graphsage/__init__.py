import torch
from typing import Dict, Any
from ai.interaction_prediction.models.base import BasePredictionModel
from ai.interaction_prediction.models.graphsage.model import GraphSageModel
from ai.interaction_prediction.models.graphsage.trainer import GraphSageTrainer
from ai.interaction_prediction.models.graphsage.inference import GraphSageInference
from ai.interaction_prediction.models.graphsage.config import GraphSageConfig
from ai.interaction_prediction.models.graphsage.metrics import GnnMetrics
from ai.interaction_prediction.registry import ipe_registry

class GraphSagePredictor(BasePredictionModel):
    def __init__(self):
        self.config = GraphSageConfig()
        self.model = GraphSageModel(
            in_channels=self.config.in_channels,
            hidden_channels=self.config.hidden_channels,
            out_channels=self.config.out_channels
        )
        self.trainer = GraphSageTrainer(self.model, self.config)
        self.inference = GraphSageInference(self.model)

    def train(self, data: Any, epochs: int = 15, lr: float = 0.005) -> Dict[str, Any]:
        """Trains GraphSAGE GNN on input features and graph structure."""
        self.config.epochs = epochs
        self.config.lr = lr
        
        # Unpack mock or actual pyg data tensors
        x = data.get("x", torch.randn(10, self.config.in_channels))
        edge_index = data.get("edge_index", torch.tensor([[0, 1, 2, 3, 4], [1, 2, 3, 4, 0]], dtype=torch.long))
        labels = data.get("labels", torch.tensor([1, 1, 1, 1, 1], dtype=torch.float))
        
        return self.trainer.fit(x, edge_index, labels)

    def predict(self, data: Any) -> Dict[str, Any]:
        """Runs joint link, edge-type, and functional annotations prediction."""
        z = self.model(data["x"], data["edge_index"])
        
        # Extract indices
        src_idx = data.get("src_idx", 0)
        dst_idx = data.get("dst_idx", 1)
        
        z_src = z[src_idx].unsqueeze(0)
        z_dst = z[dst_idx].unsqueeze(0)
        
        link_prob = self.inference.predict_link_probability(z_src, z_dst)
        edge_classes = self.inference.predict_edge_classification(z_src, z_dst)
        node_ann = self.inference.predict_node_annotations(z_src)
        
        return {
            "link_probability": link_prob,
            "interaction_type_probabilities": edge_classes,
            "node_functional_annotations": node_ann,
            "latent_node_embeddings": z.tolist()
        }

    def evaluate(self, data: Any) -> Dict[str, float]:
        """Evaluates classification accuracy metrics."""
        z = self.model(data["x"], data["edge_index"])
        
        # Link predictions probabilities list
        edge_index = data["edge_index"]
        z_src = z[edge_index[0]]
        z_dst = z[edge_index[1]]
        
        probs = []
        for i in range(len(edge_index[0])):
            prob = self.inference.predict_link_probability(z_src[i].unsqueeze(0), z_dst[i].unsqueeze(0))
            probs.append(prob)
            
        import numpy as np
        y_true = data["labels"].cpu().numpy()
        y_pred = np.array(probs)
        
        return GnnMetrics.calculate(y_true, y_pred)

    def save(self, path: str):
        torch.save(self.model.state_dict(), path)

    def load(self, path: str):
        self.model.load_state_dict(torch.load(path, map_location="cpu"))

    def export(self, path: str):
        # ONNX export stub
        torch.save(self.model, path)

# Auto-register model in registry
ipe_registry.register("graphsage", GraphSagePredictor)
