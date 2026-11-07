"""
Unit and integration tests for PROTEA Phase 9: AI Scientist (Autonomous Biological Discovery Engine).
"""

import pytest
from ai.ai_scientist.schema import ResearchState, ClaimStatus, GapType
from ai.ai_scientist.question_understanding.parser import QuestionParser
from ai.ai_scientist.question_understanding.entity_resolver import BiologicalEntityResolver
from ai.ai_scientist.question_understanding.feasibility import FeasibilityChecker
from ai.ai_scientist.literature.search import LiteratureSearchCoordinator
from ai.ai_scientist.literature.deduplication import LiteratureDeduplicator
from ai.ai_scientist.literature.citation_graph import CitationGraphBuilder
from ai.ai_scientist.knowledge_synthesis.claim_extractor import ScientificClaimExtractor
from ai.ai_scientist.knowledge_synthesis.evidence_linker import EvidenceLinker
from ai.ai_scientist.knowledge_synthesis.contradiction_resolver import ContradictionResolver
from ai.ai_scientist.knowledge_synthesis.knowledge_builder import EvidenceKnowledgeGraphBuilder
from ai.ai_scientist.research_gaps.gap_detector import GapDetector
from ai.ai_scientist.research_gaps.novelty_auditor import NoveltyAuditor
from ai.ai_scientist.hypothesis.generator import HypothesisGenerator
from ai.ai_scientist.hypothesis.hypothesis_ranker import HypothesisRanker
from ai.ai_scientist.hypothesis.falsification import FalsificationEvaluator
from ai.ai_scientist.experiment_design.planner import ExperimentPlanner
from ai.ai_scientist.experiment_design.protocol_validator import ProtocolValidator
from ai.ai_scientist.execution.workflow_executor import WorkflowExecutor
from ai.ai_scientist.analysis.statistical_analysis import StatisticalAnalyzer
from ai.ai_scientist.analysis.effect_sizes import EffectSizeCalculator
from ai.ai_scientist.analysis.robustness import RobustnessAnalyzer
from ai.ai_scientist.criticism.adversarial_review import AdversarialReviewer
from ai.ai_scientist.criticism.leakage_detection import LeakageDetector
from ai.ai_scientist.reproducibility.experiment_manifest import ExperimentManifestBuilder
from ai.ai_scientist.reproducibility.provenance import ScientificProvenanceTracker
from ai.ai_scientist.reproducibility.workflow_replay import WorkflowReplayEngine
from ai.ai_scientist.reproducibility.artifact_versioning import ReproducibilityPackageBuilder
from ai.ai_scientist.writing.manuscript_generator import ScientificManuscriptGenerator
from ai.ai_scientist.writing.citation_validator import CitationValidator
from ai.ai_scientist.memory.finding_store import FindingStore
from ai.ai_scientist.agents.orchestrator import PrincipalResearchOrchestrator
from ai.ai_scientist.evaluation.benchmarks import ScientificDiscoveryBenchmarkSuite


def test_question_understanding():
    parser = QuestionParser()
    resolver = BiologicalEntityResolver()
    feasibility = FeasibilityChecker()

    res = parser.parse("Does EGFR phosphorylation directly regulate STAT3 nuclear translocation in NSCLC?")
    assert res["domain"] in ["oncology", "signaling", "molecular_biology"]
    assert "EGFR" in res["extracted_entities"]
    assert "STAT3" in res["extracted_entities"]

    entities = resolver.resolve_entities(res["extracted_entities"])
    assert len(entities) >= 2
    assert any(e["canonical_id"] == "P00533" for e in entities)

    feas = feasibility.check_feasibility(res["raw_question"], entities)
    assert feas["is_feasible"] is True
    assert feas["feasibility_score"] > 0.5


def test_literature_and_knowledge_synthesis():
    search = LiteratureSearchCoordinator()
    dedup = LiteratureDeduplicator()
    extractor = ScientificClaimExtractor()
    kg_builder = EvidenceKnowledgeGraphBuilder()

    pubs = search.search(query="EGFR STAT3 lung cancer", max_results=10)
    assert len(pubs) > 0

    dedup_res = dedup.deduplicate(pubs)
    assert dedup_res["unique_count"] > 0
    # Strict boundary: peer-reviewed vs preprints must be separated
    assert "peer_reviewed_count" in dedup_res
    assert "preprint_count" in dedup_res

    claims = extractor.extract_claims(dedup_res["unique_records"])
    assert len(claims) > 0
    assert hasattr(claims[0], "statement")
    assert hasattr(claims[0], "evidence_polarity")

    graph = kg_builder.build_graph(claims)
    assert "nodes" in graph
    assert "edges" in graph


