"""
PROTEA Phase 12: Biological Intelligence Foundation Model (BIFM) - Schemas
Typed canonical contracts for multimodal representations, biological context,
multi-task predictions, world model states, interventions, and governance.
"""

from __future__ import annotations
import datetime
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Dict, List, Any, Optional


class ModalityType(str, Enum):
    SEQUENCE = "sequence"
    STRUCTURE = "structure"
    INTERACTION = "interaction"
    PATHWAY = "pathway"
    OMICS = "omics"
    CELLULAR = "cellular"
    SPATIAL = "spatial"
    EVOLUTION = "evolution"
    LITERATURE = "literature"
    UNIFIED = "unified"


class BiologicalDomain(str, Enum):
    MOLECULAR = "molecular"
    STRUCTURAL = "structural"
    INTERACTION = "interaction"
    FUNCTIONAL = "functional"
    CELLULAR = "cellular"
    DISEASE = "disease"
    EVOLUTIONARY = "evolutionary"
    EXPERIMENTAL = "experimental"
    THERAPEUTIC = "therapeutic"


class EvidenceLevel(str, Enum):
    OBSERVED = "observed"      # Tier 1: Direct experimental measurement
    CURATED = "curated"        # Tier 2: Peer-reviewed database
    INFERRED = "inferred"      # Tier 3: Statistical/projection program
    PREDICTED = "predicted"    # Tier 4: Foundation model / ML prediction
    SIMULATED = "simulated"    # Tier 5: In-silico forward dynamical run


@dataclass
class BiologicalContext:
    """Multi-scale conditioning context for biological intelligence."""
    organism_taxonomy_id: int = 9606
    organism_name: str = "Homo sapiens"
    tissue: str = "Whole_Organism"
    cell_type: Optional[str] = None
    disease_state: str = "Healthy"
    mutation_status: Optional[str] = None
    developmental_stage: Optional[str] = None
    treatment: str = "Untreated"
    timepoint: str = "0h"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> BiologicalContext:
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class BiologicalRepresentation:
    """
    Canonical representation contract for any biological entity or observation.
    Guarantees stable identity, versioned embeddings, and explicit provenance.
    """
    entity_id: str
    entity_type: str
    organism_id: Optional[str]
    biological_context: Dict[str, Any]
    modality: str
    embedding: List[float]
    model_name: str
    model_version: str
    representation_version: str
    source_ids: List[str]
    evidence_type: str
    uncertainty: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> BiologicalRepresentation:
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class MultiModalProfile:
    """Holds preserved modality-specific representations alongside unified embeddings."""
    entity_id: str
    entity_domain: str
    modality_representations: Dict[str, BiologicalRepresentation]
    unified_embedding: Optional[List[float]] = None
    shared_factors: Optional[List[float]] = None
    private_factors: Optional[Dict[str, List[float]]] = None
    created_at: str = field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["modality_representations"] = {
            k: v.to_dict() if hasattr(v, "to_dict") else v
            for k, v in self.modality_representations.items()
        }
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> MultiModalProfile:
        data_clean = dict(data)
        if "modality_representations" in data_clean:
            data_clean["modality_representations"] = {
                k: BiologicalRepresentation.from_dict(v) if isinstance(v, dict) else v
                for k, v in data_clean["modality_representations"].items()
            }
        return cls(**{k: v for k, v in data_clean.items() if k in cls.__dataclass_fields__})


@dataclass
class TaskPrediction:
    """Output contract for multi-task predictive heads."""
    task_name: str
    entity_id: str
    prediction_value: Any
    probability: float
    confidence_tier: str
    contributing_modalities: List[str]
    uncertainty: Dict[str, float]
    provenance_tier: str = EvidenceLevel.PREDICTED.value
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> TaskPrediction:
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class WorldModelState:
    """State vector representing biological system state in the BIFM world model."""
    state_id: str
    system_id: str
    context: Dict[str, Any]
    state_vector: List[float]
    pathway_activities: Dict[str, float]
    active_interactions_count: int
    step: int = 0
    uncertainty_std: float = 0.05
    timestamp: str = field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> WorldModelState:
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class InterventionSpec:
    """Standardized intervention specification for world model and counterfactual simulations."""
    target_entity: str
    intervention_type: str  # gene_knockout, knockdown, overexpression, inhibition, mutation, drug
    magnitude: float = 1.0   # e.g. 0.0 for knockout, 0.2 for knockdown, 2.0 for overexpression
    duration_hours: float = 24.0
    drug_id: Optional[str] = None
    mutation_code: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> InterventionSpec:
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class CounterfactualResult:
    """Evaluation of an in-silico counterfactual intervention."""
    intervention: InterventionSpec
    baseline_state_id: str
    perturbed_state_id: str
    state_delta_norm: float
    affected_pathways: Dict[str, float]
    candidate_rewired_edges: List[Dict[str, Any]]
    confidence: float
    is_counterfactual_hypothesis: bool = True
    epistemic_disclaimer: str = (
        "Scientific Disclaimer: Result represents a statistical counterfactual prediction from the BIFM World Model, "
        "not an experimentally verified biological intervention."
    )

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["intervention"] = self.intervention.to_dict() if hasattr(self.intervention, "to_dict") else self.intervention
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> CounterfactualResult:
        data_clean = dict(data)
        if "intervention" in data_clean and isinstance(data_clean["intervention"], dict):
            data_clean["intervention"] = InterventionSpec.from_dict(data_clean["intervention"])
        return cls(**{k: v for k, v in data_clean.items() if k in cls.__dataclass_fields__})


@dataclass
class StructuredExplanation:
    """Scientific explanation artifact synthesizing evidence, mechanisms, and hypotheses."""
    question: str
    biological_context: Dict[str, Any]
    focal_entities: List[str]
    supporting_evidence: List[Dict[str, Any]]
    contradictory_evidence: List[Dict[str, Any]]
    proposed_mechanism: str
    competing_hypotheses: List[Dict[str, Any]]
    model_predictions: List[Dict[str, Any]]
    uncertainty_analysis: Dict[str, Any]
    falsification_experiments: List[Dict[str, Any]]
    provenance_summary: Dict[str, int]
    generated_at: str = field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> StructuredExplanation:
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class ModelCardRecord:
    """Governance and model transparency record."""
    model_id: str
    model_name: str
    version: str
    architecture: str
    modalities_supported: List[str]
    encoder_dependencies: Dict[str, str]
    training_datasets: List[str]
    license: str
    benchmark_macro_score: float
    calibration_expected_error: float
    limitations: List[str]
    approval_status: str
    promoted_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ModelCardRecord:
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
