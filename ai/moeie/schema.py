"""
PROTEA Phase 11: Multi-Omics & Evolution Intelligence Engine (MOEIE)
Unified Biological Data Architecture and Canonical Domain Entities
"""

from __future__ import annotations
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Dict, List, Any, Optional, Tuple
import uuid
import datetime


class OmicsModality(str, Enum):
    GENOMICS = "genomics"
    TRANSCRIPTOMICS = "transcriptomics"
    PROTEOMICS = "proteomics"
    PHOSPHOPROTEOMICS = "phosphoproteomics"
    EPIGENOMICS = "epigenomics"
    METABOLOMICS = "metabolomics"
    SINGLE_CELL = "single_cell"
    SPATIAL = "spatial"
    MULTIOMICS = "multiomics"


class ConservationTier(str, Enum):
    ULTRACONSERVED = "ultraconserved"         # Across Eukaryota / deep Metazoa
    VERTEBRATE_CONSERVED = "vertebrate_conserved" # Conserved across Vertebrata
    MAMMALIAN_SPECIFIC = "mammalian_specific"     # Conserved in Mammalia
    LINEAGE_SPECIFIC = "lineage_specific"         # Primate / species-specific
    DIVERGENT = "divergent"                       # Rapidly evolving / non-conserved


class EvidenceProvenance(str, Enum):
    OBSERVED = "observed"
    CURATED = "curated"
    INFERRED = "inferred"
    PREDICTED = "predicted"
    SIMULATED = "simulated"


@dataclass
class CanonicalIdentityRecord:
    """Standardized cross-species protein/gene identity record."""
    organism_taxonomy_id: int
    gene_id: str
    protein_accession: str
    protein_isoform: str = "1"
    sequence_hash: str = ""
    annotation_release: str = "Ensembl_110"
    source_database: str = "UniProt"
    gene_symbol: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def dict(self) -> Dict[str, Any]:
        return self.to_dict()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> CanonicalIdentityRecord:
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class OmicsDataset:
    """Represents an ingested omics dataset preserving modality semantics and provenance."""
    dataset_id: str
    name: str
    modality: OmicsModality
    source: str  # GEO, PRIDE, CPTAC, HCA, etc.
    organism_taxonomy_id: int = 9606
    genome_assembly: str = "GRCh38"
    n_samples: int = 0
    n_features: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    version: str = "v1.0"
    created_at: str = field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["modality"] = self.modality.value if isinstance(self.modality, Enum) else self.modality
        return d

    def dict(self) -> Dict[str, Any]:
        return self.to_dict()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> OmicsDataset:
        data_clean = dict(data)
        if "modality" in data_clean and isinstance(data_clean["modality"], str):
            data_clean["modality"] = OmicsModality(data_clean["modality"])
        return cls(**{k: v for k, v in data_clean.items() if k in cls.__dataclass_fields__})


@dataclass
class BiologicalSample:
    """Represents an individual biological specimen, cell, or spatial spot with context."""
    sample_id: str
    dataset_id: str
    donor_id: str
    tissue: str
    cell_type: Optional[str] = None
    disease_state: str = "healthy"
    treatment: str = "control"
    timepoint: str = "0h"
    batch_id: str = "batch_0"
    organism_taxonomy_id: int = 9606
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def dict(self) -> Dict[str, Any]:
        return self.to_dict()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> BiologicalSample:
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class OmicsMeasurement:
    """Represents a specific feature measurement preserving raw and normalized values."""
    measurement_id: str
    sample_id: str
    feature_id: str
    modality: OmicsModality
    raw_value: float
    normalized_value: float
    unit: str = "log2_cpm"
    is_missing: bool = False
    quality_flag: str = "PASS"

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["modality"] = self.modality.value if isinstance(self.modality, Enum) else self.modality
        return d

    def dict(self) -> Dict[str, Any]:
        return self.to_dict()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> OmicsMeasurement:
        data_clean = dict(data)
        if "modality" in data_clean and isinstance(data_clean["modality"], str):
            data_clean["modality"] = OmicsModality(data_clean["modality"])
        return cls(**{k: v for k, v in data_clean.items() if k in cls.__dataclass_fields__})


