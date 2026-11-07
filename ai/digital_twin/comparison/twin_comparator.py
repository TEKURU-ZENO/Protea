"""Digital Twin Comparator coordinator."""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from ai.digital_twin.comparison.differential_state import DifferentialStateAnalyzer
from ai.digital_twin.comparison.network_rewiring import NetworkRewiringAnalyzer
from ai.digital_twin.schema import DigitalTwin, TwinVersion

logger = logging.getLogger(__name__)


class DigitalTwinComparator:
    """Performs comparative systems biology analysis between two twin versions or conditions."""

    def __init__(self) -> None:
        self.state_analyzer = DifferentialStateAnalyzer()
        self.rewiring_analyzer = NetworkRewiringAnalyzer()

    def compare_versions(
        self,
        baseline_version: TwinVersion,
        perturbed_version: TwinVersion
    ) -> Dict[str, Any]:
        """Compares baseline vs perturbed versions across network wiring and molecular states."""
        # 1. Molecular state differentials
        state_diff = self.state_analyzer.compute_differential_states(
            baseline_states=baseline_version.states,
            perturbed_states=perturbed_version.states
        )

        # 2. Network rewiring
        rewiring: Dict[str, Any] = {}
        if baseline_version.snapshot and perturbed_version.snapshot:
            rewiring = self.rewiring_analyzer.analyze_rewiring(
                snapshot_baseline=baseline_version.snapshot,
                snapshot_perturbed=perturbed_version.snapshot
            )

        summary_narrative = (
            f"Comparison between '{baseline_version.context.condition}' ({baseline_version.version_tag}) "
            f"and '{perturbed_version.context.condition}' ({perturbed_version.version_tag}): "
            f"{state_diff['significant_count']} significantly altered genes/proteins detected "
            f"({state_diff['upregulated_count']} UP, {state_diff['downregulated_count']} DOWN). "
            f"Network rewiring indicates {len(rewiring.get('gained_edges', []))} gained interactions and "
            f"{len(rewiring.get('lost_edges', []))} lost interactions."
        )

        return {
            "baseline_version": baseline_version.version_tag,
            "perturbed_version": perturbed_version.version_tag,
            "baseline_condition": baseline_version.context.condition,
            "perturbed_condition": perturbed_version.context.condition,
            "differential_state": state_diff,
            "network_rewiring": rewiring,
            "summary_narrative": summary_narrative
        }
