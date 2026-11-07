"""Cellular Simulation Service for PROTEA Phase 8."""

from typing import Any, Dict, List, Optional, Tuple
from ai.cellular_simulation.schema import (
    SimulationModel, Species, Reaction, Parameter, InterventionSpec,
)
from ai.cellular_simulation.registry.model_registry import ModelRegistry
from ai.cellular_simulation.registry.simulation_registry import SimulationRunRegistry
from ai.cellular_simulation.registry.artifact_manager import ArtifactManager
from ai.cellular_simulation.model_builder.model_validator import ModelValidator
from ai.cellular_simulation.deterministic.ode_engine import ODEDynamicsEngine
from ai.cellular_simulation.stochastic.gillespie import GillespieEngine
from ai.cellular_simulation.stochastic.tau_leaping import TauLeapingEngine
from ai.cellular_simulation.gene_regulation.regulatory_network import RegulatoryNetworkEngine
from ai.cellular_simulation.signaling.signaling_model import SignalingEngine
from ai.cellular_simulation.metabolism.fba import FluxBalanceAnalysis
from ai.cellular_simulation.metabolism.fva import FluxVariabilityAnalysis
from ai.cellular_simulation.metabolism.gene_knockout import MetabolicKnockoutAnalyzer
from ai.cellular_simulation.hybrid.orchestrator import MultiscaleHybridOrchestrator
from ai.cellular_simulation.interventions.intervention_manager import InSilicoInterventionManager
from ai.cellular_simulation.uncertainty.sensitivity import LocalSensitivityAnalyzer
from ai.cellular_simulation.uncertainty.ensemble import EnsembleSimulator
from ai.cellular_simulation.validation.conservation import MassConservationValidator
from ai.cellular_simulation.validation.numerical_validation import NumericalValidator
from ai.cellular_simulation.evaluation.benchmarks import SimulationBenchmarks
from ai.cellular_simulation.evaluation.reproducibility import ReproducibilityVerifier


