"""Experimental prediction generator translating hypotheses into observable endpoints."""

from typing import Any, Dict, List
from ai.ai_scientist.schema import ResearchHypothesis


class PredictionGenerator:
    """Derives precise, testable quantitative predictions from biological hypotheses."""

    @staticmethod
    def derive_predictions(hypothesis: ResearchHypothesis) -> List[Dict[str, Any]]:
        """Formulate explicit mathematical and observational predictions."""
        predictions = []
        for idx, text in enumerate(hypothesis.testable_predictions):
            predictions.append({
                "prediction_id": f"{hypothesis.hypothesis_id}-P{idx+1}",
                "description": text,
                "target_observable": hypothesis.experimental_plan.get("outcome_observables", ["ERK_star"])[0],
                "expected_direction": "DECREASE" if "inhib" in text.lower() or "prevent" in text.lower() else "INCREASE",
                "minimum_detectable_effect": 0.30, # 30% fold change threshold
                "verification_metric": "relative_concentration_change",
            })
        return predictions

    @classmethod
    def generate_predictions(cls, hypothesis: ResearchHypothesis) -> List[Any]:
        """Convenience alias for derive_predictions."""
        return cls.derive_predictions(hypothesis)

