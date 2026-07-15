import torch
import torch.nn as nn
from ai.interaction_prediction.models.graphsage.config import GraphSageConfig

class MultiTaskLoss(nn.Module):
    def __init__(self, config: GraphSageConfig):
        super().__init__()
        self.config = config
        self.link_loss_fn = nn.BCEWithLogitsLoss()
        self.node_loss_fn = nn.BCEWithLogitsLoss() # GO multi-label
        self.edge_loss_fn = nn.CrossEntropyLoss()  # multi-class edge labels

    def forward(
        self,
        pred_link_logits: torch.Tensor,
        true_links: torch.Tensor,
        pred_node_logits: Optional[torch.Tensor] = None,
        true_nodes: Optional[torch.Tensor] = None,
        pred_edge_logits: Optional[torch.Tensor] = None,
        true_edges: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        loss = self.config.link_loss_weight * self.link_loss_fn(pred_link_logits, true_links.float())
        
        if pred_node_logits is not None and true_nodes is not None:
            loss += self.config.node_loss_weight * self.node_loss_fn(pred_node_logits, true_nodes.float())
            
        if pred_edge_logits is not None and true_edges is not None:
            loss += self.config.edge_loss_weight * self.edge_loss_fn(pred_edge_logits, true_edges.long())
            
        return loss
