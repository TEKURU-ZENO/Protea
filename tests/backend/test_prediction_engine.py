import sys
import torch
from pathlib import Path

# Resolve imports pathing
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

def test_graphsage_forward():
    from ai.interaction_prediction.models.graphsage.model import GraphSageModel
    
    # 5 nodes, 1280 dimension input features
    x = torch.randn(5, 1280)
    edge_index = torch.tensor([[0, 1, 2, 3], [1, 2, 3, 0]], dtype=torch.long)
    
    model = GraphSageModel(in_channels=1280, hidden_channels=64, out_channels=32)
    z = model(x, edge_index)
    
    # Verify node representations size
    assert z.shape == (5, 32)
    
    # Test multi-task heads: Link prediction (should yield raw logits shape)
    link_logits = model.predict_link(z[0].unsqueeze(0), z[1].unsqueeze(0))
    assert link_logits.shape == (1, 1)
    
    # Test Node classification
    node_logits = model.predict_node(z[0].unsqueeze(0))
    assert node_logits.shape == (1, 10)
    
    # Test Edge classification
    edge_logits = model.predict_edge(z[0].unsqueeze(0), z[1].unsqueeze(0))
    assert edge_logits.shape == (1, 6)

def test_feature_fusion():
    from ai.interaction_prediction.fusion.registry import fusion_registry
    
    seq_emb = torch.randn(5, 1280)
    graph_emb = torch.randn(5, 128)
    
    # Test concatenation strategy
    concat = fusion_registry.get("concatenation")
    fused = concat.fuse(seq_emb, graph_emb)
    assert fused.shape == (5, 1408)
    
    # Test weighted strategy
    weighted = fusion_registry.get("weighted")
    fused_w = weighted.fuse(seq_emb, graph_emb)
    assert fused_w.shape == (5, 128)

def test_calibration_and_explainability():
    from ai.interaction_prediction.calibration.scaling import calibrator
    from ai.interaction_prediction.explainability.attention import gnn_explainer
    
    # Check scaling conversion
    scaled = calibrator.calibrate(0.88)
    assert scaled > 0.0 and scaled < 1.0
    
    # Check explainer output path
    explanation = gnn_explainer.explain_link("BRCA1", "BARD1")
    assert "reasoning_path" in explanation
    assert len(explanation["attention_weights"]) > 0

def test_dataset_builder():
    from ai.interaction_prediction.datasets.graph_builder import graph_dataset_builder
    
    data = graph_dataset_builder.build_dataset_from_neo4j()
    assert "x" in data
    assert "edge_index" in data
    assert "labels" in data
    # ESM-2 150M has 640 dims, ESM-2 650M has 1280 dims
    assert data["x"].shape[1] in (640, 1280)

def test_evaluate_and_uninstantiated_stubs():
    import pytest
    from ai.interaction_prediction.models.graphsage import GraphSagePredictor
    from ai.interaction_prediction.models.gat import Gatv2Predictor
    from ai.interaction_prediction.models.seal import SealPredictor
    from ai.interaction_prediction.models.graph_transformer import GraphTransformerPredictor

    # Test GraphSagePredictor evaluate returns genuine metrics or raises
    sage = GraphSagePredictor()
    metrics = sage.evaluate()
    assert "test_roc_auc" in metrics
    assert metrics["test_roc_auc"] > 0.70

    # Test unknown protein raises ValueError
    with pytest.raises(ValueError, match="not found in trained STRING PPI interactome"):
        sage.predict_link("NONEXISTENT_PROT_ABC", "NONEXISTENT_PROT_XYZ")

    # Test uninstantiated stubs raise NotImplementedError on evaluate and predict
    gat = Gatv2Predictor()
    with pytest.raises(NotImplementedError):
        gat.evaluate()
    with pytest.raises(NotImplementedError):
        gat.predict({})

    seal = SealPredictor()
    with pytest.raises(NotImplementedError):
        seal.evaluate()

    gt = GraphTransformerPredictor()
    with pytest.raises(NotImplementedError):
        gt.evaluate()

if __name__ == "__main__":
    print("Running Phase 4 IPE backend tests...")
    test_graphsage_forward()
    test_feature_fusion()
    test_calibration_and_explainability()
    test_dataset_builder()
    test_evaluate_and_uninstantiated_stubs()
    print("All Phase 4 IPE tests passed successfully!")
