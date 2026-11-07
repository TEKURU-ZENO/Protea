"""
PROTEA Phase 10: Mutation & Therapeutic Intelligence Engine (MTIE)
From molecular variation to therapeutic discovery intelligence.
"""

from ai.mutation_therapeutics.schema import (
    GenomicVariant,
    TranscriptVariant,
    ProteinMutation,
    MutantProtein,
    StructuralEffect,
    FunctionalEffect,
    InteractionRewiring,
    DiseaseMechanism,
    TherapeuticTarget,
    DrugCandidate,
    BindingEvidence,
    DrugTargetEvidence,
    DrugResponse,
    ResistanceMechanism,
    CombinationTherapy,
    TherapeuticScenario,
    TherapeuticValidationReport,
    MutationType,
    FunctionalClass,
    StabilityClass,
    ACMGClass,
    TractabilityTier
)

from ai.mutation_therapeutics.variant import (
    VariantParser,
    VariantNormalizer,
    VariantAnnotator
)

from ai.mutation_therapeutics.effect_prediction import (
    MissenseScorer,
    DomainDisruptionAnalyzer,
    FunctionalClassifier,
    EnsembleEffectPredictor
)

from ai.mutation_therapeutics.structure import (
    StructureFetcher,
    MutantModeler,
    InterfaceAnalyzer,
    StructuralConfidenceEvaluator
)

from ai.mutation_therapeutics.stability import (
    FoldingStabilityPredictor,
    AggregationAnalyzer,
    AllostericPerturbationEngine
)

from ai.mutation_therapeutics.interaction_rewiring import (
    PPIInterfaceDisruptionAnalyzer,
    RewiringPredictor,
    MutantInteractomeGraphBuilder
)

from ai.mutation_therapeutics.disease_mechanisms import (
    PathwayDisruptionAnalyzer,
    CausalDiseaseTracer,
    CompensatoryBypassDetector
)

from ai.mutation_therapeutics.target_discovery import (
    DruggabilityAnalyzer,
    TargetPrioritizer
)

from ai.mutation_therapeutics.drug_intelligence import (
    DrugRetriever,
    DockingEngine,
    SelectivityAnalyzer
)

from ai.mutation_therapeutics.resistance import (
    ResistancePredictor,
    DoseResponseModel
)

from ai.mutation_therapeutics.combination_therapy import (
    SynergyCalculator,
    CombinationRanker
)

from ai.mutation_therapeutics.simulation import (
    TherapeuticSimulator,
    MultiObjectiveTherapeuticOptimizer
)

from ai.mutation_therapeutics.validation import (
    ACMGClassifier,
    EvidenceAggregator,
    UncertaintyReporter
)

from ai.mutation_therapeutics.evaluation.benchmarks import MTIEBenchmarkSuite

__version__ = "1.0.0"

__all__ = [
    # Schemas
    "GenomicVariant",
    "TranscriptVariant",
    "ProteinMutation",
    "MutantProtein",
    "StructuralEffect",
    "FunctionalEffect",
    "InteractionRewiring",
    "DiseaseMechanism",
    "TherapeuticTarget",
    "DrugCandidate",
    "BindingEvidence",
    "DrugTargetEvidence",
    "DrugResponse",
    "ResistanceMechanism",
    "CombinationTherapy",
    "TherapeuticScenario",
    "TherapeuticValidationReport",
    "MutationType",
    "FunctionalClass",
    "StabilityClass",
    "ACMGClass",
    "TractabilityTier",
    # Modules
    "VariantParser",
    "VariantNormalizer",
    "VariantAnnotator",
    "MissenseScorer",
    "DomainDisruptionAnalyzer",
    "FunctionalClassifier",
    "EnsembleEffectPredictor",
    "StructureFetcher",
    "MutantModeler",
    "InterfaceAnalyzer",
    "StructuralConfidenceEvaluator",
    "FoldingStabilityPredictor",
    "AggregationAnalyzer",
    "AllostericPerturbationEngine",
    "PPIInterfaceDisruptionAnalyzer",
    "RewiringPredictor",
    "MutantInteractomeGraphBuilder",
    "PathwayDisruptionAnalyzer",
    "CausalDiseaseTracer",
    "CompensatoryBypassDetector",
    "DruggabilityAnalyzer",
    "TargetPrioritizer",
    "DrugRetriever",
    "DockingEngine",
    "SelectivityAnalyzer",
    "ResistancePredictor",
    "DoseResponseModel",
    "SynergyCalculator",
    "CombinationRanker",
    "TherapeuticSimulator",
    "MultiObjectiveTherapeuticOptimizer",
    "ACMGClassifier",
    "EvidenceAggregator",
    "UncertaintyReporter",
    "MTIEBenchmarkSuite"
]
