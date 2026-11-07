"""
PROTEA - Biological Reasoning Engine (BRE) Core Schemas
Typed data models for questions, evidence, mechanisms, hypotheses, perturbations, and reasoning traces.
"""

from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
from enum import Enum
import uuid
import time

class EvidenceStatus(str, Enum):
    EXPERIMENTAL = "EXPERIMENTAL"     # Supported by physical/biochemical wet-lab experiment
    COMPUTATIONAL = "COMPUTATIONAL"   # Derived from GNN, PLM, or graph prediction
    HYPOTHESIS = "HYPOTHESIS"         # Proposed mechanism or abductive conjecture

class BiologicalCertainty(str, Enum):
    ESTABLISHED = "ESTABLISHED"       # Multiple independent peer-reviewed experimental verifications
    PROBABLE = "PROBABLE"             # Strong computational and indirect evidence
    HYPOTHETICAL = "HYPOTHETICAL"     # Plausible candidate requiring primary experimental testing
    CONTRADICTED = "CONTRADICTED"     # Existing evidence disputes this mechanism

class RelationshipType(str, Enum):
    PHYSICAL_BINDING = "PHYSICAL_BINDING"         # Direct physical protein-protein interaction
    DIRECT_REGULATION = "DIRECT_REGULATION"       # Enzymatic/transcription factor regulation
    CAUSAL_EFFECT = "CAUSAL_EFFECT"               # Net downstream outcome

class BiologicalEvidence(BaseModel):
    """Atomic unit of evidence in the biological reasoning framework."""
    evidence_id: str = Field(default_factory=lambda: f"EVD-{uuid.uuid4().hex[:8].upper()}")
    subject_id: str
    predicate: str
    object_id: str
    source: str                                   # IntAct, BioGRID, Reactome, STRING, PubMed
    evidence_type: str = "binding"                # binding, phosphorylation, ubiquitination, expression
    evidence_code: Optional[str] = "EXP"          # EXP, IDA, X-ray, NMR, Cryo-EM, Y2H, AP-MS, IEA, COMP
    organism: Optional[str] = "Homo sapiens"
    tissue: Optional[str] = None
    condition: Optional[str] = None
    publication_id: Optional[str] = None          # PubMed ID, DOI
    dataset_version: Optional[str] = "1.0"
    confidence: float = 0.85
    evidence_status: EvidenceStatus = EvidenceStatus.EXPERIMENTAL

class BiologicalQuestion(BaseModel):
    """Structured representation of a biological query."""
    question_id: str = Field(default_factory=lambda: f"Q-{uuid.uuid4().hex[:8].upper()}")
    raw_query: str
    task: str = "upstream_regulator_analysis"
    target: str
    organism: str = "Homo sapiens"
    context: Dict[str, Any] = Field(default_factory=dict) # tissue, condition, observation, timepoint
    requested_outputs: List[str] = Field(default_factory=lambda: ["candidate_regulators", "affected_pathways", "supporting_evidence"])
    ambiguities: List[Dict[str, Any]] = Field(default_factory=list)

class MolecularMechanismStep(BaseModel):
    """Single step in a multi-hop molecular chain."""
    source: str
    target: str
    mechanism: str                               # activates, inhibits, phosphorylates, cleaves
    relationship_type: RelationshipType = RelationshipType.DIRECT_REGULATION
    sign: int = 1                                # +1 (activation), -1 (inhibition), 0 (neutral/ambiguous)
    confidence: float = 0.85
    evidence_status: EvidenceStatus = EvidenceStatus.EXPERIMENTAL
    evidence_ids: List[str] = Field(default_factory=list)

class MolecularMechanism(BaseModel):
    """Complete multi-hop molecular causal mechanism."""
    mechanism_id: str = Field(default_factory=lambda: f"MECH-{uuid.uuid4().hex[:8].upper()}")
    chain: List[str]
    steps: List[MolecularMechanismStep] = Field(default_factory=list)
    net_effect: str = "Activation"
    net_sign: int = 1
    cumulative_confidence: float = 0.85
    compartments: List[str] = Field(default_factory=list)

class Hypothesis(BaseModel):
    """Competing testable biological hypothesis."""
    hypothesis_id: str = Field(default_factory=lambda: f"HYP-{uuid.uuid4().hex[:8].upper()}")
    statement: str
    target_process: str
    proposed_mechanism: Optional[MolecularMechanism] = None
    supporting_evidence: List[BiologicalEvidence] = Field(default_factory=list)
    contradictory_evidence: List[BiologicalEvidence] = Field(default_factory=list)
    required_assumptions: List[str] = Field(default_factory=list)
    predicted_consequences: List[str] = Field(default_factory=list)
    evidence_strength: float = 0.75              # Quality and quantity of supporting observations
    model_confidence: float = 0.80               # Statistical confidence of computational models
    biological_certainty: BiologicalCertainty = BiologicalCertainty.PROBABLE
    potential_validation_experiments: List[str] = Field(default_factory=list)

class PerturbationScenario(BaseModel):
    """In silico perturbation experiment and network response."""
    scenario_id: str = Field(default_factory=lambda: f"PERT-{uuid.uuid4().hex[:8].upper()}")
    target_protein: str
    perturbation_type: str = "knockout"          # knockout, knockdown, overexpression, inhibition
    tissue: Optional[str] = None
    propagation_depth: int = 3
    perturbed_nodes: Dict[str, float] = Field(default_factory=dict)
    affected_pathways: List[Dict[str, Any]] = Field(default_factory=list)
    model_qualifications: List[str] = Field(default_factory=list)

class ReasoningTraceStep(BaseModel):
    """Individual auditable step executed by reasoning agents."""
    step_index: int
    agent: str
    action: str
    inputs: Dict[str, Any] = Field(default_factory=dict)
    outputs: Dict[str, Any] = Field(default_factory=dict)
    status: str = "SUCCESS"
    timestamp: float = Field(default_factory=time.time)

class ReasoningReport(BaseModel):
    """Comprehensive, evidence-grounded scientific reasoning report."""
    report_id: str = Field(default_factory=lambda: f"REP-{uuid.uuid4().hex[:8].upper()}")
    question: BiologicalQuestion
    executive_summary: str
    primary_mechanism: Optional[MolecularMechanism] = None
    competing_hypotheses: List[Hypothesis] = Field(default_factory=list)
    contradictions_and_limitations: List[str] = Field(default_factory=list)
    confidence_breakdown: Dict[str, float] = Field(default_factory=dict)
    suggested_experiments: List[str] = Field(default_factory=list)
    evidence_manifest: List[BiologicalEvidence] = Field(default_factory=list)
    reasoning_trace: List[ReasoningTraceStep] = Field(default_factory=list)
    created_at: float = Field(default_factory=time.time)
