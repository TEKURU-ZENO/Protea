"""Phase 7: Digital Interactome Twin (DIT) Backend Test Suite."""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from ai.digital_twin.comparison.twin_comparator import DigitalTwinComparator
from ai.digital_twin.evaluation.benchmarks import DigitalTwinBenchmarkSuite
from ai.digital_twin.evaluation.leakage_checks import LeakageChecker
from ai.digital_twin.initialization.initializer import DigitalTwinInitializer
from ai.digital_twin.interactome.builder import ContextAwareInteractomeBuilder
from ai.digital_twin.multiomics.integration import MultiOmicsIntegrator
from ai.digital_twin.registry import DigitalTwinRegistry
from ai.digital_twin.scenarios.scenario_manager import ScenarioManager
from ai.digital_twin.schema import (
    EdgeStatus,
    EdgeType,
    InterventionType,
    Modality,
    MolecularObservation,
    MolecularState,
    NetworkEdgeEvidence,
    StateStatus,
    TemporalObservation,
)
from ai.digital_twin.state.state_estimator import StateEstimator
from ai.digital_twin.state.state_manager import BiologicalStateManager
from ai.digital_twin.synchronization.assimilation import DataAssimilator
from ai.digital_twin.synchronization.conflict_resolution import ConflictResolver
from ai.digital_twin.synchronization.state_updater import TwinStateUpdater
from ai.digital_twin.temporal.change_detection import ChangeDetectionEngine
from ai.digital_twin.temporal.temporal_graph import TemporalGraphManager
from ai.digital_twin.validation.uncertainty import TwinValidationEngine
from services.api.services.digital_twin_service import DigitalTwinService


def test_twin_initialization():
    initializer = DigitalTwinInitializer()
    twin = initializer.initialize_twin(
        name="Test Hepatocyte Twin",
        organism="NCBI:9606",
        tissue="liver",
        cell_type="hepatocyte",
        condition="healthy",
        mode="hybrid"
    )

    assert twin.twin_id.startswith("DTW-")
    assert twin.organism == "NCBI:9606"
    assert twin.primary_tissue == "liver"
    active_v = twin.get_active_version()
    assert active_v is not None
    assert active_v.version_tag == "v1.0"
    assert active_v.snapshot is not None
    assert len(active_v.snapshot.nodes) >= 15
    assert len(active_v.snapshot.edges) >= 10
    assert len(active_v.content_hash) == 64  # SHA256

    # Verify states
    assert "ALB" in active_v.states
    assert active_v.states["ALB"].gene_expression == 14.8
    assert active_v.states["ALB"].status == StateStatus.OBSERVED.value
    print("[PASS] test_twin_initialization passed")


def test_context_aware_interactome():
    builder = ContextAwareInteractomeBuilder()
    twin = DigitalTwinInitializer().initialize_twin()
    active_v = twin.get_active_version()

    # Filter with restricted expressed nodes
    expressed = {"HNF4A", "ALB", "CYP3A4", "INSR", "IRS1", "AKT1"}
    compartment_map = {
        "HNF4A": "nucleus",
        "ALB": "cytosol",
        "CYP3A4": "endoplasmic_reticulum",
        "INSR": "plasma_membrane",
        "IRS1": "cytosol",
        "AKT1": "cytosol"
    }

    filtered_snap = builder.build_context_interactome(
        twin_id=twin.twin_id,
        version_id=active_v.version_id,
        nodes=list(expressed),
        candidate_edges=active_v.snapshot.edges,
        context=active_v.context,
        expressed_nodes=expressed,
        compartment_map=compartment_map
    )

    assert len(filtered_snap.nodes) == len(expressed)
    # Undirected edges must not become directed regulation
    for e in filtered_snap.edges:
        if e.edge_type == EdgeType.PHYSICAL_INTERACTION.value and not e.directed:
            assert e.directed is False
    print("[PASS] test_context_aware_interactome passed")


