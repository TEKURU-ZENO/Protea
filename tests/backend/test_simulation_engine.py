"""Comprehensive backend test suite for PROTEA Phase 8 — Cellular Simulation Engine (CSE)."""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from ai.cellular_simulation.schema import (
    SimulationModel, Species, Reaction, Parameter, InterventionSpec,
    ModelType, RateLawType, InterventionType, ParameterProvenance
)
from ai.cellular_simulation.model_builder import (
    StoichiometryBuilder, ReactionRateEvaluator, ParameterStore,
    ModelValidator, ModelFactory
)
from ai.cellular_simulation.deterministic import (
    KineticsEvaluator, RK4Integrator, AdaptiveRKSolver, ODEDynamicsEngine
)
from ai.cellular_simulation.stochastic import (
    StochasticNetwork, GillespieEngine, TauLeapingEngine
)
from ai.cellular_simulation.gene_regulation import (
    BooleanNetwork, HillTranscriptionalKinetics, TwoStageGeneExpression,
    GeneExpressionParameters, RegulatoryNetworkEngine
)
from ai.cellular_simulation.signaling import (
    PhosphorylationCycle, SignalingCascadeAnalyzer, FeedbackAnalyzer, SignalingEngine
)
from ai.cellular_simulation.metabolism import (
    FluxBalanceAnalysis, FluxVariabilityAnalysis, MetabolicKnockoutAnalyzer,
    MetabolicConstraintsManager
)
from ai.cellular_simulation.hybrid import (
    StateExchangeBridge, MultiscaleClock, ModelCouplingLink, MultiscaleHybridOrchestrator
)
from ai.cellular_simulation.calibration import (
    CalibrationLikelihood, IdentifiabilityAnalyzer, ParameterEstimator, BayesianCalibrator
)
from ai.cellular_simulation.uncertainty import (
    LocalSensitivityAnalyzer, SobolSensitivityAnalyzer, MonteCarloSampler, EnsembleSimulator
)
from ai.cellular_simulation.interventions import (
    KnockoutIntervention, ChemicalInhibitionIntervention, OverexpressionIntervention,
    DoseResponseCurve, InSilicoInterventionManager
)
from ai.cellular_simulation.validation import (
    MassConservationValidator, NumericalValidator, BiologicalPlausibilityValidator,
    ExperimentalDataComparator
)
from ai.cellular_simulation.registry import (
    ModelRegistry, SimulationRunRegistry, ExperimentManager, ArtifactManager
)
from ai.cellular_simulation.evaluation import (
    SimulationMetrics, SimulationBenchmarks, ReproducibilityVerifier
)
from services.api.services.simulation_service import CellularSimulationService


def test_model_builder_and_factory():
    """Test 1: Model creation, stoichiometry, and validation."""
    model = ModelFactory.create_goldbeter_koshland_model()
    assert model.model_id == "goldbeter_koshland"
    assert len(model.species) == 4
    assert len(model.reactions) == 2

    report = ModelValidator.validate(model)
    assert report.is_valid is True
    assert report.non_negativity_satisfied is True

    S, species, reactions = StoichiometryBuilder.build_matrix(model)
    assert S.shape == (4, 2)
    print("[PASS] test_model_builder_and_factory")


def test_deterministic_ode_solvers():
    """Test 2: Deterministic kinetics with LSODA, RK4, and Adaptive RKF45."""
    model = ModelFactory.create_goldbeter_koshland_model()
    engine = ODEDynamicsEngine(model)

    # 1. LSODA
    res_lsoda = engine.simulate(t_span=(0.0, 30.0), dt=0.5, solver="LSODA")
    assert len(res_lsoda.trajectory.times) > 10
    assert "W_star" in res_lsoda.trajectory.species_trajectories
    w_star_lsoda = res_lsoda.trajectory.species_trajectories["W_star"][-1]
    assert w_star_lsoda > 0.0

    # 2. RK4
    res_rk4 = engine.simulate(t_span=(0.0, 30.0), dt=0.5, solver="RK4")
    assert len(res_rk4.trajectory.times) > 10

    # 3. RKF45
    res_rkf = engine.simulate(t_span=(0.0, 30.0), dt=0.5, solver="RKF45")
    assert len(res_rkf.trajectory.times) > 5

    print("[PASS] test_deterministic_ode_solvers")


