"""
Unit & Integration Test Suite for PROTEA Phase 12:
Biological Intelligence Foundation Model (BIFM)
"""

import pytest
from ai.bifm.schema import (
    ModalityType,
    BiologicalDomain,
    EvidenceLevel,
    BiologicalContext,
    BiologicalRepresentation,
    MultiModalProfile,
    TaskPrediction,
    WorldModelState,
    InterventionSpec,
    CounterfactualResult,
    StructuredExplanation,
    ModelCardRecord
)
from ai.bifm.representations.canonical import UniversalRepresentationRegistry
from ai.bifm.encoders.adapters import (
    BiologicalEncoder,
    SequenceEncoderAdapter,
    StructureEncoderAdapter,
    InteractionEncoderAdapter,
    PathwayEncoderAdapter,
    OmicsEncoderAdapter,
    CellularEncoderAdapter,
    SpatialEncoderAdapter,
    EvolutionEncoderAdapter,
    LiteratureEncoderAdapter
)
from ai.bifm.fusion.cross_modal_fusion import CrossModalFusionEngine
from ai.bifm.knowledge.grounding_engine import BiologicalKnowledgeGroundingEngine
from ai.bifm.prediction.multitask_engine import BiologicalMultiTaskEngine
from ai.bifm.context.conditional_engine import BiologicalContextEngine
from ai.bifm.world_model.state_transition import BiologicalWorldModel
from ai.bifm.counterfactuals.intervention_engine import CounterfactualIntelligenceEngine
from ai.bifm.reasoning.scientific_reasoning import UnifiedBiologicalReasoningEngine
from ai.bifm.research.autonomous_orchestrator import AutonomousResearchInterface
from ai.bifm.continual.adapter_manager import ContinualLearningEngine
from ai.bifm.governance.model_cards import FoundationModelGovernance
from ai.bifm.evaluation.benchmarks import BIFMBenchmarkSuite
from services.api.services.bifm_service import BIFMService


def test_universal_representation_registry():
    """Module A: Test canonical entity registration, versioning, hash, and immutability."""
    registry = UniversalRepresentationRegistry()

    rep = registry.register_representation(
        entity_id="uniprot:P15056",
        entity_type="protein",
        modality="sequence",
        embedding=[0.12, -0.45, 0.88, 0.23] * 64,
        model_name="esm2",
        model_version="2.0.0",
        organism_id="9606",
        representation_version="v1"
    )

    assert rep.entity_id == "uniprot:P15056"
    assert rep.modality == "sequence"
    assert len(rep.embedding) == 256

    h = registry.compute_representation_hash(rep)
    assert len(h) == 16

    retrieved = registry.get_representation("uniprot:P15056", "sequence", "v1")
    assert retrieved is not None
    assert retrieved.entity_id == "uniprot:P15056"

    prof = registry.get_multimodal_profile("uniprot:P15056")
    assert prof is not None
    assert "sequence" in prof.modality_representations


def test_multimodal_encoders_all_modalities():
    """Module B: Test all 9 modality encoders for validation and normalized embeddings."""
    seq_enc = SequenceEncoderAdapter()
    struct_enc = StructureEncoderAdapter()
    inter_enc = InteractionEncoderAdapter()
    path_enc = PathwayEncoderAdapter()
    omics_enc = OmicsEncoderAdapter()
    cell_enc = CellularEncoderAdapter()
    spat_enc = SpatialEncoderAdapter()
    evo_enc = EvolutionEncoderAdapter()
    lit_enc = LiteratureEncoderAdapter()

    assert seq_enc.validate_input("MNGTEGPNFYVPFSNKTG") is True
    assert seq_enc.validate_input("1234INVALID") is False

    v_seq = seq_enc.encode("MNGTEGPNFYVPFSNKTG")
    assert len(v_seq) == 256

    v_struct = struct_enc.encode({"pdb": "1XYZ", "coords": [[0, 1, 2]]})
    assert len(v_struct) == 256

    v_inter = inter_enc.encode(["BRAF-MAP2K1"])
    assert len(v_inter) == 256

    v_path = path_enc.encode("Reactome:R-HSA-5683057")
    assert len(v_path) == 256

    v_omics = omics_enc.encode({"BRAF": 12.5, "EGFR": 8.4})
    assert len(v_omics) == 256

    v_cell = cell_enc.encode("T_Cell_CD8_Cytotoxic")
    assert len(v_cell) == 256

    v_spat = spat_enc.encode({"x": 120.0, "y": 340.0})
    assert len(v_spat) == 256

    v_evo = evo_enc.encode("Bilateria_Ortholog_RAF")
    assert len(v_evo) == 256

    v_lit = lit_enc.encode("BRAF V600E confers constitutive kinase activity.")
    assert len(v_lit) == 256


