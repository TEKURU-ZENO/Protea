import torch
from typing import Dict, Any
from ai.interaction_prediction.models.graphsage.model import GraphSageModel

class GraphSageInference:
    def __init__(self, model: GraphSageModel):
        self.model = model

    @torch.no_grad()
    def predict_link_probability(self, z_src: torch.Tensor, z_dst: torch.Tensor) -> float:
        """Returns normalized probability of link existence."""
        self.model.eval()
        logits = self.model.predict_link(z_src, z_dst)
        prob = torch.sigmoid(logits).item()
        return float(prob)

    @torch.no_grad()
    def predict_node_annotations(self, z: torch.Tensor) -> Dict[str, float]:
        """Returns functional node classification labels probabilities mapping."""
        self.model.eval()
        logits = self.model.predict_node(z).squeeze(0)
        probs = torch.sigmoid(logits).tolist()
        
        # Simple multi-label annotation categories mapping
        annotations = [
            "GO:0005515 (protein binding)",
            "GO:0008270 (zinc ion binding)",
            "GO:0005634 (nucleus)",
            "GO:0005829 (cytosol)",
            "GO:0005737 (cytoplasm)",
            "GO:0006355 (regulation of transcription)",
            "GO:0006357 (transcription)",
            "GO:0005654 (nucleoplasm)",
            "GO:0005524 (ATP binding)",
            "GO:0004674 (protein serine/threonine kinase activity)"
        ]
        return {annotations[i]: float(probs[i]) for i in range(len(annotations))}

    @torch.no_grad()
    def predict_edge_classification(self, z_src: torch.Tensor, z_dst: torch.Tensor) -> Dict[str, float]:
        """Returns multi-class probabilities for relationship interaction types."""
        self.model.eval()
        logits = self.model.predict_edge(z_src, z_dst).squeeze(0)
        probs = torch.softmax(logits, dim=-1).tolist()
        
        interaction_types = ["binds", "activates", "inhibits", "phosphorylates", "complex formation", "unknown"]
        return {interaction_types[i]: float(probs[i]) for i in range(len(interaction_types))}
