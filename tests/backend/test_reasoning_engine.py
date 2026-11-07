"""
PROTEA BRE - Comprehensive Backend Test Suite
Validates question parsing, multi-hop mechanistic reconstruction, hypothesis generation,
evidence fusion, counterfactual simulation, constraint validation, and multi-agent orchestration.
"""

import sys
from pathlib import Path

# Resolve imports pathing
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

def test_question_parsing_and_entities():
    from ai.biological_reasoning.query.parser import BiologicalQuestionParser
    from ai.biological_reasoning.query.entity_resolution import BiologicalEntityResolver

    resolver = BiologicalEntityResolver()
    symbol, amb = resolver.resolve_protein("p53")
    assert symbol == "TP53"

    parser = BiologicalQuestionParser()
    q = parser.parse("A protein TP53 is downregulated in liver under disease condition. Which upstream regulators could explain this change?")
    assert q.target == "TP53"
    assert q.task == "upstream_regulator_analysis"
    assert q.context.get("tissue") == "liver"
    assert q.context.get("observation") == "downregulated"

def test_evidence_retrieval_and_fusion():
    from ai.biological_reasoning.retrieval.hybrid_retriever import HybridEvidenceRetriever
    from ai.biological_reasoning.evidence.fusion import EvidenceFusionEngine, ContradictionResolutionEngine
    from ai.biological_reasoning.schema import BiologicalEvidence, EvidenceStatus

    retriever = HybridEvidenceRetriever()
    evs = retriever.retrieve_evidence_for_target("TP53")
    assert len(evs) > 0
    assert any(e.subject_id == "MDM2" and e.object_id == "TP53" for e in evs)

    fusion = EvidenceFusionEngine()
    fused = fusion.fuse_evidence(evs)
    assert fused["evidence_strength"] >= 0.80
    assert fused["biological_certainty"] in ["ESTABLISHED", "PROBABLE"]
    assert "unique_publications" in fused

    # Test contradiction detection
    conflicting_evs = [
        BiologicalEvidence(subject_id="PROT_A", predicate="activates", object_id="PROT_B", source="IntAct", publication_id="PubMed:1"),
        BiologicalEvidence(subject_id="PROT_A", predicate="inhibits", object_id="PROT_B", source="BioGRID", publication_id="PubMed:2")
    ]
    contra_engine = ContradictionResolutionEngine()
    contradictions = contra_engine.detect_contradictions(conflicting_evs)
    assert len(contradictions) == 1
    assert contradictions[0]["severity"] == "HIGH"

def test_mechanistic_and_graph_reasoning():
    from ai.biological_reasoning.mechanistic.mechanism_reconstructor import MechanisticReasoningEngine
    from ai.biological_reasoning.graph_reasoning.path_reasoner import BiologicalGraphReasoningEngine

    mechanistic = MechanisticReasoningEngine()
    regulators = mechanistic.identify_upstream_regulators("TP53", observed_change="downregulated")
    assert len(regulators) > 0
    assert any(r["regulator"] == "MDM2" for r in regulators)

    mech = mechanistic.reconstruct_mechanism(["MDM2", "TP53", "BAX", "CASP3"])
    assert mech.net_effect in ["Activation", "Inhibition"]
    assert len(mech.steps) == 3
    assert mech.cumulative_confidence > 0.70

    # Graph reasoning
    graph_engine = BiologicalGraphReasoningEngine()
    paths = graph_engine.find_mechanistic_paths("ATM", "CASP3", max_hops=4)
    assert len(paths) > 0
    assert paths[0]["path"][0] == "ATM"
    assert paths[0]["path"][-1] == "CASP3"