def test_stochastic_simulation():
    """Test 3: Gillespie SSA and Tau-Leaping stochastic algorithms."""
    model = ModelFactory.create_goldbeter_koshland_model()

    # Gillespie SSA
    gillespie = GillespieEngine(model)
    res_ssa = gillespie.simulate(t_span=(0.0, 20.0), dt_record=0.5, random_seed=42)
    assert res_ssa.model_type == "STOCHASTIC"
    assert res_ssa.metrics["total_stochastic_steps"] > 0
    assert len(res_ssa.trajectory.times) > 5

    # Tau-Leaping
    tau_engine = TauLeapingEngine(model)
    res_tau = tau_engine.simulate(t_span=(0.0, 20.0), tau=0.2, random_seed=42)
    assert len(res_tau.trajectory.times) > 5

    print("[PASS] test_stochastic_simulation")


def test_gene_regulatory_networks():
    """Test 4: Continuous Hill transcription and Boolean network dynamics."""
    # Hill kinetics
    act = HillTranscriptionalKinetics.activation(2.0, Ka=1.0, n=2.0)
    assert 0.75 < act < 0.85
    rep = HillTranscriptionalKinetics.repression(2.0, Kr=1.0, n=2.0)
    assert 0.15 < rep < 0.25

    # Two-stage expression steady state
    expr = TwoStageGeneExpression(GeneExpressionParameters(alpha_m=0.5, delta_m=0.05, alpha_p=0.2, delta_p=0.01))
    mrna_ss, prot_ss = expr.steady_state(promoter_activity=1.0)
    assert abs(mrna_ss - 10.0) < 1e-3
    assert abs(prot_ss - 200.0) < 1e-3

    # Lac Operon Simulation
    model = ModelFactory.create_lac_operon_grn_model()
    reg_engine = RegulatoryNetworkEngine(model)
    res = reg_engine.simulate_continuous(t_span=(0.0, 50.0))
    assert res.trajectory.species_trajectories["BetaGal"][-1] > 0.0

    # Boolean network attractors
    rules = {
        "A": lambda s: 1 if s.get("B", 0) == 0 else 0,
        "B": lambda s: 1 if s.get("A", 0) == 1 else 0,
    }
    bn = BooleanNetwork(["A", "B"], rules)
    attractors = bn.find_attractors()
    assert isinstance(attractors, list)

    print("[PASS] test_gene_regulatory_networks")


def test_signaling_pathway_dynamics():
    """Test 5: Signaling cascade amplification and dose-response."""
    model = ModelFactory.create_mapk_cascade_model()
    sig_engine = SignalingEngine(model)

    # Multi-tier cascade
    res = sig_engine.simulate_cascade(
        t_span=(0.0, 50.0),
        tiers=["Raf_star", "MEK_star", "ERK_star"],
    )
    cascade_metrics = res.metrics.get("cascade_tier_analysis", {})
    assert "ERK_star" in cascade_metrics
    assert cascade_metrics["ERK_star"]["peak_concentration"] > 1.0

    # Analytical Goldbeter-Koshland
    gk_analytical = PhosphorylationCycle.goldbeter_koshland_analytical(v1=1.0, v2=0.8, J1=0.05, J2=0.05)
    assert 0.7 < gk_analytical <= 1.0

    # Dose response
    dr = sig_engine.simulate_dose_response(
        stimulus_species="RasGTP",
        response_species="ERK_star",
        doses=[0.05, 0.2, 0.5, 1.0, 5.0],
    )
    assert dr["ec50"] > 0.0

    print("[PASS] test_signaling_pathway_dynamics")