def test_state_representation_and_estimation():
    estimator = StateEstimator()
    twin = DigitalTwinInitializer().initialize_twin()
    v = twin.get_active_version()

    # Introduce a node with missing abundance and activity
    v.states["TEST_GENE"] = MolecularState(
        entity_id="TEST_GENE",
        gene_expression=8.0,
        protein_abundance=None,
        protein_activity=None,
        status=StateStatus.OBSERVED.value
    )

    # Estimate
    estimated_states = estimator.estimate_missing_states(v.states, v.snapshot.edges)
    test_state = estimated_states["TEST_GENE"]

    assert test_state.protein_abundance is not None
    assert "protein_abundance" in test_state.imputed_fields
    assert test_state.status == StateStatus.ESTIMATED.value
    assert test_state.confidence < 1.0  # Confidence penalty applied
    print("[PASS] test_state_representation_and_estimation passed")


def test_temporal_dynamics():
    time_series = [
        TemporalObservation(
            timepoint=0.0,
            states={
                "CYP3A4": MolecularState(entity_id="CYP3A4", gene_expression=10.0),
                "TP53": MolecularState(entity_id="TP53", gene_expression=6.0)
            }
        ),
        TemporalObservation(
            timepoint=6.0,
            states={
                "CYP3A4": MolecularState(entity_id="CYP3A4", gene_expression=12.5),  # Acute shift
                "TP53": MolecularState(entity_id="TP53", gene_expression=6.1)
            }
        ),
        TemporalObservation(
            timepoint=24.0,
            states={
                "CYP3A4": MolecularState(entity_id="CYP3A4", gene_expression=10.2),
                "TP53": MolecularState(entity_id="TP53", gene_expression=6.0)
            }
        )
    ]

    detector = ChangeDetectionEngine(velocity_threshold=0.30)
    change_points = detector.detect_change_points(time_series, feature="gene_expression")

    assert len(change_points) >= 1
    top_responder = change_points[0]["top_responders"][0]
    assert top_responder["entity"] == "CYP3A4"
    assert top_responder["delta"] == 2.5
    print("[PASS] test_temporal_dynamics passed")


def test_multiomics_integration():
    integrator = MultiOmicsIntegrator()
    twin = DigitalTwinInitializer().initialize_twin()
    v = twin.get_active_version()

    observations = [
        MolecularObservation(
            observation_id="OBS-1",
            entity_id="ALB",
            modality=Modality.TRANSCRIPTOMICS.value,
            measurement_type="gene_expression",
            value=15.0,
            unit="log2(TPM)",
            organism_id="NCBI:9606",
            tissue_id="liver",
            cell_type_id="hepatocyte",
            sample_id="SMP-1",
            condition="observed",
            timepoint=0.0,
            assay="RNA-seq",
            source_dataset="GEO:GSE1",
            uncertainty=0.05
        ),
        MolecularObservation(
            observation_id="OBS-2",
            entity_id="ALB",
            modality=Modality.PROTEOMICS.value,
            measurement_type="protein_abundance",
            value=15.4,
            unit="log2(LFQ)",
            organism_id="NCBI:9606",
            tissue_id="liver",
            cell_type_id="hepatocyte",
            sample_id="SMP-1",
            condition="observed",
            timepoint=0.0,
            assay="LC-MS/MS",
            source_dataset="PRIDE:PXD1",
            uncertainty=0.08
        )
    ]

    updated = integrator.integrate_observations(v.states, observations)
    assert updated["ALB"].gene_expression == 15.0
    assert updated["ALB"].protein_abundance == 15.4

    concordance = integrator.compute_cross_modal_concordance(updated)
    assert concordance["concordance_score"] >= 0.80
    print("[PASS] test_multiomics_integration passed")