def test_cross_modal_fusion_and_shared_private_latent():
    """Module C: Test multimodal alignment, shared/private VAE factor recovery, and cosine score."""
    registry = UniversalRepresentationRegistry()
    seq_enc = SequenceEncoderAdapter()
    omics_enc = OmicsEncoderAdapter()

    v_seq = seq_enc.encode("MNGTEGPNFYVPFSNKTG")
    v_omics = omics_enc.encode([2.5, 4.1, 1.2, 5.0])

    rep1 = registry.register_representation("BRAF", "protein", "sequence", v_seq, "esm2")
    rep2 = registry.register_representation("BRAF", "protein", "omics", v_omics, "scvi")

    profile = registry.get_multimodal_profile("BRAF")
    fusion = CrossModalFusionEngine(unified_dim=256, shared_dim=64, private_dim=32)

    fused = fusion.fuse_multimodal_profile(profile)
    assert len(fused["unified_embedding"]) == 256
    assert len(fused["shared_factors"]) == 64
    assert "sequence" in fused["private_factors"]
    assert "omics" in fused["private_factors"]
    assert fused["variance_explained"] >= 0.70

    score = fusion.compute_cross_modal_alignment_score(rep1, rep2)
    assert -1.0 <= score <= 1.0


def test_missing_modality_bayesian_imputation():
    """Module C: Test Bayesian missing-modality latent reconstruction with uncertainty envelope."""
    fusion = CrossModalFusionEngine(unified_dim=256, shared_dim=64, private_dim=32)
    shared_factors = [0.18] * 64

    imputed = fusion.impute_missing_modality(shared_factors, "phosphoproteomics", target_dim=256)
    assert len(imputed["imputed_embedding"]) == 256
    assert imputed["target_modality"] == "phosphoproteomics"
    assert imputed["mean_uncertainty_std"] > 0.0
    assert imputed["is_imputed"] is True


def test_knowledge_grounding_and_constraint_checking():
    """Module D: Test grounding in UBKG, constraint verification, and contradiction detection."""
    grounding = BiologicalKnowledgeGroundingEngine()

    braf_g = grounding.ground_entity("BRAF")
    assert braf_g["is_grounded"] is True
    assert "GO:0004709" in braf_g["go_terms"]
    assert "MAP2K1" in braf_g["interactors"]

    ev_pkg = grounding.retrieve_evidence_package("BRAF", "MAP2K1")
    assert ev_pkg["is_grounded_in_ubkg"] is True
    assert ev_pkg["known_physical_binding"] is True
    assert ev_pkg["evidence_count"] >= 3

    # Constraint check: nuclear TP53 cannot bind extracellular ligand EGF directly
    constraint_res = grounding.verify_biological_constraints("TP53", "EGF", "direct_physical_binding")
    assert constraint_res["passes_constraints"] is False
    assert "Spatial Disjointness" in constraint_res["violations"][0]

    contradictions = grounding.detect_contradictions("BRAF is an inactive dead kinase", "BRAF")
    assert len(contradictions) >= 1
    assert "constitutive kinase activation" in contradictions[0]["detail"]


def test_multitask_prediction_heads():
    """Module E: Test function, interaction, evolution transfer, mutation, and therapeutic prioritization."""
    multitask = BiologicalMultiTaskEngine()
    latent = [0.2] * 256

    fn_pred = multitask.predict_protein_function("BRAF", latent)
    assert fn_pred.task_name == "protein_function"
    assert fn_pred.probability >= 0.85
    assert len(fn_pred.prediction_value) >= 3

    ppi_pred = multitask.predict_protein_interaction("BRAF", "MAP2K1", latent, latent)
    assert ppi_pred.task_name == "protein_interaction"
    assert ppi_pred.prediction_value["is_interacting"] is True
    assert ppi_pred.probability >= 0.85

    evo_pred = multitask.predict_evolution_transfer("BRAF", 9606, 10090)
    assert evo_pred.task_name == "evolution_transfer"
    assert evo_pred.prediction_value["is_transferable"] is True

    mut_pred = multitask.predict_mutation_effect("BRAF", "V600E", latent)
    assert mut_pred.task_name == "mutation_effect"
    assert mut_pred.prediction_value["pathogenic_status"] == "PATHOGENIC"

    target_pred = multitask.predict_therapeutic_prioritization("BRAF", latent)
    assert target_pred.task_name == "therapeutic_prioritization"
    assert target_pred.prediction_value["is_favored"] is True

    polr_pred = multitask.predict_therapeutic_prioritization("POLR2A", latent)
    assert polr_pred.prediction_value["is_favored"] is False


