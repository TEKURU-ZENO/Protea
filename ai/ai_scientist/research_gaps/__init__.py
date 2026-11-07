"""Research Gaps and Novelty Intelligence Engine."""

from ai.ai_scientist.research_gaps.gap_detector import ResearchGapDetector
from ai.ai_scientist.research_gaps.novelty_auditor import NoveltyAuditor
from ai.ai_scientist.research_gaps.literature_coverage import LiteratureCoverageAnalyzer
from ai.ai_scientist.research_gaps.opportunity_ranker import OpportunityRanker

__all__ = [
    "ResearchGapDetector",
    "NoveltyAuditor",
    "LiteratureCoverageAnalyzer",
    "OpportunityRanker",
]
