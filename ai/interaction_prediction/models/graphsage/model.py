import torch
import torch.nn as nn
from typing import Dict, Any, Optional

try:
    from torch_geometric.nn import SAGEConv
    HAS_PYG = True
except ImportError:
    HAS_PYG = False

class GraphSageModel(nn.Module if HAS_PYG or torch.__version__ else object):
    def __init__(self, in_channels: int = 1280, hidden_channels: int = 256, out_channels: int = 128):
        super().__init__()
        self.in_channels = in_channels
        self.hidden_channels = hidden_channels
        self.out_channels = out_channels

        if HAS_PYG:
            self.conv1 = SAGEConv(in_channels, hidden_channels)
            self.conv2 = SAGEConv(hidden_channels, out_channels)
        else:
            # Fallback dense layer representation
            self.conv1 = nn.Linear(in_channels, hidden_channels)
            self.conv2 = nn.Linear(hidden_channels, out_channels)

        # Multi-task heads: Link prediction (binary), Edge classification (interaction type classes)
        # and Node classification (functional GO classification)
        self.link_predictor = nn.Sequential(
            nn.Linear(out_channels * 2, 64),
            nn.ReLU(),
            nn.Linear(64, 1) # Sigmoid applied later (logits output)
        )
        
        self.node_classifier = nn.Sequential(
            nn.Linear(out_channels, 64),
            nn.ReLU(),
            nn.Linear(64, 10) # 10 GO terms multi-label logits
        )

        self.edge_classifier = nn.Sequential(
            nn.Linear(out_channels * 2, 64),
            nn.ReLU(),
            nn.Linear(64, 6) # 6 interaction types (binds, activates, inhibits, phosphorylates, complex, unknown)
        )

    def forward(self, x: torch.Tensor, edge_index: torch.Tensor) -> torch.Tensor:
        """Forward pass generating node representations."""
        if HAS_PYG:
            x = self.conv1(x, edge_index).relu()
            x = self.conv2(x, edge_index)
        else:
            x = self.conv1(x).relu()
            x = self.conv2(x)
        return x

    def predict_link(self, z_src: torch.Tensor, z_dst: torch.Tensor) -> torch.Tensor:
        """Predicts binary interaction presence."""
        edge_feats = torch.cat([z_src, z_dst], dim=-1)
        return self.link_predictor(edge_feats)

    def predict_node(self, z: torch.Tensor) -> torch.Tensor:
        """Predicts node functional labels."""
        return self.node_classifier(z)

    def predict_edge(self, z_src: torch.Tensor, z_dst: torch.Tensor) -> torch.Tensor:
        """Predicts multi-class edge interaction types."""
        edge_feats = torch.cat([z_src, z_dst], dim=-1)
        return self.edge_classifier(edge_feats)