def test_contextual_film_modulation():
    """Module F: Test FiLM modulation by tissue/disease context and concordance evaluation."""
    context_engine = BiologicalContextEngine(context_dim=64)
    base_rep = UniversalRepresentationRegistry().register_representation(
        entity_id="BRAF",
        entity_type="protein",
        modality="sequence",
        embedding=[0.35] * 256,
        model_name="esm2"
    )

    ctx_melanoma = BiologicalContext(tissue="Skin", disease_state="Melanoma", mutation_status="V600E")
    ctx_lung = BiologicalContext(tissue="Lung", disease_state="Healthy")

    mod_melanoma = context_engine.contextualize_representation(base_rep, ctx_melanoma)
    mod_lung = context_engine.contextualize_representation(base_rep, ctx_lung)

    assert mod_melanoma.modality == "sequence_contextualized"
    diff = sum(abs(a - b) for a, b in zip(mod_melanoma.embedding, mod_lung.embedding))
    assert diff > 1.0

    concordance = context_engine.evaluate_context_concordance(ctx_melanoma, ctx_lung)
    assert "transferability_score" in concordance
    assert concordance["same_tissue"] is False


def test_world_model_state_transition_and_trajectory():
    """Module G: Test world model state initialization, transition under intervention, and trajectory."""
    world_model = BiologicalWorldModel(state_dim=128)
    init_state = world_model.initialize_state("sys_melanoma")

    assert init_state.system_id == "sys_melanoma"
    assert len(init_state.state_vector) == 128
    assert init_state.pathway_activities["MAPK_Signaling"] > 0.80

    spec = InterventionSpec(target_entity="BRAF", intervention_type="small_molecule_inhibition", magnitude=0.10)
    stepped = world_model.transition_state(init_state, spec, steps=2)

    assert stepped.step == 2
    assert stepped.pathway_activities["MAPK_Signaling"] < init_state.pathway_activities["MAPK_Signaling"]
    assert stepped.pathway_activities["Apoptosis_Pathway"] > init_state.pathway_activities["Apoptosis_Pathway"]

    trajectory = world_model.forecast_trajectory(init_state, spec, total_steps=3)
    assert len(trajectory) == 4
    assert trajectory[-1].step == 3


def test_counterfactual_intelligence_and_epistemology():
    """Module H: Test counterfactual simulation delta norm, rewiring, and epistemic categorization."""
    cf_engine = CounterfactualIntelligenceEngine()
    spec = InterventionSpec(target_entity="BRAF", intervention_type="gene_knockout", magnitude=0.0)

    result = cf_engine.evaluate_counterfactual(spec)
    assert result.is_counterfactual_hypothesis is True
    assert result.state_delta_norm > 0.5
    assert len(result.candidate_rewired_edges) >= 2
    assert "CRAF" in result.candidate_rewired_edges[1]["edge"]

    cat_obs = cf_engine.categorize_epistemic_evidence("observation")
    cat_cf = cf_engine.categorize_epistemic_evidence("counterfactual")
    assert cat_obs["provenance_tier"] == 1
    assert cat_cf["provenance_tier"] == 4


def test_scientific_reasoning_and_explanation():
    """Module I: Test unified mechanistic reasoning, competing hypotheses, and falsification tests."""
    reasoning = UnifiedBiologicalReasoningEngine()
    explanation = reasoning.generate_explanation(
        question="How does BRAF V600E disrupt the MAPK cascade and drive proliferation?",
        focal_gene="BRAF",
        partner_gene="MAP2K1"
    )

    assert explanation.focal_entities == ["BRAF", "MAP2K1"]
    assert "constitutive monomeric kinase activity" in explanation.proposed_mechanism
    assert len(explanation.competing_hypotheses) == 3
    assert len(explanation.falsification_experiments) == 2
    assert "In vitro Kinase Assay" in explanation.falsification_experiments[0]["experiment_type"]


