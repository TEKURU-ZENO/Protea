"""
PROTEA Biological Reasoning Engine (BRE) Package
Unified evidence-grounded scientific reasoning, multi-hop mechanisms, competing hypotheses, and counterfactual simulation.
"""

from ai.biological_reasoning.schema import (
    EvidenceStatus,
    BiologicalCertainty,
    RelationshipType,
    BiologicalEvidence,
    BiologicalQuestion,
    MolecularMechanismStep,
    MolecularMechanism,
    Hypothesis,
    PerturbationScenario,
    ReasoningTraceStep,
    ReasoningReport
)
from ai.biological_reasoning.registry import bre_registry
from ai.biological_reasoning.query import (
    BiologicalEntityResolver,
    BiologicalQuestionParser,
    BiologicalQueryPlanner
)
from ai.biological_reasoning.retrieval import HybridEvidenceRetriever
from ai.biological_reasoning.mechanistic import MechanisticReasoningEngine
from ai.biological_reasoning.graph_reasoning import BiologicalGraphReasoningEngine
from ai.biological_reasoning.hypothesis import (
    HypothesisGenerationEngine,
    HypothesisRankingEngine
)
from ai.biological_reasoning.evidence import (
    EvidenceFusionEngine,
    ContradictionResolutionEngine,
    SOURCE_RELIABILITY_WEIGHTS
)
from ai.biological_reasoning.counterfactual import CounterfactualReasoningEngine
from ai.biological_reasoning.uncertainty import (
    calculate_brier_score,
    calculate_expected_calibration_error,
    UncertaintyEstimator
)
from ai.biological_reasoning.validation import BiologicalConstraintValidator
from ai.biological_reasoning.explanation import ScientificReportGenerator
from ai.biological_reasoning.agents import MultiAgentReasoningOrchestrator, orchestrator

__all__ = [
    "EvidenceStatus",
    "BiologicalCertainty",
    "RelationshipType",
    "BiologicalEvidence",
    "BiologicalQuestion",
    "MolecularMechanismStep",
    "MolecularMechanism",
    "Hypothesis",
    "PerturbationScenario",
    "ReasoningTraceStep",
    "ReasoningReport",
    "bre_registry",
    "BiologicalEntityResolver",
    "BiologicalQuestionParser",
    "BiologicalQueryPlanner",
    "HybridEvidenceRetriever",
    "MechanisticReasoningEngine",
    "BiologicalGraphReasoningEngine",
    "HypothesisGenerationEngine",
    "HypothesisRankingEngine",
    "EvidenceFusionEngine",
    "ContradictionResolutionEngine",
    "SOURCE_RELIABILITY_WEIGHTS",
    "CounterfactualReasoningEngine",
    "calculate_brier_score",
    "calculate_expected_calibration_error",
    "UncertaintyEstimator",
    "BiologicalConstraintValidator",
    "ScientificReportGenerator",
    "MultiAgentReasoningOrchestrator",
    "orchestrator"
]