def test_research_gaps_and_novelty():
    gap_detector = GapDetector()
    novelty_auditor = NoveltyAuditor()

    gaps = gap_detector.detect_gaps(claims=[], entities=["EGFR", "STAT3"])
    assert len(gaps) > 0
    assert any(g.gap_type == GapType.UNTESTED_INTERACTION for g in gaps)

    audit = novelty_auditor.audit_novelty(
        proposed_discovery="Novel EGFR phosphorylation of STAT3 Tyr705",
        retrieved_publications=[{"title": "EGFR phosphorylates STAT3 Tyr705", "doi": "10.1038/123", "is_preprint": False}],
    )
    assert "novelty_score" in audit
    assert "is_genuinely_novel" in audit


def test_hypothesis_generation_and_falsification():
    generator = HypothesisGenerator()
    ranker = HypothesisRanker()
    falsification = FalsificationEvaluator()

    hyps = generator.generate_competing_hypotheses(
        gap_id="gap_01",
        gap_description="EGFR-STAT3 cross-talk under kinase inhibition",
        claims=[],
        entities=["EGFR", "STAT3"],
        prior_knowledge={},
    )
    assert len(hyps) >= 2
    assert all(len(h.falsification_criteria) > 0 for h in hyps)

    ranked = ranker.rank_hypotheses(hyps)
    assert ranked[0].composite_score >= ranked[-1].composite_score

    f_eval = falsification.evaluate_hypothesis(
        hypothesis=ranked[0],
        observed_outcomes={"p_value": 0.001, "direction_consistent": True, "effect_size": -1.8},
    )
    assert f_eval["is_falsified"] is False
    assert f_eval["status"] == "SURVIVED_FALSIFICATION"


def test_experiment_design_and_execution():
    planner = ExperimentPlanner()
    validator = ProtocolValidator()
    executor = WorkflowExecutor()

    plan = planner.plan_experiment(
        hypothesis={"hypothesis_id": "hyp_01", "statement": "EGFR regulates STAT3"},
        target_entities=["EGFR", "STAT3"],
    )
    assert plan.controls.positive_controls is not None
    assert plan.controls.negative_controls is not None
    assert plan.controls.vehicle is not None
    # Scientific guardrail: stochastic replicates are strictly labeled
    assert "stochastic numerical solver" in plan.controls.statistical_distinction_note.lower()

    val_res = validator.validate(plan)
    assert val_res["is_valid"] is True

    record = executor.execute_experiment(plan, user_approved=True)
    assert record.success is True
    assert len(record.replicate_outcomes) > 0


def test_statistical_analysis_and_robustness():
    stat_analyzer = StatisticalAnalyzer()
    effect_calc = EffectSizeCalculator()
    robustness = RobustnessAnalyzer()

    intervention = [0.22, 0.25, 0.21, 0.24, 0.23, 0.20, 0.26, 0.22]
    control = [1.02, 0.98, 1.05, 0.95, 1.00, 1.03, 0.99, 1.01]

    stat_report = stat_analyzer.evaluate_significance(
        experiment_id="exp_01",
        hypothesis_id="hyp_01",
        intervention_replicates=intervention,
        control_replicates=control,
    )
    assert stat_report.statistically_significant is True
    assert stat_report.p_value < 0.001
    assert stat_report.effect_size < -2.0

    fc = effect_calc.fold_change(0.23, 1.00)
    assert fc["log2_fold_change"] < -1.5

    rob = robustness.analyze_parameter_sensitivity(
        nominal_output=0.23,
        perturbed_evaluations=[
            {"parameter_name": "k_cat", "nominal_param_val": 1.0, "perturbed_param_val": 1.1, "perturbed_output": 0.24},
            {"parameter_name": "k_deg", "nominal_param_val": 0.1, "perturbed_param_val": 0.12, "perturbed_output": 0.22},
        ],
    )
    assert rob["robustness_score"] > 0.7


def test_adversarial_critic_and_leakage():
    critic = AdversarialReviewer()
    leakage = LeakageDetector()

    leak_audit = leakage.audit_leakage(
        predicted_pairs=[{"source": "EGFR", "target": "STAT3"}],
        training_database_edges={"EGFR:STAT3"},
        validation_engine_name="CSE",
        inference_engine_name="IPE",
    )
    assert leak_audit["passed_leakage_audit"] is False
    assert leak_audit["leaked_pairs_count"] == 1

    clean_audit = leakage.audit_leakage(
        predicted_pairs=[{"source": "EGFR", "target": "NOVEL_TARGET"}],
        training_database_edges={"EGFR:STAT3"},
        validation_engine_name="CSE",
        inference_engine_name="IPE",
    )
    assert clean_audit["passed_leakage_audit"] is True

    adv_report = critic.conduct_audit(
        hypothesis_id="hyp_01",
        hypothesis_statement="EGFR directly regulates STAT3",
        falsification_criteria=["Absence of downstream phosphorylation suppression (p > 0.05)"],
        experiment_design={"controls": {"vehicle": "DMSO", "orthogonal_controls": ["WesternBlot"]}},
        experimental_results={"p_value": 0.0001, "effect_size": -2.4, "statistically_significant": True},
        pathway_context={"has_parallel_pathways": False},
        training_database_edges=set(),
        predicted_pairs=[{"source": "EGFR", "target": "NOVEL_TARGET"}],
    )
    assert adv_report.passed_audit is True
    assert adv_report.recommendation in ["APPROVED_FOR_PUBLICATION", "REQUIRES_REVISION"]


