"""Intermediate and final experimental result aggregator."""

from typing import Any, Dict, List
from ai.ai_scientist.schema import ExperimentExecutionRecord


class ResultCollector:
    """Aggregates raw execution records across replicates into statistical summary matrices."""

    @staticmethod
    def aggregate_replicate_results(
        records: List[ExperimentExecutionRecord],
        observable: str = "ERK_star",
    ) -> Dict[str, Any]:
        """Extract baseline vs treated values across all replicates."""
        wild_type_vals = []
        perturbed_vals = []

        for rec in records:
            deltas = rec.raw_results.get("species_deltas", {})
            if observable in deltas:
                wild_type_vals.append(float(deltas[observable]["wild_type_final"]))
                perturbed_vals.append(float(deltas[observable]["perturbed_final"]))

        return {
            "observable": observable,
            "replicate_count": len(records),
            "wild_type_values": wild_type_vals,
            "perturbed_values": perturbed_vals,
            "mean_wild_type": sum(wild_type_vals) / max(1, len(wild_type_vals)),
            "mean_perturbed": sum(perturbed_vals) / max(1, len(perturbed_vals)),
        }
