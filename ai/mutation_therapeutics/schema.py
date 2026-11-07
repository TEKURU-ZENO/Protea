"""
PROTEA Phase 10: Mutation & Therapeutic Intelligence Engine (MTIE)
Core Data Schemas and Domain Models
"""

from __future__ import annotations
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Dict, List, Any, Optional, Tuple
import uuid
import datetime


class MutationType(str, Enum):
    MISSENSE = "missense"
    NONSENSE = "nonsense"
    FRAMESHIFT = "frameshift"
    INFRAME_INDEL = "inframe_indel"
    SYNONYMOUS = "synonymous"
    SPLICE_SITE = "splice_site"
    OTHER = "other"


class FunctionalClass(str, Enum):
    LOSS_OF_FUNCTION = "loss_of_function"
    GAIN_OF_FUNCTION = "gain_of_function"
    DOMINANT_NEGATIVE = "dominant_negative"
    NEUTRAL_BENIGN = "neutral_benign"
    UNCHARACTERIZED = "uncharacterized"


class StabilityClass(str, Enum):
    STABILIZING = "stabilizing"
    NEUTRAL = "neutral"
    DESTABILIZING = "destabilizing"
    SEVERELY_DESTABILIZING = "severely_destabilizing"


class ACMGClass(str, Enum):
    PATHOGENIC = "pathogenic"
    LIKELY_PATHOGENIC = "likely_pathogenic"
    VUS = "uncertain_significance"
    LIKELY_BENIGN = "likely_benign"
    BENIGN = "benign"


class TractabilityTier(str, Enum):
    SMALL_MOLECULE = "small_molecule"
    MONOCLONAL_ANTIBODY = "monoclonal_antibody"
    PROTAC_DEGRADER = "protac_degrader"
    RNA_TARGETING = "rna_targeting"
    OTHER = "other"


@dataclass
class GenomicVariant:
    """Represents a genomic variant parsed from VCF or coordinate specifications."""
    chrom: str
    pos: int
    ref: str
    alt: str
    id: str = "."
    qual: float = 100.0
    filter: str = "PASS"
    info: Dict[str, Any] = field(default_factory=dict)
    build: str = "GRCh38"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def dict(self) -> Dict[str, Any]:
        return self.to_dict()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> GenomicVariant:
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class TranscriptVariant:
    """Represents an isoform/transcript-level consequence of a variant."""
    transcript_id: str
    gene_id: str
    gene_symbol: str
    hgvs_c: str
    hgvs_p: Optional[str] = None
    exon: Optional[int] = None
    strand: str = "+"
    consequence: str = "missense_variant"
    is_canonical: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def dict(self) -> Dict[str, Any]:
        return self.to_dict()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> TranscriptVariant:
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class ProteinMutation:
    """Represents a specific amino acid change in a target protein."""
    gene_symbol: str
    protein_id: str
    wildtype_aa: str
    position: int
    mutant_aa: str
    hgvs_p: str  # e.g., 'p.Val600Glu' or 'p.V600E'
    mutation_type: MutationType = MutationType.MISSENSE
    is_somatic: bool = True
    clinical_significance: str = "unknown"
    dbsnp_id: Optional[str] = None
    cosmic_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["mutation_type"] = self.mutation_type.value if isinstance(self.mutation_type, Enum) else self.mutation_type
        return d

    def dict(self) -> Dict[str, Any]:
        return self.to_dict()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ProteinMutation:
        data_clean = dict(data)
        if "mutation_type" in data_clean and isinstance(data_clean["mutation_type"], str):
            data_clean["mutation_type"] = MutationType(data_clean["mutation_type"])
        return cls(**{k: v for k, v in data_clean.items() if k in cls.__dataclass_fields__})


@dataclass
class MutantProtein:
    """
    Represents a versioned, branched mutated protein model.
    Follows Branching Principle: Reference protein is never overwritten.
    """
    protein_id: str
    wildtype_protein_id: str
    mutation_label: str  # e.g. "BRAF_V600E"
    mutated_sequence: str
    wildtype_sequence: str
    mutations: List[ProteinMutation] = field(default_factory=list)
    branch_id: str = field(default_factory=lambda: f"branch_{uuid.uuid4().hex[:8]}")
    version: str = "v1.0"
    created_at: str = field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["mutations"] = [m.to_dict() if hasattr(m, "to_dict") else m for m in self.mutations]
        return d

    def dict(self) -> Dict[str, Any]:
        return self.to_dict()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> MutantProtein:
        data_clean = dict(data)
        if "mutations" in data_clean:
            data_clean["mutations"] = [
                ProteinMutation.from_dict(m) if isinstance(m, dict) else m
                for m in data_clean["mutations"]
            ]
        return cls(**{k: v for k, v in data_clean.items() if k in cls.__dataclass_fields__})