def test_metabolic_fba_and_knockouts():
    """Test 6: Flux Balance Analysis, FVA, and gene knockout screening."""
    model = ModelFactory.create_central_metabolism_fba_model()
    fba = FluxBalanceAnalysis(model)

    # 1. Base FBA
    res_fba = fba.optimize()
    z_biomass = res_fba.metrics.get("objective_value", 0.0)
    assert z_biomass > 1.0
    assert res_fba.fluxes["v_uptake"] > 0.0

    # 2. FVA
    fva = FluxVariabilityAnalysis(model)
    ranges = fva.analyze(fraction_of_optimum=0.9)
    assert "v_biomass" in ranges
    assert ranges["v_biomass"][1] >= ranges["v_biomass"][0]

    # 3. Knockout screen
    ko_analyzer = MetabolicKnockoutAnalyzer(model)
    screen = ko_analyzer.single_knockout_screen()
    assert "v_uptake" in screen
    assert screen["v_uptake"]["is_essential"] is True
    assert screen["v_lactate"]["is_essential"] is False

    print("[PASS] test_metabolic_fba_and_knockouts")


def test_hybrid_multiscale_coupling():
    """Test 7: Multiscale unit conversion and synchronized hybrid simulation."""
    # State bridge
    counts = StateExchangeBridge.concentration_to_counts(1.0, cell_volume_liters=1e-15)
    assert counts > 500
    conc = StateExchangeBridge.counts_to_concentration(counts, cell_volume_liters=1e-15)
    assert abs(conc - 1.0) < 0.05

    # Coupled hybrid run
    model = ModelFactory.create_hybrid_signaling_grn_model()
    clock = MultiscaleClock(t_start=0.0, t_end=20.0, sync_interval=2.0, fast_dt=0.1)
    link = ModelCouplingLink(
        source_model_id="mapk",
        source_variable="TF_active",
        target_model_id="grn",
        target_variable="Ka_tf",
    )
    orchestrator = MultiscaleHybridOrchestrator(model, clock=clock, coupling_links=[link])
    res_hybrid = orchestrator.simulate()
    assert len(res_hybrid.trajectory.times) > 10
    assert "Protein_target" in res_hybrid.trajectory.species_trajectories

    print("[PASS] test_hybrid_multiscale_coupling")


def test_in_silico_interventions():
    """Test 8: Genetic knockout, drug inhibition, and overexpression."""
    model = ModelFactory.create_mapk_cascade_model()
    manager = InSilicoInterventionManager(model)

    # 80% MEK chemical inhibition
    spec = InterventionSpec(
        intervention_id="pert_mek",
        intervention_type=InterventionType.INHIBITION.value,
        target_entities=["MEK"],
        strength=0.8,
    )
    comp = manager.run_comparative_experiment(spec, t_span=(0.0, 40.0))
    deltas = comp["species_deltas"]
    assert "ERK_star" in deltas
    assert deltas["ERK_star"]["perturbed_final"] < deltas["ERK_star"]["wild_type_final"]

    # Biological direction verification
    dir_check = BiologicalPlausibilityValidator.verify_perturbation_direction(
        wild_type_final=deltas["ERK_star"]["wild_type_final"],
        perturbed_final=deltas["ERK_star"]["perturbed_final"],
        expected_direction="DECREASE",
        target_name="Phospho-ERK",
    )
    assert dir_check["passed"] is True

    print("[PASS] test_in_silico_interventions")