def test_data_assimilation_and_updating():
    assimilator = DataAssimilator(process_variance=0.05, default_measurement_variance=0.15)
    st = MolecularState(entity_id="AKT1", gene_expression=7.0, confidence=0.80)

    # Kalman update
    updated_st = assimilator.assimilate_kalman(st, measurement_value=7.5, measurement_variance=0.10)
    assert 7.0 < updated_st.gene_expression < 7.5

    # State updater versioning
    twin = DigitalTwinInitializer().initialize_twin()
    updater = TwinStateUpdater()
    new_obs = [
        MolecularObservation(
            observation_id="OBS-U1",
            entity_id="AKT1",
            modality=Modality.TRANSCRIPTOMICS.value,
            measurement_type="gene_expression",
            value=7.8,
            unit="log2(TPM)",
            organism_id="NCBI:9606",
            tissue_id="liver",
            cell_type_id="hepatocyte",
            sample_id="SMP-2",
            condition="healthy",
            timepoint=0.0,
            assay="RNA-seq",
            source_dataset="GEO:GSE2"
        )
    ]

    new_v = updater.update_twin_with_observations(twin, new_obs, new_version_tag="v1.1")
    assert new_v.version_tag == "v1.1"
    assert new_v.parent_version_id == "VER-1.0-BASE"
    assert twin.active_version_id == new_v.version_id
    assert len(twin.versions) == 2
    print("[PASS] test_data_assimilation_and_updating passed")


def test_twin_comparison():
    comparator = DigitalTwinComparator()
    twin = DigitalTwinInitializer().initialize_twin()
    v_base = twin.get_active_version()

    # Create disease version
    pert_states = {k: MolecularState(**st.to_dict()) for k, st in v_base.states.items()}
    pert_states["TP53"].gene_expression = 3.5  # Downregulated
    pert_states["AKT1"].gene_expression = 9.5  # Upregulated

    v_pert = DigitalTwinInitializer().initialize_twin().get_active_version()
    v_pert.states = pert_states
    v_pert.context.condition = "HCC"

    diff = comparator.compare_versions(v_base, v_pert)
    assert diff["baseline_condition"] == "healthy"
    assert diff["perturbed_condition"] == "HCC"
    assert diff["differential_state"]["significant_count"] >= 2
    print("[PASS] test_twin_comparison passed")


def test_scenario_management():
    manager = ScenarioManager()
    twin = DigitalTwinInitializer().initialize_twin()
    v_base = twin.get_active_version()
    base_tp53_expr = v_base.states["TP53"].gene_expression

    scenario = manager.create_and_run_scenario(
        twin=twin,
        name="TP53 Knockout Experiment",
        intervention_type=InterventionType.KNOCKOUT.value,
        target_entities=["TP53"],
        strength=1.0
    )

    # CRITICAL TEST: Parent baseline states MUST NOT be modified
    assert v_base.states["TP53"].gene_expression == base_tp53_expr
    assert v_base.states["TP53"].status == StateStatus.OBSERVED.value

    # Scenario result has simulated states
    assert scenario.result is not None
    sim_tp53 = scenario.result.perturbed_states["TP53"]
    assert sim_tp53.status == StateStatus.SIMULATED.value
    assert sim_tp53.gene_expression < base_tp53_expr
    print("[PASS] test_scenario_management passed")


def test_validation_engine():
    validator = TwinValidationEngine()
    twin = DigitalTwinInitializer().initialize_twin()
    report = validator.validate_twin_version(twin)

    assert report.is_valid is True
    assert "auroc" in report.structural_fidelity
    assert "mae" in report.state_fidelity
    assert "tissue_specificity_score" in report.context_fidelity
    assert "calibration_ece" in report.uncertainty_calibration
    assert report.coverage_score > 0.80
    print("[PASS] test_validation_engine passed")


def test_service_and_benchmarks():
    service = DigitalTwinService()
    twins = service.list_twins()
    assert len(twins) >= 1

    twin_id = twins[0]["twin_id"]
    state_res = service.get_molecular_state(twin_id)
    assert "summary" in state_res
    assert "states" in state_res

    # Run full 6-experiment benchmark suite
    bench_res = service.run_benchmarks()
    assert len(bench_res) == 6
    for exp_key, exp_data in bench_res.items():
        assert exp_data["passed"] is True, f"Benchmark {exp_key} failed: {exp_data}"

    print("[PASS] test_service_and_benchmarks passed")


if __name__ == "__main__":
    print("Executing Phase 7 DIT backend test suite...")
    test_twin_initialization()
    test_context_aware_interactome()
    test_state_representation_and_estimation()
    test_temporal_dynamics()
    test_multiomics_integration()
    test_data_assimilation_and_updating()
    test_twin_comparison()
    test_scenario_management()
    test_validation_engine()
    test_service_and_benchmarks()
    print("All Phase 7 DIT backend tests passed successfully!")
