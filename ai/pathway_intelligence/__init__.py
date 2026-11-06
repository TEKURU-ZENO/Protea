"""
PROTEA Pathway Intelligence Engine (PaIE) Package
Global entrypoint for pathway ingestion, community discovery, enrichment, prediction, causal reasoning, and explainability.
"""

from ai.pathway_intelligence.registry import paie_registry
from ai.pathway_intelligence.ingestion import (
    ReactomeAdapter,
    KEGGAdapter,
    WikiPathwaysAdapter,
    PathwayCommonsAdapter
)
from ai.pathway_intelligence.annotation import (
    go_engine,
    annotation_manager,
    localization_mapper
)
from ai.pathway_intelligence.enrichment import (
    ORAEngine,
    GSEAEngine,
    GSVAEngine,
    benjamini_hochberg,
    bonferroni
)
from ai.pathway_intelligence.discovery import (
    LouvainDetector,
    LeidenDetector,
    MarkovClusterAlgorithm,
    WCCDetector,
    SubgraphMiner,
    MotifDiscoveryEngine,
    DeNovoPathwayDiscoveryEngine
)
from ai.pathway_intelligence.prediction import (
    PathwayMembershipPredictor,
    PathwayReconstructor,
    PathwayEmbeddingAggregator
)
from ai.pathway_intelligence.causal import (
    RegulatoryReasoningEngine,
    NetworkPropagationEngine,
    SignalingCascadeTracer,
    ReverseCausalReasoning
)
from ai.pathway_intelligence.evolution import (
    CrossSpeciesOrthologMapper,
    PathwayEvolutionAnalyzer
)
from ai.pathway_intelligence.explainability import (
    EvidenceAggregator,
    ScientificExplanationGenerator
)

__all__ = [
    "paie_registry",
    "ReactomeAdapter",
    "KEGGAdapter",
    "WikiPathwaysAdapter",
    "PathwayCommonsAdapter",
    "go_engine",
    "annotation_manager",
    "localization_mapper",
    "ORAEngine",
    "GSEAEngine",
    "GSVAEngine",
    "benjamini_hochberg",
    "bonferroni",
    "LouvainDetector",
    "LeidenDetector",
    "MarkovClusterAlgorithm",
    "WCCDetector",
    "SubgraphMiner",
    "MotifDiscoveryEngine",
    "DeNovoPathwayDiscoveryEngine",
    "PathwayMembershipPredictor",
    "PathwayReconstructor",
    "PathwayEmbeddingAggregator",
    "RegulatoryReasoningEngine",
    "NetworkPropagationEngine",
    "SignalingCascadeTracer",
    "ReverseCausalReasoning",
    "CrossSpeciesOrthologMapper",
    "PathwayEvolutionAnalyzer",
    "EvidenceAggregator",
    "ScientificExplanationGenerator"
]