@dataclass
class StructuralEffect:
    """Structural impact evaluation including residue displacement and interface perturbation."""
    protein_id: str
    mutation_label: str
    pdb_id: Optional[str] = None
    plddt_wildtype: float = 85.0
    plddt_mutant: float = 83.5
    backbone_rmsd: float = 0.42
    interface_residues_perturbed: List[int] = field(default_factory=list)
    hydrogen_bonds_lost: int = 0
    salt_bridges_disrupted: int = 0
    sasa_change_angstrom2: float = 12.4
    allosteric_pocket_perturbed: bool = False
    confidence_score: float = 0.88

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def dict(self) -> Dict[str, Any]:
        return self.to_dict()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> StructuralEffect:
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class FunctionalEffect:
    """Thermodynamic stability and functional mechanism predictions."""
    protein_id: str
    mutation_label: str
    ddg_kcal_mol: float  # Folding DeltaDeltaG: positive = destabilizing, negative = stabilizing
    stability_classification: StabilityClass = StabilityClass.NEUTRAL
    functional_classification: FunctionalClass = FunctionalClass.UNCHARACTERIZED
    esm_log_odds_delta: float = -4.5
    evolutionary_conservation_score: float = 0.72
    catalytic_site_disrupted: bool = False
    aggregation_propensity_delta: float = 0.15
    confidence_score: float = 0.85

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["stability_classification"] = (
            self.stability_classification.value
            if isinstance(self.stability_classification, Enum)
            else self.stability_classification
        )
        d["functional_classification"] = (
            self.functional_classification.value
            if isinstance(self.functional_classification, Enum)
            else self.functional_classification
        )
        return d

    def dict(self) -> Dict[str, Any]:
        return self.to_dict()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> FunctionalEffect:
        data_clean = dict(data)
        if "stability_classification" in data_clean and isinstance(data_clean["stability_classification"], str):
            data_clean["stability_classification"] = StabilityClass(data_clean["stability_classification"])
        if "functional_classification" in data_clean and isinstance(data_clean["functional_classification"], str):
            data_clean["functional_classification"] = FunctionalClass(data_clean["functional_classification"])
        return cls(**{k: v for k, v in data_clean.items() if k in cls.__dataclass_fields__})


@dataclass
class InteractionRewiring:
    """Mutation-conditioned interactome rewiring tracking retention, loss, and candidate gains."""
    mutation_label: str
    mutant_protein_id: str
    wildtype_protein_id: str
    retained_interactions: List[Dict[str, Any]] = field(default_factory=list)
    lost_interactions: List[Dict[str, Any]] = field(default_factory=list)
    gained_interactions: List[Dict[str, Any]] = field(default_factory=list)
    total_reference_edges: int = 0
    rewiring_index: float = 0.0  # (lost + gained) / (retained + lost)
    branch_graph_id: str = field(default_factory=lambda: f"interactome_branch_{uuid.uuid4().hex[:8]}")

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def dict(self) -> Dict[str, Any]:
        return self.to_dict()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> InteractionRewiring:
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class DiseaseMechanism:
    """Causal mechanistic trace linking variant to pathway breakdown and disease phenotype."""
    disease_name: str
    disease_id: str
    primary_mutations: List[str]
    disrupted_pathways: List[Dict[str, Any]] = field(default_factory=list)
    hyperactivated_pathways: List[Dict[str, Any]] = field(default_factory=list)
    causal_chain: List[str] = field(default_factory=list)
    bypass_mechanisms: List[str] = field(default_factory=list)
    phenotypic_consequence: str = ""
    evidence_score: float = 0.85

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def dict(self) -> Dict[str, Any]:
        return self.to_dict()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> DiseaseMechanism:
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class TherapeuticTarget:
    """Identified drug target with multi-criteria prioritization scores."""
    target_id: str
    gene_symbol: str
    protein_id: str
    rationale: str
    centrality_score: float = 0.5
    depmap_dependency_score: float = -0.6
    druggability_score: float = 0.8
    safety_score: float = 0.75
    tractability_tier: TractabilityTier = TractabilityTier.SMALL_MOLECULE
    composite_priority: float = 0.75
    pocket_volume_angstrom3: float = 650.0

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["tractability_tier"] = (
            self.tractability_tier.value
            if isinstance(self.tractability_tier, Enum)
            else self.tractability_tier
        )
        return d

    def dict(self) -> Dict[str, Any]:
        return self.to_dict()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> TherapeuticTarget:
        data_clean = dict(data)
        if "tractability_tier" in data_clean and isinstance(data_clean["tractability_tier"], str):
            data_clean["tractability_tier"] = TractabilityTier(data_clean["tractability_tier"])
        return cls(**{k: v for k, v in data_clean.items() if k in cls.__dataclass_fields__})


