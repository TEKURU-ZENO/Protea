"""Scenario Manager lifecycle coordinator."""

from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from ai.digital_twin.scenarios.perturbation_overlay import PerturbationOverlayEngine
from ai.digital_twin.scenarios.scenario_comparison import ScenarioDeltaVisualizer
from ai.digital_twin.schema import DigitalTwin, ScenarioResult, TwinScenario, TwinVersion

logger = logging.getLogger(__name__)


class ScenarioManager:
    """Manages creation, execution, and branching of isolated in silico scenario experiments."""

    def __init__(self) -> None:
        self.overlay_engine = PerturbationOverlayEngine()
        self.delta_visualizer = ScenarioDeltaVisualizer()

    def create_and_run_scenario(
        self,
        twin: DigitalTwin,
        name: str,
        intervention_type: str,
        target_entities: List[str],
        strength: float = 1.0,
        description: str = "",
        target_version_id: Optional[str] = None
    ) -> TwinScenario:
        """Executes an intervention on the target version without modifying its observed states."""
        version_id = target_version_id or twin.active_version_id
        version = twin.versions.get(version_id)
        if not version or not version.snapshot:
            raise ValueError(f"Target version {version_id} not found or missing interactome snapshot.")

        scenario_id = f"SCN-{twin.twin_id}-{str(uuid.uuid4())[:6].upper()}"

        # 1. Run simulation overlay
        result: ScenarioResult = self.overlay_engine.simulate_intervention(
            scenario_id=scenario_id,
            parent_version_id=version_id,
            baseline_states=version.states,
            snapshot=version.snapshot,
            intervention_type=intervention_type,
            target_entities=target_entities,
            strength=strength
        )

        scenario = TwinScenario(
            scenario_id=scenario_id,
            twin_id=twin.twin_id,
            parent_version_id=version_id,
            name=name,
            description=description or f"{intervention_type} on {', '.join(target_entities)}",
            target_entities=target_entities,
            intervention_type=intervention_type,
            strength=strength,
            result=result,
            created_at=datetime.utcnow().isoformat()
        )

        # Store under the version's scenario list
        version.scenarios.append(scenario)
        logger.info(f"Created scenario {scenario_id} ({name}) on twin {twin.twin_id} version {version_id}.")
        return scenario
