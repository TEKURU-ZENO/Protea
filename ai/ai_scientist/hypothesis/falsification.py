"""Falsification protocol definitions and rejection standards."""

from typing import Any, Dict, List
from ai.ai_scientist.schema import ResearchHypothesis


class FalsificationEngine:
    """Manages Karl Popper-style falsification standards for biological hypotheses."""

    @staticmethod
    def evaluate_falsification(
        hypothesis: ResearchHypothesis,
        experimental_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Test whether experimental observations violate falsification criteria."""
        criteria_results = []
        is_falsified = False

        deltas = experimental_data.get("species_deltas", {})
        final_change = deltas.get("ERK_star", {}).get("delta", 0.0)

        # Check if intervention failed to show expected attenuation
        if abs(final_change) < 1e-4:
            is_falsified = True
            criteria_results.append({
                "criterion": hypothesis.falsification_criteria[0] if hypothesis.falsification_criteria else "No effect observed",
                "triggered": True,
                "evidence": f"ERK_star delta was {final_change:.4f}, indicating absence of functional response.",
            })
        else:
            criteria_results.append({
                "criterion": hypothesis.falsification_criteria[0] if hypothesis.falsification_criteria else "Observable response required",
                "triggered": False,
                "evidence": f"Functional response detected: delta = {final_change:.4f}",
            })

        status = "FALSIFIED" if is_falsified else "SURVIVED"

        return {
            "hypothesis_id": hypothesis.hypothesis_id,
            "status": status,
            "criteria_tested": criteria_results,
            "is_falsified": is_falsified,
        }

    @classmethod
    def evaluate_hypothesis(
        cls,
        hypothesis: Any,
        observed_outcomes: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Evaluates hypothesis against observed statistical outcomes and directionality."""
        p_val = observed_outcomes.get("p_value", 1.0)
        eff_size = observed_outcomes.get("effect_size", 0.0)
        direction_consistent = observed_outcomes.get("direction_consistent", True)

        is_falsified = (p_val > 0.05) or (abs(eff_size) < 0.2) or (not direction_consistent)
        status = "FALSIFIED" if is_falsified else "SURVIVED_FALSIFICATION"

        return {
            "hypothesis_id": getattr(hypothesis, "hypothesis_id", "HYP_01"),
            "status": status,
            "is_falsified": is_falsified,
            "falsification_tested": True,
        }


FalsificationEvaluator = FalsificationEngine