@dataclass
class MolecularFeature:
    """Gene, transcript, protein, phosphosite, or metabolite feature."""
    feature_id: str
    symbol: str
    feature_type: str  # gene, transcript, protein, phosphosite, peak, metabolite
    canonical_ids: Dict[str, str] = field(default_factory=dict)
    organism_taxonomy_id: int = 9606
    genomic_locus: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def dict(self) -> Dict[str, Any]:
        return self.to_dict()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> MolecularFeature:
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class CellPopulation:
    """Annotated cell population, state cluster, or single-cell subpopulation."""
    population_id: str
    dataset_id: str
    cell_type: str
    cell_state: str = "homeostatic"
    marker_genes: List[str] = field(default_factory=list)
    cell_count: int = 0
    fraction_of_total: float = 0.0
    trajectory_pseudotime: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def dict(self) -> Dict[str, Any]:
        return self.to_dict()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> CellPopulation:
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class SpatialRegion:
    """Tissue microenvironment, spatial coordinate spot, or histological domain."""
    region_id: str
    sample_id: str
    tissue_section: str
    x_microns: float
    y_microns: float
    spatial_cluster: str
    dominant_cell_type: str
    neighborhood_density: float = 1.0
    spatially_variable_genes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def dict(self) -> Dict[str, Any]:
        return self.to_dict()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> SpatialRegion:
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class MolecularProgram:
    """Coordinated biological program (signaling cascade, metabolic flux, or regulon)."""
    program_id: str
    name: str
    program_type: str  # transcription_regulon, phosphorylation_cascade, metabolic_module
    associated_features: List[str] = field(default_factory=list)
    activity_scores: Dict[str, float] = field(default_factory=dict)
    pathway_enrichment: List[Dict[str, Any]] = field(default_factory=list)
    confidence: float = 0.88

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def dict(self) -> Dict[str, Any]:
        return self.to_dict()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> MolecularProgram:
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class LatentRepresentation:
    """Multi-omics learned embedding preserving shared and modality-specific latent spaces."""
    representation_id: str
    entity_id: str  # sample_id or cell_id
    model_name: str
    shared_factors: List[float] = field(default_factory=list)
    private_factors: Dict[str, List[float]] = field(default_factory=dict)
    variance_explained: Dict[str, float] = field(default_factory=dict)
    version: str = "v1.0"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def dict(self) -> Dict[str, Any]:
        return self.to_dict()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> LatentRepresentation:
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class OrthologGroup:
    """Cross-species orthologous gene/protein cluster."""
    ortholog_group_id: str
    gene_symbol: str
    evolutionary_depth: str  # Eukaryota, Bilateria, Vertebrata, Mammalia
    member_genes: List[Dict[str, Any]] = field(default_factory=list)
    consensus_function: str = ""
    duplication_events: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def dict(self) -> Dict[str, Any]:
        return self.to_dict()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> OrthologGroup:
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class ProteinFamily:
    """Protein domain architecture family classification (Pfam/InterPro)."""
    family_id: str
    name: str
    accession: str  # PF00069
    domain_architecture: List[str] = field(default_factory=list)
    members_count: int = 0
    species_distribution: Dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def dict(self) -> Dict[str, Any]:
        return self.to_dict()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ProteinFamily:
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class PhylogeneticTree:
    """Evolutionary tree representation with species mapping and branch lengths."""
    tree_id: str
    family_id: str
    newick_string: str
    species_included: List[str] = field(default_factory=list)
    bootstrap_support_mean: float = 92.5
    tree_method: str = "Maximum Likelihood (IQ-TREE / FastTree)"
    created_at: str = field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def dict(self) -> Dict[str, Any]:
        return self.to_dict()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> PhylogeneticTree:
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class EvolutionaryEvent:
    """Inferred evolutionary event: duplication, loss, functional divergence, or innovation."""
    event_id: str
    gene_symbol: str
    event_type: str  # gene_duplication, gene_loss, subfunctionalization, neofunctionalization
    lineage: str     # e.g., Teleost whole-genome duplication, Primate-specific
    divergence_mya: float = 100.0  # Millions of years ago
    confidence: float = 0.85

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def dict(self) -> Dict[str, Any]:
        return self.to_dict()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> EvolutionaryEvent:
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class ConservedInteraction:
    """
    Protein-protein interaction mapped across evolutionary history.
    Explicitly accounts for unequal database experimental coverage.
    """
    interaction_id: str
    protein_a: str
    protein_b: str
    conservation_tier: ConservationTier = ConservationTier.VERTEBRATE_CONSERVED
    organisms_observed: List[int] = field(default_factory=list)  # Taxonomy IDs where experimentally confirmed
    organisms_inferred: List[int] = field(default_factory=list)  # Taxonomy IDs where transferred via orthology
    alignment_score: float = 0.85
    coverage_adjusted_confidence: float = 0.82
    coverage_caution_note: str = (
        "Absence of interaction in an organism database reflects unequal experimental coverage, not proof of evolutionary loss."
    )

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["conservation_tier"] = (
            self.conservation_tier.value
            if isinstance(self.conservation_tier, Enum)
            else self.conservation_tier
        )
        return d

    def dict(self) -> Dict[str, Any]:
        return self.to_dict()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ConservedInteraction:
        data_clean = dict(data)
        if "conservation_tier" in data_clean and isinstance(data_clean["conservation_tier"], str):
            data_clean["conservation_tier"] = ConservationTier(data_clean["conservation_tier"])
        return cls(**{k: v for k, v in data_clean.items() if k in cls.__dataclass_fields__})