def test_autonomous_research_workflow():
    """Module J: Test ABDE discovery workflow (hypotheses, in-silico experiment, critic review, manuscript)."""
    orchestrator = AutonomousResearchInterface()
    inv_res = orchestrator.launch_investigation(
        research_question="What mechanisms govern therapeutic vulnerability in BRAF-mutant melanoma?",
        focal_gene="BRAF",
        partner_gene="MAP2K1"
    )

    assert inv_res["status"] == "COMPLETED"
    assert "explanation" in inv_res
    assert "simulation_result" in inv_res
    assert "critic_review" in inv_res
    assert inv_res["critic_review"]["critic_score"] > 0.85
    assert "manuscript" in inv_res
    assert "In-Silico Systems Investigation" in inv_res["manuscript"]["title"]


def test_continual_learning_and_regression_release_gate():
    """Module K: Test LoRA adapter registration, drift tracking, and promotion release gate."""
    continual = ContinualLearningEngine(lora_rank=16, lora_alpha=32)
    adapter = continual.register_adapter("oncology", "target_discovery", ["TCGA_Melanoma", "CPTAC"])

    assert adapter["rank"] == 16
    assert adapter["status"] == "REGISTERED"

    # Test release gate approval
    approved_res = continual.audit_regression_gate(adapter["adapter_id"], benchmark_pass_rate=0.98)
    assert approved_res["is_promotable"] is True
    assert approved_res["verdict"] == "PROMOTED_TO_PRODUCTION"

    # Test release gate rejection
    rejected_res = continual.audit_regression_gate(adapter["adapter_id"], benchmark_pass_rate=0.85)
    assert rejected_res["is_promotable"] is False


def test_foundation_model_governance_and_model_card():
    """Module L: Test model card generation and mandatory safety disclosures."""
    gov = FoundationModelGovernance()
    card = gov.generate_bifm_model_card()

    assert card.model_id == "bifm_v1_0_core"
    assert len(card.modalities_supported) == 9
    assert card.benchmark_macro_score > 0.90
    assert card.approval_status == "APPROVED_FOR_RESEARCH_RELEASE"

    payload = {"test": 123}
    safe_payload = gov.verify_safety_disclaimers(payload)
    assert "safety_disclosure" in safe_payload
    assert "research and decision-support" in safe_payload["safety_disclosure"]


def test_bifm_benchmarks_all_passing():
    """Test that all 10 BIFM standardized research benchmarks pass at 100%."""
    suite = BIFMBenchmarkSuite()
    summary = suite.run_all_benchmarks()

    assert summary["status"] == "PASSED"
    assert summary["passed_benchmarks"] == 10
    assert summary["total_benchmarks"] == 10
    assert summary["pass_rate_percent"] == 100.0


def test_bifm_service_facade_and_api():
    """Module 15: Test end-to-end integration via the BIFMService singleton facade."""
    service = BIFMService()
    assert service is not None

    # Test encoding
    rep = service.encode_entity("TP53", "protein", "sequence", "MEEPQSDPSVEPPLSQETFS")
    assert rep["entity_id"] == "TP53"
    assert len(rep["embedding"]) == 256

    # Test alignment
    align_res = service.align_entity_modalities("BRAF")
    assert len(align_res["unified_embedding"]) == 256

    # Test prediction
    pred = service.predict("protein_function", "BRAF")
    assert pred["task_name"] == "protein_function"
    assert "safety_disclosure" in pred

    # Test world model forecast
    forecast = service.forecast_world_model("sys_01", "BRAF", steps=2)
    assert len(forecast) == 3

    # Test counterfactual
    cf = service.evaluate_counterfactual("BRAF", "small_molecule_inhibition", 0.10)
    assert cf["is_counterfactual_hypothesis"] is True

    # Test investigation
    inv = service.launch_investigation("How does BRAF interact with MAP2K1?", "BRAF", "MAP2K1")
    assert inv["status"] == "COMPLETED"

    # Test model card & benchmarks
    card = service.get_model_card()
    assert card["model_id"] == "bifm_v1_0_core"

    bench = service.run_benchmarks()
    assert bench["status"] == "PASSED"
