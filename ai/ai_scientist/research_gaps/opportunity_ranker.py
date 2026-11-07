"""Scientific discovery opportunity ranker."""

from typing import Any, Dict, List
from ai.ai_scientist.schema import ResearchGap


class OpportunityRanker:
    """Prioritizes research gaps using multi-objective scientific criteria."""

    @staticmethod
    def rank_gaps(gaps: List[ResearchGap]) -> List[ResearchGap]:
        """Rank gaps by evidence deficiency, biological importance, and feasibility."""
        def score_gap(gap: ResearchGap) -> float:
            # Lower evidence density = higher discovery potential (inverted)
            novelty_factor = 1.0 - gap.evidence_density
            base_priority = gap.priority_score
            return 0.6 * base_priority + 0.4 * novelty_factor

        sorted_gaps = sorted(gaps, key=score_gap, reverse=True)
        return sorted_gaps
