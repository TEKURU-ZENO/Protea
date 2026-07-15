class GraphSageConfig:
    def __init__(self):
        self.in_channels = 1280  # Default feature size (ESM-2)
        self.hidden_channels = 256
        self.out_channels = 128
        self.lr = 0.005
        self.epochs = 15
        self.batch_size = 64
        
        # Loss balance weights for multi-task learning
        self.link_loss_weight = 1.0
        self.node_loss_weight = 0.5
        self.edge_loss_weight = 0.8
