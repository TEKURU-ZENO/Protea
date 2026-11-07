"""Core data schemas and typed structures for the Digital Interactome Twin (DIT)."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class StateStatus(str, Enum):
    """Categorical origin of a molecular state measurement or property."""
    OBSERVED = "OBSERVED"        # Directly quantified via physical wet-lab assay (e.g. RNA-seq, Mass-Spec)
    ESTIMATED = "ESTIMATED"      # Imputed or statistically reconstructed from neighboring data
    PREDICTED = "PREDICTED"      # Inferred by machine learning or structural foundation models (PLM/GNN)
    SIMULATED = "SIMULATED"      # Counterfactual perturbation or dynamic propagation state


class EdgeType(str, Enum):
    """Biological nature of interactome network edges."""
    PHYSICAL_INTERACTION = "PHYSICAL_INTERACTION"       # Direct physical binding / PPI
    TRANSCRIPTIONAL_REGULATION = "TRANSCRIPTIONAL_REGULATION" # TF to gene promoter
    PHOSPHORYLATION = "PHOSPHORYLATION"                 # Kinase-substrate post-translational modification
    COMPLEX_MEMBER = "COMPLEX_MEMBER"                   # Co-complex membership
    METABOLIC_CONVERSION = "METABOLIC_CONVERSION"       # Enzyme-catalyzed reaction
    TRANSLOCATION = "TRANSLOCATION"                     # Translocation between cellular compartments


class EdgeStatus(str, Enum):
    """Provenance class of a network edge."""
    OBSERVED = "OBSERVED"        # Confirmed in matched experimental sample
    CURATED = "CURATED"          # Documented in curated gold-standard reference (e.g., IntAct, Reactome)
    INFERRED = "INFERRED"        # High-confidence topological or pathway transitive inference
    PREDICTED = "PREDICTED"      # Edge candidate predicted by GNN link prediction


class Modality(str, Enum):
    """Supported multi-omics modalities."""
    TRANSCRIPTOMICS = "TRANSCRIPTOMICS"
    PROTEOMICS = "PROTEOMICS"
    PHOSPHOPROTEOMICS = "PHOSPHOPROTEOMICS"
    EPIGENOMICS = "EPIGENOMICS"
    METABOLOMICS = "METABOLOMICS"


class InterventionType(str, Enum):
    """Types of in silico interventions applicable to twin scenarios."""
    KNOCKOUT = "KNOCKOUT"              # Complete -100% loss-of-function
    KNOCKDOWN = "KNOCKDOWN"            # -50% to -80% shRNA/CRISPRi reduction
    OVEREXPRESSION = "OVEREXPRESSION"  # +100% to +300% cDNA gain-of-function
    INHIBITION = "INHIBITION"          # Targeted small-molecule chemical inhibition
    ACTIVATION = "ACTIVATION"          # Agonist or upstream activation
    DRUG_TREATMENT = "DRUG_TREATMENT"  # Multi-target pharmacological perturbation
    MUTATION = "MUTATION"              # Single nucleotide variant / missense alteration


@dataclass
class BiologicalContext:
    """Contextual metadata specifying the biological environment of the twin."""
    organism_id: str = "NCBI:9606"              # Organism taxon (e.g. NCBI:9606 for Homo sapiens)
    tissue_id: Optional[str] = "liver"          # Tissue ontology ID or common name
    cell_type_id: Optional[str] = "hepatocyte"  # Cell ontology ID or name
    condition: str = "healthy"                  # Clinical or experimental state (e.g., healthy, disease, treated)
    treatment: Optional[str] = None             # Specific perturbation/treatment regime if applied
    timepoint: Optional[float] = None           # Relative or absolute timepoint in hours
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class MolecularObservation:
    """Individual empirical observation ingested into the digital twin."""
    observation_id: str
    entity_id: str
    modality: str
    measurement_type: str
    value: Optional[float]
    unit: Optional[str]
    organism_id: str
    tissue_id: Optional[str]
    cell_type_id: Optional[str]
    sample_id: str
    condition: Optional[str]
    timepoint: Optional[float]
    assay: str
    source_dataset: str
    normalization_method: Optional[str] = None
    uncertainty: Optional[float] = None
    provenance_id: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class NetworkEdgeEvidence:
    """Directed or undirected biological edge with full contextual provenance."""
    source: str
    target: str
    edge_type: str = EdgeType.PHYSICAL_INTERACTION.value
    directed: bool = False
    sign: Optional[int] = None                  # +1 (activation), -1 (inhibition), 0 (neutral/binding)
    confidence: float = 0.50
    edge_status: str = EdgeStatus.CURATED.value
    evidence_sources: List[str] = field(default_factory=list)
    tissue: Optional[str] = None
    mechanism: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class InteractomeSnapshot:
    """Immutable graph snapshot for a specific context and version."""
    snapshot_id: str
    twin_id: str
    version_id: str
    nodes: List[str] = field(default_factory=list)
    edges: List[NetworkEdgeEvidence] = field(default_factory=list)
    content_hash: str = ""
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def compute_hash(self) -> str:
        data_str = f"{self.twin_id}:{self.version_id}:{sorted(self.nodes)}:{len(self.edges)}"
        self.content_hash = hashlib.sha256(data_str.encode("utf-8")).hexdigest()
        return self.content_hash

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["edges"] = [e.to_dict() if hasattr(e, "to_dict") else e for e in self.edges]
        return d


@dataclass
class MolecularState:
    """State vector attributes for a specific biological entity."""
    entity_id: str
    gene_expression: Optional[float] = None       # log2(TPM + 1)
    protein_abundance: Optional[float] = None     # log2(LFQ intensity)
    protein_activity: Optional[float] = None      # Estimated regulatory/enzymatic activity [-1.0, 1.0]
    phosphorylation: Optional[float] = None       # Mean phosphorylation occupancy [0.0, 1.0]
    subcellular_location: Optional[str] = None    # nucleus, cytosol, membrane, mitochondria
    pathway_activity: Optional[float] = None      # Pathway activity metric
    interaction_status: Optional[str] = "active"  # active, repressed, rewired
    cell_condition: Optional[str] = "healthy"
    status: str = StateStatus.OBSERVED.value
    imputed_fields: List[str] = field(default_factory=list)
    confidence: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class TemporalObservation:
    """Time-stamped molecular state bundle capturing biological trajectory."""
    timepoint: float
    unit: str = "hours"
    states: Dict[str, MolecularState] = field(default_factory=dict)
    active_edges_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timepoint": self.timepoint,
            "unit": self.unit,
            "states": {k: v.to_dict() if hasattr(v, "to_dict") else v for k, v in self.states.items()},
            "active_edges_count": self.active_edges_count,
            "metadata": self.metadata
        }


@dataclass
class ScenarioResult:
    """Result of an in silico intervention scenario simulation."""
    scenario_id: str
    parent_version_id: str
    target_entities: List[str]
    intervention_type: str
    perturbation_strength: float
    perturbed_states: Dict[str, MolecularState] = field(default_factory=dict)
    pathway_shifts: Dict[str, float] = field(default_factory=dict)
    rewired_edges: List[Dict[str, Any]] = field(default_factory=list)
    assumptions: List[str] = field(default_factory=list)
    uncertainty_score: float = 0.05

    def to_dict(self) -> Dict[str, Any]:
        return {
            "scenario_id": self.scenario_id,
            "parent_version_id": self.parent_version_id,
            "target_entities": self.target_entities,
            "intervention_type": self.intervention_type,
            "perturbation_strength": self.perturbation_strength,
            "perturbed_states": {k: v.to_dict() if hasattr(v, "to_dict") else v for k, v in self.perturbed_states.items()},
            "pathway_shifts": self.pathway_shifts,
            "rewired_edges": self.rewired_edges,
            "assumptions": self.assumptions,
            "uncertainty_score": self.uncertainty_score
        }


@dataclass
class TwinScenario:
    """Isolated branch representing an intervention or hypothesis without altering baseline."""
    scenario_id: str
    twin_id: str
    parent_version_id: str
    name: str
    description: str
    target_entities: List[str]
    intervention_type: str
    strength: float = 1.0
    duration: Optional[float] = None
    result: Optional[ScenarioResult] = None
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        if self.result:
            d["result"] = self.result.to_dict()
        return d


@dataclass
class TwinValidationReport:
    """Multi-dimensional fidelity report validating twin against experimental truth."""
    report_id: str
    twin_id: str
    version_id: str
    structural_fidelity: Dict[str, float] = field(default_factory=dict)  # AUROC, AUPRC, F1
    state_fidelity: Dict[str, float] = field(default_factory=dict)       # MAE, RMSE, Spearman rho
    temporal_fidelity: Dict[str, float] = field(default_factory=dict)    # Trajectory RMSE, correlation
    context_fidelity: Dict[str, float] = field(default_factory=dict)     # Tissue specificity score
    uncertainty_calibration: Dict[str, float] = field(default_factory=dict) # ECE, Brier score
    coverage_score: float = 0.90
    is_valid: bool = True
    summary: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class TwinVersion:
    """Immutable, versioned release of a biological digital twin."""
    version_id: str
    version_tag: str
    twin_id: str
    parent_version_id: Optional[str] = None
    context: BiologicalContext = field(default_factory=BiologicalContext)
    initialization_mode: str = "hybrid"
    layers: List[str] = field(default_factory=lambda: [
        "protein_interactions", "gene_regulation", "pathways", "expression", "localization"
    ])
    snapshot: Optional[InteractomeSnapshot] = None
    states: Dict[str, MolecularState] = field(default_factory=dict)
    temporal_series: List[TemporalObservation] = field(default_factory=list)
    scenarios: List[TwinScenario] = field(default_factory=list)
    validation_report: Optional[TwinValidationReport] = None
    content_hash: str = ""
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def compute_hash(self) -> str:
        s_hash = self.snapshot.compute_hash() if self.snapshot else "none"
        body = f"{self.version_id}:{self.twin_id}:{self.version_tag}:{s_hash}:{len(self.states)}"
        self.content_hash = hashlib.sha256(body.encode("utf-8")).hexdigest()
        return self.content_hash

    def to_dict(self) -> Dict[str, Any]:
        return {
            "version_id": self.version_id,
            "version_tag": self.version_tag,
            "twin_id": self.twin_id,
            "parent_version_id": self.parent_version_id,
            "context": self.context.to_dict() if hasattr(self.context, "to_dict") else self.context,
            "initialization_mode": self.initialization_mode,
            "layers": self.layers,
            "snapshot": self.snapshot.to_dict() if self.snapshot else None,
            "states": {k: v.to_dict() if hasattr(v, "to_dict") else v for k, v in self.states.items()},
            "temporal_series": [t.to_dict() if hasattr(t, "to_dict") else t for t in self.temporal_series],
            "scenarios": [s.to_dict() if hasattr(s, "to_dict") else s for s in self.scenarios],
            "validation_report": self.validation_report.to_dict() if self.validation_report else None,
            "content_hash": self.content_hash,
            "created_at": self.created_at
        }


@dataclass
class DigitalTwin:
    """Top-level container representing a biological entity's dynamic digital twin."""
    twin_id: str
    name: str
    organism: str = "NCBI:9606"
    primary_tissue: str = "liver"
    primary_cell_type: str = "hepatocyte"
    active_version_id: str = ""
    versions: Dict[str, TwinVersion] = field(default_factory=dict)
    description: str = ""
    tags: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def get_active_version(self) -> Optional[TwinVersion]:
        return self.versions.get(self.active_version_id)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "twin_id": self.twin_id,
            "name": self.name,
            "organism": self.organism,
            "primary_tissue": self.primary_tissue,
            "primary_cell_type": self.primary_cell_type,
            "active_version_id": self.active_version_id,
            "versions": {k: v.to_dict() if hasattr(v, "to_dict") else v for k, v in self.versions.items()},
            "description": self.description,
            "tags": self.tags,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
