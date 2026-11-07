"""
PROTEA AI Scientist - Falsification Criteria Review
Formally evaluates experimental outcomes against pre-registered Popperian falsification criteria.
"""

from typing import Dict, Any, List


class FalsificationReviewer:
    """
    Evaluates whether an experiment has falsified or failed to falsify the target hypothesis.
    In accordance with Popperian epistemology:
    - Evidence cannot 'prove' a hypothesis definitively; it can only withstand falsification tests.
    - If any strict falsification criterion is met, the hypothesis is FALSIFIED.
    """

    def review_falsification(
        self,
        falsification_criteria: List[str],
        observed_outcomes: Dict[str, Any],
        statistical_significance: bool,
    ) -> Dict[str, Any]:
        """
        Evaluates observed results against registered falsification criteria.
        """
        triggered_falsifications = []
        criteria_evaluations = []

        effect_size = observed_outcomes.get("effect_size", 0.0)
        p_val = observed_outcomes.get("p_val", observed_outcomes.get("p_value", 1.0))
        direction_consistent = observed_outcomes.get("direction_consistent", True)

        for crit in falsification_criteria:
            crit_lower = crit.lower()
            triggered = False

            # Check directional failure
            if "opposite direction" in crit_lower and not direction_consistent:
                triggered = True
            # Check null effect
            elif "no significant" in crit_lower and (not statistical_significance or abs(effect_size) < 0.2):
                triggered = True
            # Check p-value threshold
            elif "p >" in crit_lower and p_val > 0.05:
                triggered = True

            criteria_evaluations.append({
                "criterion": crit,
                "triggered": triggered,
            })

            if triggered:
                triggered_falsifications.append(crit)

        is_falsified = len(triggered_falsifications) > 0

        status = "FALSIFIED" if is_falsified else "SURVIVED_FALSIFICATION"
        summary = (
            f"Hypothesis was FALSIFIED by {len(triggered_falsifications)} registered criteria."
            if is_falsified
            else "Hypothesis survived all pre-registered falsification tests with statistical rigor."
        )

        return {
            "status": status,
            "is_falsified": is_falsified,
            "total_criteria": len(falsification_criteria),
            "triggered_count": len(triggered_falsifications),
            "criteria_evaluations": criteria_evaluations,
            "triggered_falsifications": triggered_falsifications,
            "summary": summary,
        }
