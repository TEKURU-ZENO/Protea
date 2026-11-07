"""
PROTEA Phase 9: AI Scientist (Autonomous Biological Discovery Engine - ABDE)
Autonomous research intelligence capable of conducting end-to-end evidence-grounded scientific investigations.
"""

from ai.ai_scientist.schema import (
    ResearchInvestigation,
    ResearchState,
    ClaimStatus,
    GapType,
    PublicationRecord,
    ScientificClaim,
    ResearchGap,
    ResearchHypothesis,
    ExperimentPlan,
    ExperimentExecutionRecord,
    StatisticalAnalysisReport,
    AdversarialAuditReport,
    ScientificManuscript,
    ReproducibilityPackage,
)
from ai.ai_scientist.agents.orchestrator import PrincipalResearchOrchestrator
from ai.ai_scientist.evaluation.benchmarks import ScientificDiscoveryBenchmarkSuite

__version__ = "1.0.0-phase9"

__all__ = [
    "ResearchInvestigation",
    "ResearchState",
    "ClaimStatus",
    "GapType",
    "PublicationRecord",
    "ScientificClaim",
    "ResearchGap",
    "ResearchHypothesis",
    "ExperimentPlan",
    "ExperimentExecutionRecord",
    "StatisticalAnalysisReport",
    "AdversarialAuditReport",
    "ScientificManuscript",
    "ReproducibilityPackage",
    "PrincipalResearchOrchestrator",
    "ScientificDiscoveryBenchmarkSuite",
]