class CellularSimulationService:
    """Singleton service coordinating all Phase 8 Cellular Simulation operations."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CellularSimulationService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.model_registry = ModelRegistry()
        self.run_registry = SimulationRunRegistry()
        self._initialized = True

    # 1. Model Catalog
    def list_models(self) -> List[Dict[str, Any]]:
        return self.model_registry.list_models()

    def get_model(self, model_id: str) -> Optional[Dict[str, Any]]:
        m = self.model_registry.get_model(model_id)
        return m.to_dict() if m else None

    def register_custom_model(self, model_data: Dict[str, Any]) -> Dict[str, Any]:
        species = {
            k: Species(**v) for k, v in model_data.get("species", {}).items()
        }
        reactions = [
            Reaction(**r) for r in model_data.get("reactions", [])
        ]
        parameters = {
            k: Parameter(**v) for k, v in model_data.get("parameters", {}).items()
        }
        model = SimulationModel(
            model_id=model_data["model_id"],
            name=model_data["name"],
            model_version=model_data.get("model_version", "1.0.0"),
            model_type=model_data.get("model_type", "ODE"),
            species=species,
            reactions=reactions,
            parameters=parameters,
            compartments=model_data.get("compartments", ["cytosol"]),
            metadata=model_data.get("metadata", {}),
        )
        report = ModelValidator.validate(model)
        self.model_registry.register_model(model)
        return {
            "model_id": model.model_id,
            "status": "registered",
            "validation_report": report.to_dict(),
        }

    # 2. Deterministic ODE Simulation
    def run_deterministic(
        self,
        model_id: str,
        t_span: Tuple[float, float] = (0.0, 50.0),
        dt: float = 0.1,
        solver: str = "LSODA",
    ) -> Dict[str, Any]:
        model = self.model_registry.get_model(model_id)
        if not model:
            raise ValueError(f"Model '{model_id}' not found.")

        engine = ODEDynamicsEngine(model)
        res = engine.simulate(t_span=t_span, dt=dt, solver=solver)
        p_hash = SimulationRunRegistry.compute_provenance_hash(model, solver, t_span, dt)
        self.run_registry.record_run(res, provenance_hash=p_hash)
        val_report = NumericalValidator.validate_trajectory(res)

        output = res.to_dict()
        output["provenance_hash"] = p_hash
        output["validation"] = val_report.to_dict()
        return output

    # 3. Stochastic Simulation (Gillespie SSA / Tau-Leaping)
    def run_stochastic(
        self,
        model_id: str,
        algorithm: str = "gillespie",
        t_span: Tuple[float, float] = (0.0, 30.0),
        dt_record: float = 0.5,
        random_seed: Optional[int] = 42,
    ) -> Dict[str, Any]:
        model = self.model_registry.get_model(model_id)
        if not model:
            raise ValueError(f"Model '{model_id}' not found.")

        if algorithm.lower() == "tau_leaping":
            engine = TauLeapingEngine(model)
            res = engine.simulate(t_span=t_span, tau=dt_record, random_seed=random_seed)
        else:
            engine = GillespieEngine(model)
            res = engine.simulate(t_span=t_span, dt_record=dt_record, random_seed=random_seed)

        self.run_registry.record_run(res)
        return res.to_dict()

    # 4. Metabolic FBA & FVA
    def run_fba(
        self,
        model_id: str,
        objective_reaction: Optional[str] = None,
    ) -> Dict[str, Any]:
        model = self.model_registry.get_model(model_id)
        if not model:
            raise ValueError(f"Model '{model_id}' not found.")

        fba = FluxBalanceAnalysis(model)
        res = fba.optimize(objective_reaction=objective_reaction)
        self.run_registry.record_run(res)
        return res.to_dict()

    def run_fva(
        self,
        model_id: str,
        fraction_of_optimum: float = 0.95,
    ) -> Dict[str, Any]:
        model = self.model_registry.get_model(model_id)
        if not model:
            raise ValueError(f"Model '{model_id}' not found.")

        fva = FluxVariabilityAnalysis(model)
        ranges = fva.analyze(fraction_of_optimum=fraction_of_optimum)
        return {
            "model_id": model_id,
            "fraction_of_optimum": fraction_of_optimum,
            "flux_bounds": {k: {"min_flux": v[0], "max_flux": v[1]} for k, v in ranges.items()},
        }

    def run_metabolic_knockout_screen(self, model_id: str) -> Dict[str, Any]:
        model = self.model_registry.get_model(model_id)
        if not model:
            raise ValueError(f"Model '{model_id}' not found.")

        analyzer = MetabolicKnockoutAnalyzer(model)
        screen = analyzer.single_knockout_screen()
        return {
            "model_id": model_id,
            "reactions_screened": len(screen),
            "screen_results": screen,
        }

    # 5. Signaling Pathway Simulation
    def run_signaling_cascade(
        self,
        model_id: str = "mapk_erk_cascade",
        tiers: Optional[List[str]] = None,
        t_span: Tuple[float, float] = (0.0, 60.0),
    ) -> Dict[str, Any]:
        model = self.model_registry.get_model(model_id)
        if not model:
            raise ValueError(f"Model '{model_id}' not found.")

        engine = SignalingEngine(model)
        tiers_list = tiers or ["Raf_star", "MEK_star", "ERK_star"]
        res = engine.simulate_cascade(t_span=t_span, tiers=tiers_list)
        return res.to_dict()

    def run_dose_response(
        self,
        model_id: str = "mapk_erk_cascade",
        stimulus: str = "RasGTP",
        response: str = "ERK_star",
        doses: Optional[List[float]] = None,
    ) -> Dict[str, Any]:
        model = self.model_registry.get_model(model_id)
        if not model:
            raise ValueError(f"Model '{model_id}' not found.")

        engine = SignalingEngine(model)
        dose_list = doses or [0.01, 0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0]
        return engine.simulate_dose_response(stimulus, response, dose_list)

    # 6. Gene Regulatory Simulation
    def run_gene_regulation(
        self,
        model_id: str = "lac_operon_grn",
        t_span: Tuple[float, float] = (0.0, 100.0),
    ) -> Dict[str, Any]:
        model = self.model_registry.get_model(model_id)
        if not model:
            raise ValueError(f"Model '{model_id}' not found.")

        engine = RegulatoryNetworkEngine(model)
        res = engine.simulate_continuous(t_span=t_span)
        return res.to_dict()

    # 7. Hybrid Multiscale Simulation
    def run_hybrid_multiscale(
        self,
        model_id: str = "hybrid_signaling_grn",
    ) -> Dict[str, Any]:
        model = self.model_registry.get_model(model_id)
        if not model:
            raise ValueError(f"Model '{model_id}' not found.")

        orchestrator = MultiscaleHybridOrchestrator(model)
        res = orchestrator.simulate()
        return res.to_dict()

    # 8. In-Silico Intervention Experiments
    def run_intervention_experiment(
        self,
        model_id: str,
        spec_data: Dict[str, Any],
        t_span: Tuple[float, float] = (0.0, 50.0),
    ) -> Dict[str, Any]:
        model = self.model_registry.get_model(model_id)
        if not model:
            raise ValueError(f"Model '{model_id}' not found.")

        spec = InterventionSpec(
            intervention_id=spec_data.get("intervention_id", "pert_1"),
            intervention_type=spec_data.get("intervention_type", "KNOCKOUT"),
            target_entities=spec_data.get("target_entities", []),
            strength=float(spec_data.get("strength", 1.0)),
            parameters_modified=spec_data.get("parameters_modified", {}),
        )
        manager = InSilicoInterventionManager(model)
        return manager.run_comparative_experiment(spec, t_span=t_span)

    # 9. Uncertainty & Sensitivity
    def run_sensitivity_analysis(
        self,
        model_id: str,
        parameters: List[str],
        observables: List[str],
    ) -> Dict[str, Any]:
        model = self.model_registry.get_model(model_id)
        if not model:
            raise ValueError(f"Model '{model_id}' not found.")

        analyzer = LocalSensitivityAnalyzer(model)
        sens = analyzer.analyze(parameters, observables)
        return {
            "model_id": model_id,
            "normalized_sensitivities": sens,
        }

    def run_ensemble_uncertainty(
        self,
        model_id: str,
        num_runs: int = 25,
        cv: float = 0.2,
    ) -> Dict[str, Any]:
        model = self.model_registry.get_model(model_id)
        if not model:
            raise ValueError(f"Model '{model_id}' not found.")

        simulator = EnsembleSimulator(model)
        res = simulator.simulate_ensemble(num_runs=num_runs, cv=cv)
        return res.to_dict()

    # 10. Validation & Benchmarks
    def validate_model(self, model_id: str) -> Dict[str, Any]:
        model = self.model_registry.get_model(model_id)
        if not model:
            raise ValueError(f"Model '{model_id}' not found.")
        report = ModelValidator.validate(model)
        return report.to_dict()

    def run_all_benchmarks(self) -> Dict[str, Any]:
        return SimulationBenchmarks.run_all_benchmarks()

    def verify_reproducibility(self, seed: int = 12345) -> Dict[str, Any]:
        return ReproducibilityVerifier.verify_seed_repeatability(seed)

    # 11. Artifact Export
    def export_model_json(self, model_id: str) -> str:
        model = self.model_registry.get_model(model_id)
        if not model:
            raise ValueError(f"Model '{model_id}' not found.")
        return ArtifactManager.export_json(model)

    def export_model_sbml(self, model_id: str) -> str:
        model = self.model_registry.get_model(model_id)
        if not model:
            raise ValueError(f"Model '{model_id}' not found.")
        return ArtifactManager.export_sbml_stub(model)
