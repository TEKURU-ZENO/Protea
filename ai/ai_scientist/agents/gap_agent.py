"""
PROTEA AI Scientist - Research Gap Agent
Identifies literature gaps, evaluates opportunity potential, and audits prior art novelty.
"""

from typing import Dict, Any, List
from ai.ai_scientist.research_gaps.gap_detector import GapDetector
from ai.ai_scientist.research_gaps.novelty_auditor import NoveltyAuditor
from ai.ai_scientist.research_gaps.opportunity_ranker import OpportunityRanker


class GapAgent:
    """
    Identifies white spaces, contradictions, and under-investigated questions in biological knowledge.
    """

    def __init__(self):
        self.gap_detector = GapDetector()
        self.novelty_auditor = NoveltyAuditor()
        self.opportunity_ranker = OpportunityRanker()

    def run(
        self,
        claims: List[Any],
        entities: List[str],
        prior_art_publications: List[Any],
    ) -> Dict[str, Any]:
        """
        Executes gap detection and novelty auditing.
        """
        gaps = self.gap_detector.detect_gaps(claims, entities)
        ranked_gaps = self.opportunity_ranker.rank_gaps(gaps)

        # Audit top gap for prior art
        novelty_audits = []
        for g in ranked_gaps[:3]:
            audit = self.novelty_auditor.audit_novelty(
                proposed_discovery=g.description,
                retrieved_publications=prior_art_publications,
            )
            novelty_audits.append({"gap_id": g.gap_id, "audit": audit})

        return {
            "gaps": [g.dict() if hasattr(g, "dict") else g for g in ranked_gaps],
            "total_gaps": len(ranked_gaps),
            "novelty_audits": novelty_audits,
            "top_gap": ranked_gaps[0].dict() if ranked_gaps and hasattr(ranked_gaps[0], "dict") else (ranked_gaps[0] if ranked_gaps else None),
        }
