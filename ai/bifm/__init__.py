"""
PROTEA Phase 12: Biological Intelligence Foundation Model (BIFM)
The unified intelligence layer for the protein and biological universe.
"""

from ai.bifm.schema import (
    ModalityType,
    BiologicalDomain,
    EvidenceLevel,
    BiologicalContext,
    BiologicalRepresentation,
    MultiModalProfile,
    TaskPrediction,
    WorldModelState,
    InterventionSpec,
    CounterfactualResult,
    StructuredExplanation,
    ModelCardRecord
)
from ai.bifm.representations.canonical import UniversalRepresentationRegistry
from ai.bifm.encoders.adapters import (
    BiologicalEncoder,
    SequenceEncoderAdapter,
    StructureEncoderAdapter,
    InteractionEncoderAdapter,
    PathwayEncoderAdapter,
    OmicsEncoderAdapter,
    CellularEncoderAdapter,
    SpatialEncoderAdapter,
    EvolutionEncoderAdapter,
    LiteratureEncoderAdapter
)
from ai.bifm.fusion.cross_modal_fusion import CrossModalFusionEngine
from ai.bifm.knowledge.grounding_engine import BiologicalKnowledgeGroundingEngine
from ai.bifm.prediction.multitask_engine import BiologicalMultiTaskEngine
from ai.bifm.context.conditional_engine import BiologicalContextEngine
from ai.bifm.world_model.state_transition import BiologicalWorldModel
from ai.bifm.counterfactuals.intervention_engine import CounterfactualIntelligenceEngine
from ai.bifm.reasoning.scientific_reasoning import UnifiedBiologicalReasoningEngine
from ai.bifm.research.autonomous_orchestrator import AutonomousResearchInterface
from ai.bifm.continual.adapter_manager import ContinualLearningEngine
from ai.bifm.governance.model_cards import FoundationModelGovernance
from ai.bifm.evaluation.benchmarks import BIFMBenchmarkSuite

__version__ = "1.0.0"

__all__ = [
    "ModalityType",
    "BiologicalDomain",
    "EvidenceLevel",
    "BiologicalContext",
    "BiologicalRepresentation",
    "MultiModalProfile",
    "TaskPrediction",
    "WorldModelState",
    "InterventionSpec",
    "CounterfactualResult",
    "StructuredExplanation",
    "ModelCardRecord",
    "UniversalRepresentationRegistry",
    "BiologicalEncoder",
    "SequenceEncoderAdapter",
    "StructureEncoderAdapter",
    "InteractionEncoderAdapter",
    "PathwayEncoderAdapter",
    "OmicsEncoderAdapter",
    "CellularEncoderAdapter",
    "SpatialEncoderAdapter",
    "EvolutionEncoderAdapter",
    "LiteratureEncoderAdapter",
    "CrossModalFusionEngine",
    "BiologicalKnowledgeGroundingEngine",
    "BiologicalMultiTaskEngine",
    "BiologicalContextEngine",
    "BiologicalWorldModel",
    "CounterfactualIntelligenceEngine",
    "UnifiedBiologicalReasoningEngine",
    "AutonomousResearchInterface",
    "ContinualLearningEngine",
    "FoundationModelGovernance",
    "BIFMBenchmarkSuite"
]
