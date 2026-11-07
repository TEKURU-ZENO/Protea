"""Multi-criteria hypothesis prioritization framework."""

from typing import Any, Dict, List
from ai.ai_scientist.schema import ResearchHypothesis


class HypothesisRanker:
    """Prioritizes hypotheses across independent, auditable scientific criteria."""

    DEFAULT_WEIGHTS = {
        "evidence_strength": 0.25,
        "biological_plausibility": 0.25,
        "testability": 0.20,
        "novelty": 0.15,
        "uncertainty_penalty": 0.15,
    }

    @classmethod
    def rank_hypotheses(
        cls,
        hypotheses: List[ResearchHypothesis],
        weights: Dict[str, float] = None,
    ) -> List[ResearchHypothesis]:
        """Rank hypotheses by weighted multi-criteria score."""
        w = weights or cls.DEFAULT_WEIGHTS

        def compute_score(h: ResearchHypothesis) -> float:
            scores = h.priority_scores
            ev = scores.get("evidence_strength", 0.5)
            pl = scores.get("biological_plausibility", 0.5)
            test = scores.get("testability", 0.5)
            nov = scores.get("novelty", 0.5)
            unc = scores.get("uncertainty_penalty", 0.2)

            composite = (
                w.get("evidence_strength", 0.25) * ev +
                w.get("biological_plausibility", 0.25) * pl +
                w.get("testability", 0.20) * test +
                w.get("novelty", 0.15) * nov -
                w.get("uncertainty_penalty", 0.15) * unc
            )
            return round(composite, 4)

        for h in hypotheses:
            score = compute_score(h)
            h.priority_scores["composite_priority"] = score
            h.composite_score = score

        return sorted(hypotheses, key=lambda x: getattr(x, "composite_score", x.priority_scores.get("composite_priority", 0.0)), reverse=True)