@dataclass
class DrugCandidate:
    """Small molecule or biologic therapeutic candidate."""
    drug_id: str
    name: str
    chembl_id: str
    mechanism_of_action: str
    primary_targets: List[str] = field(default_factory=list)
    molecule_type: str = "small_molecule"
    clinical_phase: str = "Phase 4"
    smiles: Optional[str] = None
    molecular_weight: float = 450.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def dict(self) -> Dict[str, Any]:
        return self.to_dict()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> DrugCandidate:
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class BindingEvidence:
    """Binding affinity and molecular docking data with explicit guardrails."""
    drug_id: str
    target_id: str
    docking_score_kcal_mol: Optional[float] = None
    experimental_kd_nm: Optional[float] = None
    experimental_ic50_nm: Optional[float] = None
    binding_site: Optional[str] = "ATP-binding cleft"
    docking_algorithm: str = "AutoDock Vina representation"
    confidence: float = 0.85
    source: str = "curated_and_docking"
    caution_note: str = (
        "Docking score is a computational ranking estimate and does NOT equal physical binding affinity."
    )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def dict(self) -> Dict[str, Any]:
        return self.to_dict()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> BindingEvidence:
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class DrugTargetEvidence:
    """Integrated candidate-target evaluation with selectivity and off-target analysis."""
    drug: DrugCandidate
    target: TherapeuticTarget
    binding: BindingEvidence
    selectivity_ratio: float = 12.5  # target vs off-target affinity ratio
    off_target_risks: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "drug": self.drug.to_dict(),
            "target": self.target.to_dict(),
            "binding": self.binding.to_dict(),
            "selectivity_ratio": self.selectivity_ratio,
            "off_target_risks": self.off_target_risks,
        }

    def dict(self) -> Dict[str, Any]:
        return self.to_dict()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> DrugTargetEvidence:
        return cls(
            drug=DrugCandidate.from_dict(data["drug"]),
            target=TherapeuticTarget.from_dict(data["target"]),
            binding=BindingEvidence.from_dict(data["binding"]),
            selectivity_ratio=data.get("selectivity_ratio", 1.0),
            off_target_risks=data.get("off_target_risks", []),
        )


@dataclass
class DrugResponse:
    """Dose-response modeling across wildtype vs mutant proteins."""
    drug_id: str
    target_id: str
    wildtype_ic50_nm: float
    mutant_ic50_nm: float
    resistance_fold_change: float
    hill_coefficient: float = 1.0
    response_phenotype: str = "sensitive"  # sensitive, intermediate, resistant

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def dict(self) -> Dict[str, Any]:
        return self.to_dict()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> DrugResponse:
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class ResistanceMechanism:
    """Secondary resistance mutation or bypass signaling emergence."""
    mutation_label: str
    drug_id: str
    target_id: str
    mechanism_type: str  # gatekeeper_mutation, allosteric_disruption, bypass_signaling
    ic50_fold_change: float
    alternative_targets: List[str] = field(default_factory=list)
    recommended_strategy: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def dict(self) -> Dict[str, Any]:
        return self.to_dict()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ResistanceMechanism:
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class CombinationTherapy:
    """Multi-metric combination synergy assessment."""
    drug_a_id: str
    drug_b_id: str
    target_a: str
    target_b: str
    bliss_excess: float  # Positive = synergy
    loewe_combination_index: float  # < 1.0 = synergy
    hsa_score: float  # Highest Single Agent
    zip_score: float  # Zero Interaction Potency
    synergistic: bool = True
    mechanistic_basis: str = ""
    recommended_ratio: str = "1:1"
    metric_assumptions: Dict[str, str] = field(
        default_factory=lambda: {
            "bliss": "Assumes mutually non-exclusive, independent probabilistic actions",
            "loewe": "Assumes identical mechanism and mutually exclusive dose-additive action",
            "hsa": "Requires combination effect to exceed greater of individual single-agent effects",
            "zip": "Captures potency shifts under zero interaction assumption without dose-response fitting bias",
        }
    )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def dict(self) -> Dict[str, Any]:
        return self.to_dict()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> CombinationTherapy:
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class TherapeuticScenario:
    """In-silico simulation scenario of a therapeutic perturbation."""
    scenario_id: str
    name: str
    mutant_context: str
    interventions: List[Dict[str, Any]] = field(default_factory=list)
    disease_pathway_inhibition: float = 0.85
    toxicity_estimate: float = 0.12
    essential_gene_retention: float = 0.94
    pareto_optimal: bool = True
    simulation_duration_hours: float = 48.0
    trajectory_points: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def dict(self) -> Dict[str, Any]:
        return self.to_dict()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> TherapeuticScenario:
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class TherapeuticValidationReport:
    """ACMG/AMP clinical research classification and evidence report."""
    variant_id: str
    mutation_label: str
    acmg_class: ACMGClass = ACMGClass.VUS
    acmg_criteria_met: List[str] = field(default_factory=list)
    evidence_counts: Dict[str, int] = field(default_factory=dict)
    confidence_interval: Tuple[float, float] = (0.75, 0.95)
    clinical_boundary_disclaimer: str = (
        "PROTEA MTIE is a computational research decision-support engine. "
        "Outputs are for hypothesis generation and must be validated experimentally and clinically."
    )
    status: str = "validated"

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["acmg_class"] = (
            self.acmg_class.value
            if isinstance(self.acmg_class, Enum)
            else self.acmg_class
        )
        return d

    def dict(self) -> Dict[str, Any]:
        return self.to_dict()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> TherapeuticValidationReport:
        data_clean = dict(data)
        if "acmg_class" in data_clean and isinstance(data_clean["acmg_class"], str):
            data_clean["acmg_class"] = ACMGClass(data_clean["acmg_class"])
        return cls(**{k: v for k, v in data_clean.items() if k in cls.__dataclass_fields__})