def test_hypothesis_generation_and_ranking():
    from ai.biological_reasoning.query.parser import BiologicalQuestionParser
    from ai.biological_reasoning.hypothesis.generator import HypothesisGenerationEngine, HypothesisRankingEngine

    parser = BiologicalQuestionParser()
    q = parser.parse("Why is TP53 downregulated in hepatic carcinoma?")

    hyp_gen = HypothesisGenerationEngine()
    hyps = hyp_gen.generate_competing_hypotheses(q, max_hypotheses=3)
    assert len(hyps) >= 2
    assert hyps[0].statement != hyps[1].statement
    assert len(hyps[0].potential_validation_experiments) > 0

    ranker = HypothesisRankingEngine()
    ranked = ranker.rank_hypotheses(hyps)
    assert len(ranked) == len(hyps)
    assert ranked[0]["composite_score"] >= ranked[1]["composite_score"]

def test_counterfactual_perturbation():
    from ai.biological_reasoning.counterfactual.scenario_comparison import CounterfactualReasoningEngine

    cf_engine = CounterfactualReasoningEngine()
    scenario = cf_engine.simulate_perturbation("TP53", perturbation_type="knockout", tissue="liver")
    assert scenario.target_protein == "TP53"
    assert scenario.perturbed_nodes.get("TP53") == -1.0
    # Downstream BAX should be suppressed
    assert "BAX" in scenario.perturbed_nodes
    assert scenario.perturbed_nodes["BAX"] < 0.0
    assert len(scenario.affected_pathways) > 0
    assert len(scenario.model_qualifications) > 0

def test_uncertainty_and_validation():
    from ai.biological_reasoning.uncertainty.calibration import (
        calculate_brier_score,
        calculate_expected_calibration_error,
        UncertaintyEstimator
    )
    from ai.biological_reasoning.validation.biological_constraints import BiologicalConstraintValidator
    from ai.biological_reasoning.mechanistic.mechanism_reconstructor import MechanisticReasoningEngine

    # Brier & ECE
    probs = [0.9, 0.8, 0.2, 0.1]
    outcomes = [1, 1, 0, 0]
    brier = calculate_brier_score(probs, outcomes)
    assert brier < 0.05
    ece = calculate_expected_calibration_error(probs, outcomes, n_bins=5)
    assert ece >= 0.0

    # Uncertainty estimator
    unc_est = UncertaintyEstimator()
    eval_res = unc_est.evaluate_uncertainty(
        target="TP53",
        evidence_count=4,
        compartment_known=True,
        tissue_specified=True,
        has_contradictions=False
    )
    assert eval_res["calibrated_confidence"] >= 0.85
    assert len(eval_res["context_warnings"]) == 0

    # Biological constraint validation
    mechanistic = MechanisticReasoningEngine()
    valid_mech = mechanistic.reconstruct_mechanism(["TP53", "BAX", "CASP3"])
    validator = BiologicalConstraintValidator()
    val_res = validator.validate_mechanism(valid_mech)
    assert val_res["is_biologically_valid"] is True
    assert val_res["verdict"] == "PASSED"

def test_multi_agent_orchestration_and_api():
    from ai.biological_reasoning.agents.orchestrator import orchestrator
    from ai.biological_reasoning.query.parser import BiologicalQuestionParser
    from services.api.services.biological_reasoning_service import biological_reasoning_service

    parser = BiologicalQuestionParser()
    q = parser.parse("TP53 is downregulated in liver tissue. What upstream regulators explain this?")

    report = orchestrator.run_reasoning_pipeline(q)
    assert report.report_id is not None
    assert len(report.reasoning_trace) >= 5 # All 6 agents executed
    assert report.primary_mechanism is not None
    assert len(report.competing_hypotheses) >= 2
    assert "MDM2" in report.executive_summary

    # Test service layer
    svc_models = biological_reasoning_service.get_models()
    assert "orchestrator" in svc_models
    assert len(svc_models["agents"]) == 6

if __name__ == "__main__":
    print("Executing Phase 6 BRE backend test suite...")
    test_question_parsing_and_entities()
    test_evidence_retrieval_and_fusion()
    test_mechanistic_and_graph_reasoning()
    test_hypothesis_generation_and_ranking()
    test_counterfactual_perturbation()
    test_uncertainty_and_validation()
    test_multi_agent_orchestration_and_api()
    print("All Phase 6 BRE backend tests passed successfully!")
