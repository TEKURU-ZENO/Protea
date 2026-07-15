import torch
import torch.optim as optim
from typing import Dict, Any
from ai.interaction_prediction.models.graphsage.model import GraphSageModel
from ai.interaction_prediction.models.graphsage.losses import MultiTaskLoss
from ai.interaction_prediction.models.graphsage.config import GraphSageConfig
from services.api.core.logging import logger

class GraphSageTrainer:
    def __init__(self, model: GraphSageModel, config: GraphSageConfig):
        self.model = model
        self.config = config
        self.loss_fn = MultiTaskLoss(config)
        self.optimizer = optim.Adam(model.parameters(), lr=config.lr)

    def train_epoch(self, x: torch.Tensor, edge_index: torch.Tensor, labels: torch.Tensor) -> float:
        self.model.train()
        self.optimizer.zero_grad()
        
        # Node representations forward pass
        z = self.model(x, edge_index)
        
        # Link prediction logits pass (evaluate first edge_index half as positive, others as negative placeholders)
        z_src = z[edge_index[0]]
        z_dst = z[edge_index[1]]
        pred_link_logits = self.model.predict_link(z_src, z_dst).squeeze(-1)
        
        loss = self.loss_fn(pred_link_logits, labels)
        loss.backward()
        self.optimizer.step()
        
        return float(loss.item())

    def fit(self, x: torch.Tensor, edge_index: torch.Tensor, labels: torch.Tensor) -> Dict[str, Any]:
        logger.info("[IPE TRAINER] Starting GNN SAGE optimization training loop...")
        losses = []
        for epoch in range(1, self.config.epochs + 1):
            loss = self.train_epoch(x, edge_index, labels)
            losses.append(loss)
            if epoch % 5 == 0:
                logger.info(f"Epoch {epoch}/{self.config.epochs} - Batch Loss: {loss:.4f}")
        return {"losses": losses, "final_loss": losses[-1]}