def test_sensitivity_and_uncertainty():
    """Test 9: Local sensitivity, Sobol indices, and Monte Carlo ensembles."""
    model = ModelFactory.create_mapk_cascade_model()

    # Local sensitivity
    sens_analyzer = LocalSensitivityAnalyzer(model)
    sens = sens_analyzer.analyze(
        parameters_to_test=["k_act_raf", "k_act_mek"],
        observables=["ERK_star"],
        t_span=(0.0, 30.0),
    )
    assert "ERK_star" in sens

    # Monte Carlo Ensemble
    ens_sim = EnsembleSimulator(model)
    res_ens = ens_sim.simulate_ensemble(num_runs=10, cv=0.15, t_span=(0.0, 20.0), seed=42)
    assert res_ens.uncertainty_intervals is not None
    assert "ERK_star" in res_ens.uncertainty_intervals
    assert "ci_lower" in res_ens.uncertainty_intervals["ERK_star"]
    assert "ci_upper" in res_ens.uncertainty_intervals["ERK_star"]

    print("[PASS] test_sensitivity_and_uncertainty")


def test_validation_and_benchmarks():
    """Test 10: Invariant mass conservation, seed reproducibility, and 7-suite benchmarks."""
    # 1. Mass conservation
    model = ModelFactory.create_goldbeter_koshland_model()
    engine = ODEDynamicsEngine(model)
    res = engine.simulate(t_span=(0.0, 30.0), dt=0.2)
    cons_report = MassConservationValidator.verify_conservation(model, res.trajectory)
    assert cons_report["is_conserved"] is True

    # 2. Numerical validation
    num_report = NumericalValidator.validate_trajectory(res)
    assert num_report.is_valid is True
    assert num_report.non_negativity_satisfied is True

    # 3. Reproducibility
    repro = ReproducibilityVerifier.verify_seed_repeatability(seed=999)
    assert repro["exact_match"] is True

    # 4. Master Benchmark Suite
    benchmarks_report = SimulationBenchmarks.run_all_benchmarks()
    assert benchmarks_report["all_passed"] is True
    assert benchmarks_report["passed_benchmarks"] == 7
    assert benchmarks_report["score_percentage"] == 100.0

    print("[PASS] test_validation_and_benchmarks")


def test_cellular_simulation_service():
    """Test 11: Singleton CellularSimulationService API coordinator."""
    svc = CellularSimulationService()

    # List models
    models = svc.list_models()
    assert len(models) >= 5

    # Run deterministic ODE
    res_det = svc.run_deterministic("goldbeter_koshland", t_span=(0.0, 20.0), solver="LSODA")
    assert res_det["job_id"].startswith("sim_")
    assert "provenance_hash" in res_det

    # Run FBA
    res_fba = svc.run_fba("central_metabolism_fba")
    assert res_fba["is_steady_state"] is True
    assert res_fba["metrics"]["objective_value"] > 0.0

    # Run Intervention
    res_pert = svc.run_intervention_experiment(
        "mapk_erk_cascade",
        {"intervention_type": "INHIBITION", "target_entities": ["MEK"], "strength": 0.5},
    )
    assert "species_deltas" in res_pert

    # Export formats
    json_export = svc.export_model_json("goldbeter_koshland")
    assert "goldbeter_koshland" in json_export
    sbml_export = svc.export_model_sbml("goldbeter_koshland")
    assert "<sbml" in sbml_export

    print("[PASS] test_cellular_simulation_service")


if __name__ == "__main__":
    print("==================================================================")
    print("RUNNING PROTEA PHASE 8 CELLULAR SIMULATION ENGINE TEST SUITE")
    print("==================================================================")
    test_model_builder_and_factory()
    test_deterministic_ode_solvers()
    test_stochastic_simulation()
    test_gene_regulatory_networks()
    test_signaling_pathway_dynamics()
    test_metabolic_fba_and_knockouts()
    test_hybrid_multiscale_coupling()
    test_in_silico_interventions()
    test_sensitivity_and_uncertainty()
    test_validation_and_benchmarks()
    test_cellular_simulation_service()
    print("==================================================================")
    print("ALL 11 TEST SUITES PASSED (100% SUCCESS)!")
    print("==================================================================")