def test_reproducibility_and_manuscript():
    manifest_builder = ExperimentManifestBuilder()
    replay = WorkflowReplayEngine()
    pkg_builder = ReproducibilityPackageBuilder()
    manuscript_gen = ScientificManuscriptGenerator()
    cit_validator = CitationValidator()

    manifest = manifest_builder.generate_manifest(
        experiment_id="exp_01",
        hypothesis_id="hyp_01",
        random_seeds=[42, 101],
        config={"sim_duration": 100},
        raw_outputs={"effect_size": -2.4},
    )
    assert "manifest_signature" in manifest
    assert "config_sha256" in manifest

    rep_eval = replay.verify_reproducibility([0.22, 0.25], [0.22, 0.25])
    assert rep_eval["reproducible"] is True

    pkg = pkg_builder.build_package(
        investigation_id="inv_01",
        experiment_id="exp_01",
        hypothesis_id="hyp_01",
        config={"sim_duration": 100},
        random_seeds=[42, 101],
        raw_outputs={"effect_size": -2.4},
        dataset_uris=["protea://kg"],
    )
    assert pkg.package_id.startswith("pkg_")

    cit_res = cit_validator.validate_citations(
        cited_dois=["10.1038/s41556-024-001"],
        retrieved_publications=[{"doi": "10.1038/s41556-024-001", "is_preprint": False}],
    )
    assert cit_res["is_valid"] is True
    assert cit_res["peer_reviewed_count"] == 1

    ms = manuscript_gen.generate_manuscript(
        investigation_id="inv_01",
        research_question="Does EGFR regulate STAT3?",
        gap_description="Mechanistic cross-talk undefined",
        primary_hypothesis={"hypothesis_id": "hyp_01", "statement": "EGFR phosphorylates STAT3"},
        experiment_plan={"experiment_id": "exp_01", "target_proteins": ["EGFR", "STAT3"]},
        statistical_report={"effect_size": -2.4, "p_value": 0.0001, "adjusted_p_value": 0.0001},
        adversarial_report={"robustness_score": 0.88, "recommendation_notes": ["No critical flaws"]},
        retrieved_publications=[{"doi": "10.1038/s41556-024-001", "authors": ["Smith, J."], "year": 2024, "title": "EGFR Paper", "is_preprint": False}],
    )
    assert "Autonomous Mechanistic Discovery" in ms.title
    assert len(ms.figures) >= 1
    assert len(ms.tables) >= 1


def test_orchestrator_full_autonomous_workflow():
    orchestrator = PrincipalResearchOrchestrator()
    result = orchestrator.run_full_investigation(
        research_question="Does EGFR phosphorylation directly regulate STAT3 nuclear translocation?",
        auto_approve_simulation=True,
    )

    assert result["final_state"] == ResearchState.COMPLETED.value
    assert result["total_steps_executed"] > 10

    # Verify finding stored in memory
    findings = orchestrator.finding_store.list_all()
    assert len(findings) > 0
    assert any("EGFR" in f["target_entities"] for f in findings)


def test_scientific_discovery_benchmarks():
    bm = ScientificDiscoveryBenchmarkSuite()

    b1 = bm.evaluate_literature_synthesis(
        extracted_claims=[{"statement": "EGFR activates STAT3 via tyrosine phosphorylation"}],
        ground_truth_claims=["EGFR activates STAT3"],
    )
    assert b1["status"] == "PASS"

    b2 = bm.evaluate_research_gap_detection(
        detected_gaps=[{"description": "Untested interaction in hypoxic tumor microenvironment"}],
        known_expert_gaps=["untested interaction in hypoxic"],
    )
    assert b2["status"] == "PASS"

    b3 = bm.evaluate_hypothesis_falsifiability(
        hypotheses=[{"falsification_criteria": ["Lack of inhibition"], "predictions": ["50% reduction"]}],
    )
    assert b3["status"] == "PASS"

    b4 = bm.evaluate_experiment_design_soundness(
        experiment_plan={
            "controls": {"positive_controls": ["Staurosporine"], "negative_controls": ["Scrambled"], "vehicle": "DMSO"},
            "replicate_count": 5,
        }
    )
    assert b4["status"] == "PASS"

    b5 = bm.evaluate_execution_reliability([{"success": True}, {"success": True}])
    assert b5["status"] == "PASS"

    b6 = bm.evaluate_adversarial_rigor([{"passed_audit": False}], flaws_present=True)
    assert b6["status"] == "PASS"

    b7 = bm.evaluate_rediscovery_benchmark(["T790M gatekeeper mutation restores ATP affinity"], "T790M")
    assert b7["status"] == "PASS"
