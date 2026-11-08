"""Service layer orchestrating Digital Interactome Twin operations."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from ai.digital_twin.comparison.twin_comparator import DigitalTwinComparator
from ai.digital_twin.evaluation.benchmarks import DigitalTwinBenchmarkSuite
from ai.digital_twin.initialization.initializer import DigitalTwinInitializer
from ai.digital_twin.interactome.builder import ContextAwareInteractomeBuilder
from ai.digital_twin.multiomics.integration import MultiOmicsIntegrator
from ai.digital_twin.registry import DigitalTwinRegistry
from ai.digital_twin.scenarios.scenario_manager import ScenarioManager
from ai.digital_twin.schema import (
    DigitalTwin,
    InteractomeSnapshot,
    MolecularObservation,
    MolecularState,
    TemporalObservation,
    TwinScenario,
    TwinValidationReport,
    TwinVersion,
)
from ai.digital_twin.state.state_estimator import StateEstimator
from ai.digital_twin.state.state_manager import BiologicalStateManager
from ai.digital_twin.synchronization.state_updater import TwinStateUpdater
from ai.digital_twin.temporal.change_detection import ChangeDetectionEngine
from ai.digital_twin.temporal.temporal_graph import TemporalGraphManager
from ai.digital_twin.validation.uncertainty import TwinValidationEngine

logger = logging.getLogger(__name__)


class DigitalTwinService:
    """Singleton service layer managing digital twins, runtime operations, and background jobs."""
    _instance: Optional[DigitalTwinService] = None

    def __new__(cls) -> DigitalTwinService:
        if cls._instance is None:
            cls._instance = super(DigitalTwinService, cls).__new__(cls)
            cls._instance._init_service()
        return cls._instance

    def _init_service(self) -> None:
        self.registry = DigitalTwinRegistry.get_instance()
        self.initializer = DigitalTwinInitializer()
        self.interactome_builder = ContextAwareInteractomeBuilder()
        self.state_manager = BiologicalStateManager()
        self.state_estimator = StateEstimator()
        self.multiomics_integrator = MultiOmicsIntegrator()
        self.state_updater = TwinStateUpdater()
        self.comparator = DigitalTwinComparator()
        self.scenario_manager = ScenarioManager()
        self.validator = TwinValidationEngine()
        self.change_detector = ChangeDetectionEngine()
        self.temporal_graph_mgr = TemporalGraphManager()
        self.benchmark_suite = DigitalTwinBenchmarkSuite()

        # Seed initial canonical Human Hepatocyte Digital Twin
        self._seed_default_twin()

    def _seed_default_twin(self) -> None:
        """Seeds the default Human Liver Hepatocyte Twin."""
        twin = self.initializer.initialize_twin(
            name="Human Liver Hepatocyte Twin",
            organism="NCBI:9606",
            tissue="liver",
            cell_type="hepatocyte",
            condition="healthy",
            mode="hybrid"
        )
        # Add initial temporal observation series
        v = twin.get_active_version()
        if v:
            t0_states = {k: MolecularState(**st.to_dict()) for k, st in v.states.items()}
            t6_states = {k: MolecularState(**st.to_dict()) for k, st in v.states.items()}
            t12_states = {k: MolecularState(**st.to_dict()) for k, st in v.states.items()}
            t24_states = {k: MolecularState(**st.to_dict()) for k, st in v.states.items()}

            # Dynamic expression shifts over circadian/treatment timeline
            if "CYP3A4" in t6_states:
                t6_states["CYP3A4"].gene_expression = 11.2
            if "CYP3A4" in t12_states:
                t12_states["CYP3A4"].gene_expression = 12.0
            if "CYP3A4" in t24_states:
                t24_states["CYP3A4"].gene_expression = 10.6

            if "AKT1" in t6_states:
                t6_states["AKT1"].protein_activity = 0.82
            if "AKT1" in t12_states:
                t12_states["AKT1"].protein_activity = 0.70

            v.temporal_series = [
                TemporalObservation(timepoint=0.0, unit="hours", states=t0_states, active_edges_count=len(v.snapshot.edges)),
                TemporalObservation(timepoint=6.0, unit="hours", states=t6_states, active_edges_count=len(v.snapshot.edges)),
                TemporalObservation(timepoint=12.0, unit="hours", states=t12_states, active_edges_count=len(v.snapshot.edges)),
                TemporalObservation(timepoint=24.0, unit="hours", states=t24_states, active_edges_count=len(v.snapshot.edges))
            ]

            # Validate
            self.validator.validate_twin_version(twin, v.version_id)

            # Pre-create a candidate scenario branch (e.g. METTL3 Knockdown)
            self.scenario_manager.create_and_run_scenario(
                twin=twin,
                name="METTL3 Knockdown in Hepatocytes",
                intervention_type="KNOCKDOWN",
                target_entities=["METTL3"],
                strength=0.70,
                description="Simulated shRNA knockdown of m6A RNA methyltransferase METTL3."
            )

        self.registry.register_twin(twin)

    # 1. Create & Initialize
    def create_twin(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        twin = self.initializer.initialize_twin(
            name=payload.get("name", "New Digital Twin"),
            organism=payload.get("organism", "NCBI:9606"),
            tissue=payload.get("tissue", "liver"),
            cell_type=payload.get("cell_type", "hepatocyte"),
            condition=payload.get("condition", "healthy"),
            mode=payload.get("mode", "hybrid")
        )
        self.registry.register_twin(twin)
        return twin.to_dict()

    # 2. Get & List
    def list_twins(self) -> List[Dict[str, Any]]:
        return [t.to_dict() for t in self.registry.list_twins()]

    def get_twin(self, twin_id: str) -> Optional[Dict[str, Any]]:
        t = self.registry.get_twin(twin_id)
        return t.to_dict() if t else None

    def get_versions(self, twin_id: str) -> List[Dict[str, Any]]:
        t = self.registry.get_twin(twin_id)
        if not t:
            return []
        return [v.to_dict() for v in t.versions.values()]

    def get_molecular_state(self, twin_id: str, version_id: Optional[str] = None) -> Dict[str, Any]:
        t = self.registry.get_twin(twin_id)
        if not t:
            return {}
        v_id = version_id or t.active_version_id
        v = t.versions.get(v_id)
        if not v:
            return {}
        summary = self.state_manager.get_state_summary(v.states)
        return {
            "twin_id": twin_id,
            "version_id": v_id,
            "states": {k: s.to_dict() for k, s in v.states.items()},
            "summary": summary
        }

    def get_network(self, twin_id: str, version_id: Optional[str] = None) -> Dict[str, Any]:
        t = self.registry.get_twin(twin_id)
        if not t:
            return {}
        v_id = version_id or t.active_version_id
        v = t.versions.get(v_id)
        if not v or not v.snapshot:
            return {}
        return v.snapshot.to_dict()

    def get_timeline(self, twin_id: str, version_id: Optional[str] = None) -> List[Dict[str, Any]]:
        t = self.registry.get_twin(twin_id)
        if not t:
            return []
        v_id = version_id or t.active_version_id
        v = t.versions.get(v_id)
        if not v:
            return []
        return [t_obs.to_dict() for t_obs in v.temporal_series]

    def get_scenarios(self, twin_id: str, version_id: Optional[str] = None) -> List[Dict[str, Any]]:
        t = self.registry.get_twin(twin_id)
        if not t:
            return []
        v_id = version_id or t.active_version_id
        v = t.versions.get(v_id)
        if not v:
            return []
        return [s.to_dict() for s in v.scenarios]

    def get_validation(self, twin_id: str, version_id: Optional[str] = None) -> Dict[str, Any]:
        t = self.registry.get_twin(twin_id)
        if not t:
            return {}
        v_id = version_id or t.active_version_id
        v = t.versions.get(v_id)
        if not v or not v.validation_report:
            if v:
                rep = self.validator.validate_twin_version(t, v.version_id)
                return rep.to_dict()
            return {}
        return v.validation_report.to_dict()

    # 3. Operations
    def build_interactome(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        twin_id = payload.get("twin_id")
        twin = self.registry.get_twin(twin_id) if twin_id else None
        if not twin:
            twin = self.registry.list_twins()[0]
        v = twin.get_active_version()
        if not v or not v.snapshot:
            return {}
        snap = self.interactome_builder.build_context_interactome(
            twin_id=twin.twin_id,
            version_id=v.version_id,
            nodes=v.snapshot.nodes,
            candidate_edges=v.snapshot.edges,
            context=v.context
        )
        v.snapshot = snap
        return snap.to_dict()

    def integrate_omics(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        twin_id = payload.get("twin_id")
        twin = self.registry.get_twin(twin_id) if twin_id else None
        if not twin:
            twin = self.registry.list_twins()[0]
        v = twin.get_active_version()
        if not v:
            return {}

        obs_dicts = payload.get("observations", [])
        obs_objs: List[MolecularObservation] = []
        for d in obs_dicts:
            obs_objs.append(MolecularObservation(**d))

        updated_states = self.multiomics_integrator.integrate_observations(v.states, obs_objs)
        v.states = updated_states
        concordance = self.multiomics_integrator.compute_cross_modal_concordance(updated_states)
        return {
            "twin_id": twin.twin_id,
            "version_id": v.version_id,
            "integrated_count": len(obs_objs),
            "cross_modal_concordance": concordance
        }

    def update_twin(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        twin_id = payload.get("twin_id")
        twin = self.registry.get_twin(twin_id) if twin_id else None
        if not twin:
            twin = self.registry.list_twins()[0]

        obs_dicts = payload.get("observations", [])
        obs_objs = [MolecularObservation(**d) for d in obs_dicts]
        new_v = self.state_updater.update_twin_with_observations(
            twin=twin,
            new_observations=obs_objs,
            new_version_tag=payload.get("version_tag")
        )
        return new_v.to_dict()

    def estimate_state(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        twin_id = payload.get("twin_id")
        twin = self.registry.get_twin(twin_id) if twin_id else None
        if not twin:
            twin = self.registry.list_twins()[0]
        v = twin.get_active_version()
        if not v or not v.snapshot:
            return {}

        estimated = self.state_estimator.estimate_missing_states(v.states, v.snapshot.edges)
        v.states = estimated
        return {
            "twin_id": twin.twin_id,
            "version_id": v.version_id,
            "estimated_states": {k: s.to_dict() for k, s in estimated.items()}
        }

    def compare_twins(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        twin_id = payload.get("twin_id")
        twin = self.registry.get_twin(twin_id) if twin_id else None
        if not twin:
            twin = self.registry.list_twins()[0]

        v_base_id = payload.get("baseline_version_id")
        v_pert_id = payload.get("perturbed_version_id")

        v_base = twin.versions.get(v_base_id) if v_base_id else twin.get_active_version()
        v_pert = twin.versions.get(v_pert_id)

        # If perturbed version doesn't exist, create a disease context version for comparison
        if not v_pert:
            # Create an in-silico disease comparison state version
            disease_states = {k: MolecularState(**st.to_dict()) for k, st in v_base.states.items()}
            # Downregulate TP53, upregulate AKT1, downregulate CYP3A4
            if "TP53" in disease_states:
                disease_states["TP53"].gene_expression = 3.8
                disease_states["TP53"].protein_activity = -0.6
                disease_states["TP53"].cell_condition = "NASH/HCC"
            if "AKT1" in disease_states:
                disease_states["AKT1"].gene_expression = 9.4
                disease_states["AKT1"].protein_activity = 0.95
                disease_states["AKT1"].cell_condition = "NASH/HCC"
            if "CYP3A4" in disease_states:
                disease_states["CYP3A4"].gene_expression = 6.2
                disease_states["CYP3A4"].protein_activity = 0.20
                disease_states["CYP3A4"].cell_condition = "NASH/HCC"

            v_pert = TwinVersion(
                version_id="VER-DISEASE-COMP",
                version_tag="v1.1-NASH",
                twin_id=twin.twin_id,
                parent_version_id=v_base.version_id,
                context=v_base.context,
                snapshot=v_base.snapshot,
                states=disease_states
            )

        return self.comparator.compare_versions(v_base, v_pert)

    def temporal_analysis(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        twin_id = payload.get("twin_id")
        twin = self.registry.get_twin(twin_id) if twin_id else None
        if not twin:
            twin = self.registry.list_twins()[0]
        v = twin.get_active_version()
        if not v or not v.temporal_series:
            return {"change_points": [], "message": "No temporal series recorded."}

        change_points = self.change_detector.detect_change_points(v.temporal_series)
        return {
            "twin_id": twin.twin_id,
            "version_id": v.version_id,
            "timepoints_count": len(v.temporal_series),
            "change_points": change_points
        }

    def create_scenario(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        twin_id = payload.get("twin_id")
        twin = self.registry.get_twin(twin_id) if twin_id else None
        if not twin:
            twin = self.registry.list_twins()[0]

        scenario = self.scenario_manager.create_and_run_scenario(
            twin=twin,
            name=payload.get("name", "New Scenario"),
            intervention_type=payload.get("intervention_type", "KNOCKDOWN"),
            target_entities=payload.get("target_entities", ["TP53"]),
            strength=float(payload.get("strength", 1.0)),
            description=payload.get("description", "")
        )
        return scenario.to_dict()

    def validate_twin(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        twin_id = payload.get("twin_id")
        twin = self.registry.get_twin(twin_id) if twin_id else None
        if not twin:
            twin = self.registry.list_twins()[0]
        rep = self.validator.validate_twin_version(twin, payload.get("version_id"))
        return rep.to_dict()

    def run_benchmarks(self) -> Dict[str, Any]:
        return self.benchmark_suite.run_all_benchmarks()
