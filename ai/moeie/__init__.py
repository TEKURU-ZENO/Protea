"""
PROTEA Phase 11: Multi-Omics & Evolution Intelligence Engine (MOEIE)
Unified biological systems intelligence across molecular modalities, cell contexts, and evolutionary history.
"""

from ai.moeie.schema import (
    OmicsModality,
    ConservationTier,
    EvidenceProvenance,
    CanonicalIdentityRecord,
    OmicsDataset,
    BiologicalSample,
    OmicsMeasurement,
    MolecularFeature,
    CellPopulation,
    SpatialRegion,
    MolecularProgram,
    LatentRepresentation,
    OrthologGroup,
    ProteinFamily,
    PhylogeneticTree,
    EvolutionaryEvent,
    ConservedInteraction,
    EvolutionaryModule,
    ComparativeAnalysis,
    EvolutionaryHypothesis
)

from ai.moeie.ingestion import (
    ModalityIngestionAdapters,
    CrossSpeciesIdentifierResolver,
    CURATED_ID_MAP,
    DatasetRegistry
)

from ai.moeie.preprocessing import (
    MultiOmicsNormalizer,
    QualityControlEngine
)

from ai.moeie.representation import (
    SharedPrivateLatentModel,
    CrossModalAligner
)

from ai.moeie.cellular import (
    CellAnnotationEngine,
    REFERENCE_CELL_MARKERS,
    TrajectoryEngine,
    CellCommunicationEngine,
    CURATED_LR_PAIRS
)

from ai.moeie.spatial import (
    SpatialGraphEngine,
    SpatialProgramEngine
)

from ai.moeie.regulatory import (
    TFActivityInferenceEngine,
    CURATED_TF_REGULONS,
    GRNReconstructionEngine,
    ProteinRNADiscordanceAnalyzer
)

from ai.moeie.evolution import (
    OrthologyInferenceEngine,
    CURATED_ORTHOLOG_GROUPS,
    SequenceConservationEngine,
    PhylogeneticEngine
)

from ai.moeie.evolutionary_interactome import (
    CrossSpeciesMappingEngine,
    CONSERVED_INTERACTION_CATALOG,
    NetworkAlignmentEngine,
    CoverageUncertaintyEstimator,
    SPECIES_DATABASE_COVERAGE
)

from ai.moeie.prediction import (
    EvolutionPPITransferEngine,
    EvolutionMutationPredictor
)

from ai.moeie.systems import (
    PathwayEvolutionEngine
)

from ai.moeie.therapeutics import (
    EvolutionaryTherapeuticPrioritizer
)

from ai.moeie.validation import (
    ScientificLeakageGuard,
    ProvenanceTracker
)

from ai.moeie.evaluation.benchmarks import MOEIEBenchmarkSuite

__version__ = "1.0.0"

__all__ = [
    # Schemas
    "OmicsModality",
    "ConservationTier",
    "EvidenceProvenance",
    "CanonicalIdentityRecord",
    "OmicsDataset",
    "BiologicalSample",
    "OmicsMeasurement",
    "MolecularFeature",
    "CellPopulation",
    "SpatialRegion",
    "MolecularProgram",
    "LatentRepresentation",
    "OrthologGroup",
    "ProteinFamily",
    "PhylogeneticTree",
    "EvolutionaryEvent",
    "ConservedInteraction",
    "EvolutionaryModule",
    "ComparativeAnalysis",
    "EvolutionaryHypothesis",
    # Modules
    "ModalityIngestionAdapters",
    "CrossSpeciesIdentifierResolver",
    "CURATED_ID_MAP",
    "DatasetRegistry",
    "MultiOmicsNormalizer",
    "QualityControlEngine",
    "SharedPrivateLatentModel",
    "CrossModalAligner",
    "CellAnnotationEngine",
    "REFERENCE_CELL_MARKERS",
    "TrajectoryEngine",
    "CellCommunicationEngine",
    "CURATED_LR_PAIRS",
    "SpatialGraphEngine",
    "SpatialProgramEngine",
    "TFActivityInferenceEngine",
    "CURATED_TF_REGULONS",
    "GRNReconstructionEngine",
    "ProteinRNADiscordanceAnalyzer",
    "OrthologyInferenceEngine",
    "CURATED_ORTHOLOG_GROUPS",
    "SequenceConservationEngine",
    "PhylogeneticEngine",
    "CrossSpeciesMappingEngine",
    "CONSERVED_INTERACTION_CATALOG",
    "NetworkAlignmentEngine",
    "CoverageUncertaintyEstimator",
    "SPECIES_DATABASE_COVERAGE",
    "EvolutionPPITransferEngine",
    "EvolutionMutationPredictor",
    "PathwayEvolutionEngine",
    "EvolutionaryTherapeuticPrioritizer",
    "ScientificLeakageGuard",
    "ProvenanceTracker",
    "MOEIEBenchmarkSuite"
]