@dataclass
class EvolutionaryModule:
    """Network community or functional module conserved or rewired across lineages."""
    module_id: str
    name: str
    core_proteins: List[str] = field(default_factory=list)
    lineage_specific_additions: Dict[str, List[str]] = field(default_factory=dict)
    pathways_spanned: List[str] = field(default_factory=list)
    conservation_score: float = 0.88

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def dict(self) -> Dict[str, Any]:
        return self.to_dict()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> EvolutionaryModule:
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class ComparativeAnalysis:
    """Cross-species system comparison result."""
    analysis_id: str
    query_species: str
    target_species: str
    conserved_features_count: int
    rewired_interactions_count: int
    alignment_f1: float = 0.85
    summary_findings: List[str] = field(default_factory=list)
    provenance: EvidenceProvenance = EvidenceProvenance.INFERRED

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["provenance"] = self.provenance.value if isinstance(self.provenance, Enum) else self.provenance
        return d

    def dict(self) -> Dict[str, Any]:
        return self.to_dict()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ComparativeAnalysis:
        data_clean = dict(data)
        if "provenance" in data_clean and isinstance(data_clean["provenance"], str):
            data_clean["provenance"] = EvidenceProvenance(data_clean["provenance"])
        return cls(**{k: v for k, v in data_clean.items() if k in cls.__dataclass_fields__})


@dataclass
class EvolutionaryHypothesis:
    """Testable scientific hypothesis linking evolutionary adaptation to molecular mechanism or disease."""
    hypothesis_id: str
    statement: str
    evidence_sources: List[str] = field(default_factory=list)
    cross_species_validity: Dict[str, bool] = field(default_factory=dict)
    falsification_criteria: str = ""
    suggested_model_organism: str = "Mus musculus"
    confidence: float = 0.82

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def dict(self) -> Dict[str, Any]:
        return self.to_dict()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> EvolutionaryHypothesis:
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
