"""Core typed schemas and data structures for the AI Scientist (Autonomous Biological Discovery Engine)."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional


class ResearchState(str, Enum):
    """Lifecycle state machine for autonomous biological discovery investigations."""
    RESEARCH_CREATED = "RESEARCH_CREATED"
    QUESTION_VALIDATED = "QUESTION_VALIDATED"
    QUESTION_UNDERSTANDING = "QUESTION_UNDERSTANDING"
    LITERATURE_REVIEW = "LITERATURE_REVIEW"
    LITERATURE_RETRIEVAL = "LITERATURE_RETRIEVAL"
    KNOWLEDGE_SYNTHESIS = "KNOWLEDGE_SYNTHESIS"
    GAP_ANALYSIS = "GAP_ANALYSIS"
    RESEARCH_GAP_DETECTION = "RESEARCH_GAP_DETECTION"
    NOVELTY_AUDITING = "NOVELTY_AUDITING"
    HYPOTHESIS_GENERATION = "HYPOTHESIS_GENERATION"
    HYPOTHESIS_REVIEW = "HYPOTHESIS_REVIEW"
    HYPOTHESIS_PRIORITIZATION = "HYPOTHESIS_PRIORITIZATION"
    EXPERIMENT_DESIGN = "EXPERIMENT_DESIGN"
    EXPERIMENT_VALIDATION = "EXPERIMENT_VALIDATION"
    HUMAN_APPROVAL = "HUMAN_APPROVAL"
    HUMAN_APPROVAL_PENDING = "HUMAN_APPROVAL_PENDING"
    COMPUTATIONAL_EXECUTION = "COMPUTATIONAL_EXECUTION"
    EXPERIMENT_EXECUTION = "EXPERIMENT_EXECUTION"
    STATISTICAL_ANALYSIS = "STATISTICAL_ANALYSIS"
    SCIENTIFIC_ANALYSIS = "SCIENTIFIC_ANALYSIS"
    ADVERSARIAL_REVIEW = "ADVERSARIAL_REVIEW"
    ADVERSARIAL_CRITICISM = "ADVERSARIAL_CRITICISM"
    REVISE_HYPOTHESIS = "REVISE_HYPOTHESIS"
    REPRODUCIBILITY_PACKAGING = "REPRODUCIBILITY_PACKAGING"
    SCIENTIFIC_REPORT = "SCIENTIFIC_REPORT"
    MANUSCRIPT_GENERATION = "MANUSCRIPT_GENERATION"
    RESEARCH_ARCHIVED = "RESEARCH_ARCHIVED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class ClaimStatus(str, Enum):
    """Validation and grounding status of a biological claim."""
    EXPERIMENTAL_EVIDENCE = "EXPERIMENTAL_EVIDENCE"
    CURATED_KNOWLEDGE = "CURATED_KNOWLEDGE"
    COMPUTATIONALLY_PREDICTED = "COMPUTATIONALLY_PREDICTED"
    HYPOTHESIZED = "HYPOTHESIZED"
    CONTRADICTED = "CONTRADICTED"
    UNRESOLVED = "UNRESOLVED"


class GapType(str, Enum):
    """Taxonomy of scientific research gaps."""
    KNOWLEDGE = "KNOWLEDGE"
    CONTEXT = "CONTEXT"
    MECHANISTIC = "MECHANISTIC"
    TEMPORAL = "TEMPORAL"
    CONTRADICTION = "CONTRADICTION"
    METHODOLOGICAL = "METHODOLOGICAL"
    EVOLUTIONARY = "EVOLUTIONARY"
    UNTESTED_INTERACTION = "UNTESTED_INTERACTION"
    UNKNOWN_MECHANISM = "UNKNOWN_MECHANISM"
    TEMPORAL_DYNAMICS = "TEMPORAL_DYNAMICS"
    CONFLICTING_EVIDENCE = "CONFLICTING_EVIDENCE"
    METHODOLOGICAL_LIMITATION = "METHODOLOGICAL_LIMITATION"
    CONTEXT_GAP = "CONTEXT_GAP"


@dataclass
class PublicationRecord:
    """Scientific publication or preprint citation with traceable metadata."""
    pub_id: str                          # PMID or DOI
    title: str
    authors: List[str]
    journal: str
    year: int
    abstract: str
    doi: Optional[str] = None
    pmid: Optional[str] = None
    is_peer_reviewed: bool = True
    is_preprint: bool = False
    citation_count: int = 0
    url: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def dict(self) -> Dict[str, Any]:
        return self.to_dict()


@dataclass
class ScientificClaim:
    """Structured molecular claim extracted from literature and validated databases."""
    claim_id: str
    subject: str                         # e.g. "BRAF_V600E"
    predicate: str                       # e.g. "phosphorylates", "activates", "confers_resistance_to"
    object: str                          # e.g. "MEK1"
    context: Dict[str, str]              # e.g. {"tissue": "melanoma", "organism": "NCBI:9606"}
    evidence_records: List[str]          # Exact sentences or assay measurements
    publication_ids: List[str]           # Supporting PMIDs or DOIs
    experimental_methods: List[str]      # e.g. ["western_blot", "co_immunoprecipitation", "crystallography"]
    claim_status: str = ClaimStatus.EXPERIMENTAL_EVIDENCE.value
    confidence: float = 0.95
    limitations: List[str] = field(default_factory=list)

    @property
    def statement(self) -> str:
        return f"{self.subject} {self.predicate} {self.object}"

    @property
    def evidence_polarity(self) -> str:
        return "SUPPORTING"

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["statement"] = self.statement
        d["evidence_polarity"] = self.evidence_polarity
        return d

    def dict(self) -> Dict[str, Any]:
        return self.to_dict()


@dataclass
class ResearchGap:
    """Identified unresolved scientific question or biological coverage void."""
    gap_id: str
    gap_type: str
    title: str
    description: str
    affected_entities: List[str]
    evidence_density: float              # 0.0 (unexplored) to 1.0 (heavily studied)
    closest_studies: List[str]
    novelty_audit: Dict[str, Any]
    priority_score: float = 0.85

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def dict(self) -> Dict[str, Any]:
        return self.to_dict()


@dataclass
class ResearchHypothesis:
    """Falsifiable biological hypothesis with mechanism, rationale, and predictions."""
    hypothesis_id: str
    statement: str
    biological_rationale: str
    supporting_evidence: List[str]
    contradictory_evidence: List[str]
    novelty_assessment: str
    testable_predictions: List[str]
    falsification_criteria: List[str]
    experimental_plan: Dict[str, Any]
    priority_scores: Dict[str, float] = field(default_factory=dict)
    status: str = "PROPOSED"             # PROPOSED, SUPPORTED, REJECTED, REVISED
    composite_score: float = 0.85
    confidence: float = 0.90
    predictions: List[str] = field(default_factory=list)

    def __post_init__(self):
        if not self.predictions and self.testable_predictions:
            self.predictions = list(self.testable_predictions)
        elif not self.testable_predictions and self.predictions:
            self.testable_predictions = list(self.predictions)
        if self.priority_scores and not self.composite_score:
            self.composite_score = sum(self.priority_scores.values()) / max(1, len(self.priority_scores))

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["composite_score"] = self.composite_score
        d["confidence"] = self.confidence
        d["predictions"] = self.predictions
        return d

    def dict(self) -> Dict[str, Any]:
        return self.to_dict()


@dataclass
class ExperimentPlan:
    """Computational protocol specification with rigorous controls and intervention parameters."""
    experiment_id: str
    hypothesis_id: str
    target_engine: str = "CSE"           # "CSE", "DIT", "PaIE", "BRE"
    model_id: str = "default_model"
    intervention_type: str = "INHIBITION" # "KNOCKOUT", "INHIBITION", "OVEREXPRESSION", "DOSE_RESPONSE"
    target_entities: List[str] = field(default_factory=list)
    treatment_levels: List[float] = field(default_factory=lambda: [1.0])
    controls: Any = field(default_factory=dict) # Negative, vehicle, wild-type baseline
    outcome_observables: List[str] = field(default_factory=list)
    replicates: int = 5
    replicate_count: int = 5
    requires_human_approval: bool = False
    simulation_parameters: Dict[str, Any] = field(default_factory=dict)
    statistical_plan: Dict[str, Any] = field(default_factory=dict)
    is_approved: bool = False
    approval_token: Optional[str] = None

    def __post_init__(self):
        if self.replicate_count and not self.replicates:
            self.replicates = self.replicate_count
        elif self.replicates and not self.replicate_count:
            self.replicate_count = self.replicates

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["replicate_count"] = self.replicate_count
        d["requires_human_approval"] = self.requires_human_approval
        d["simulation_parameters"] = self.simulation_parameters
        return d

    def dict(self) -> Dict[str, Any]:
        return self.to_dict()


@dataclass
class ExperimentExecutionRecord:
    """Audit log and raw numerical results of an executed computational protocol."""
    execution_id: str
    experiment_id: str
    engine_used: str = "CSE"
    job_id: str = ""
    raw_results: Dict[str, Any] = field(default_factory=dict)
    summary_metrics: Dict[str, Any] = field(default_factory=dict)
    execution_time_seconds: float = 0.0
    random_seed: int = 42
    provenance_hash: str = ""
    status: str = "COMPLETED"
    success: bool = True
    replicate_outcomes: List[float] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["success"] = self.success
        d["replicate_outcomes"] = self.replicate_outcomes
        return d

    def dict(self) -> Dict[str, Any]:
        return self.to_dict()


@dataclass
class StatisticalAnalysisReport:
    """Hypothesis testing, effect size estimation, and uncertainty evaluation."""
    analysis_id: str
    experiment_id: str
    p_values: Dict[str, float] = field(default_factory=dict)
    fdr_corrected_q_values: Dict[str, float] = field(default_factory=dict)
    effect_sizes_cohen_d: Dict[str, float] = field(default_factory=dict)
    fold_changes: Dict[str, float] = field(default_factory=dict)
    test_used: str = "Welch t-test"
    power_estimate: float = 0.95
    is_statistically_significant: bool = True
    interpretation: str = ""
    hypothesis_id: str = ""
    p_value: float = 0.001
    effect_size: float = -2.0
    adjusted_p_value: float = 0.001
    statistically_significant: bool = True
    metric_means: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["hypothesis_id"] = self.hypothesis_id
        d["p_value"] = self.p_value
        d["effect_size"] = self.effect_size
        d["adjusted_p_value"] = self.adjusted_p_value
        d["statistically_significant"] = self.statistically_significant
        d["metric_means"] = self.metric_means
        return d

    def dict(self) -> Dict[str, Any]:
        return self.to_dict()


@dataclass
class AdversarialAuditReport:
    """Critical evaluation from the Critic Agent attempting to falsify discoveries."""
    audit_id: str
    hypothesis_id: str
    alternative_mechanisms: List[str] = field(default_factory=list)
    confounders_detected: List[str] = field(default_factory=list)
    parameter_sensitivity_concerns: List[str] = field(default_factory=list)
    data_leakage_detected: bool = False
    falsification_verdict: str = "SURVIVED_CHALLENGE"
    critique_summary: str = ""
    recommended_revisions: List[str] = field(default_factory=list)
    critic_agent: str = "CriticAgent"
    recommendation: str = "APPROVED_FOR_PUBLICATION"
    passed_audit: bool = True
    alternative_hypotheses_evaluated: List[str] = field(default_factory=list)
    leakage_detected: bool = False
    falsification_tested: bool = True
    robustness_score: float = 0.85
    critical_flaws: List[str] = field(default_factory=list)
    recommendation_notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["critic_agent"] = self.critic_agent
        d["recommendation"] = self.recommendation
        d["passed_audit"] = self.passed_audit
        d["alternative_hypotheses_evaluated"] = self.alternative_hypotheses_evaluated
        d["leakage_detected"] = self.leakage_detected
        d["falsification_tested"] = self.falsification_tested
        d["robustness_score"] = self.robustness_score
        d["critical_flaws"] = self.critical_flaws
        d["recommendation_notes"] = self.recommendation_notes
        return d

    def dict(self) -> Dict[str, Any]:
        return self.to_dict()


@dataclass
class ScientificManuscript:
    """Peer-review ready scientific discovery report generated from validated artifacts."""
    manuscript_id: str
    research_id: str = ""
    title: str = ""
    abstract: str = ""
    background: str = ""
    literature_review: str = ""
    research_gap: str = ""
    hypotheses: str = ""
    methods: str = ""
    results: str = ""
    statistical_analysis: str = ""
    adversarial_discussion: str = ""
    limitations: Any = ""
    conclusions: str = ""
    references: List[Any] = field(default_factory=list)
    figures: List[Dict[str, Any]] = field(default_factory=list)
    reproducibility_statement: str = ""
    is_human_reviewed: bool = False
    investigation_id: str = ""
    authors: List[str] = field(default_factory=list)
    introduction: str = ""
    discussion: str = ""
    tables: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["investigation_id"] = self.investigation_id or self.research_id
        d["authors"] = self.authors
        d["introduction"] = self.introduction
        d["discussion"] = self.discussion
        d["tables"] = self.tables
        return d

    def dict(self) -> Dict[str, Any]:
        return self.to_dict()


@dataclass
class ReproducibilityPackage:
    """Cryptographic manifest and artifacts for exact workflow replay."""
    package_id: str
    research_id: str = ""
    git_commit_hash: str = "6b24ebe"
    model_versions: Dict[str, str] = field(default_factory=dict)
    dataset_hashes: Dict[str, str] = field(default_factory=dict)
    random_seeds: List[int] = field(default_factory=list)
    environment_specs: Dict[str, str] = field(default_factory=dict)
    verification_digest: str = ""
    investigation_id: str = ""
    manifest: Dict[str, Any] = field(default_factory=dict)
    environment_spec: Dict[str, Any] = field(default_factory=dict)
    dataset_uris: List[str] = field(default_factory=list)
    code_commit_hash: str = "6b24ebe"
    data_hash: str = ""
    config_hash: str = ""

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["investigation_id"] = self.investigation_id or self.research_id
        d["manifest"] = self.manifest
        d["environment_spec"] = self.environment_spec
        d["dataset_uris"] = self.dataset_uris
        d["code_commit_hash"] = self.code_commit_hash
        d["data_hash"] = self.data_hash
        d["config_hash"] = self.config_hash
        return d

    def dict(self) -> Dict[str, Any]:
        return self.to_dict()



@dataclass
class ResearchInvestigation:
    """Master stateful container for an entire autonomous scientific discovery project."""
    research_id: str = ""
    research_question: str = ""
    domain: str = "oncology"
    organism: str = "NCBI:9606"
    context: Dict[str, str] = field(default_factory=dict)
    state: str = ResearchState.RESEARCH_CREATED.value
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    objectives: List[str] = field(default_factory=list)
    constraints: Dict[str, Any] = field(default_factory=dict)
    publications: List[PublicationRecord] = field(default_factory=list)
    claims: List[ScientificClaim] = field(default_factory=list)
    gaps: List[ResearchGap] = field(default_factory=list)
    hypotheses: List[ResearchHypothesis] = field(default_factory=list)
    experiments: List[ExperimentPlan] = field(default_factory=list)
    executions: List[ExperimentExecutionRecord] = field(default_factory=list)
    statistical_reports: List[StatisticalAnalysisReport] = field(default_factory=list)
    adversarial_audits: List[AdversarialAuditReport] = field(default_factory=list)
    manuscript: Optional[ScientificManuscript] = None
    reproducibility_package: Optional[ReproducibilityPackage] = None
    audit_timeline: List[Dict[str, Any]] = field(default_factory=list)
    title: str = ""
    investigation_id: str = ""
    primary_entities: List[str] = field(default_factory=list)
    context_organism: str = "Homo sapiens"
    state_history: List[Dict[str, Any]] = field(default_factory=list)

    def __post_init__(self):
        if not self.research_id and self.investigation_id:
            self.research_id = self.investigation_id
        elif not self.investigation_id and self.research_id:
            self.investigation_id = self.research_id


    def log_state_transition(self, new_state: str, agent: str, notes: str = "") -> None:
        self.state = new_state
        self.updated_at = datetime.now(timezone.utc).isoformat()
        self.audit_timeline.append({
            "timestamp": self.updated_at,
            "new_state": new_state,
            "agent": agent,
            "notes": notes,
        })

    def to_dict(self) -> Dict[str, Any]:
        return {
            "research_id": self.research_id,
            "investigation_id": self.investigation_id or self.research_id,
            "title": self.title,
            "research_question": self.research_question,
            "domain": self.domain,
            "organism": self.organism,
            "context": self.context,
            "state": self.state,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "objectives": self.objectives,
            "constraints": self.constraints,
            "primary_entities": self.primary_entities,
            "context_organism": self.context_organism,
            "state_history": self.state_history,
            "publications": [p.to_dict() for p in self.publications],
            "claims": [c.to_dict() for c in self.claims],
            "gaps": [g.to_dict() for g in self.gaps],
            "hypotheses": [h.to_dict() for h in self.hypotheses],
            "experiments": [e.to_dict() for e in self.experiments],
            "executions": [x.to_dict() for x in self.executions],
            "statistical_reports": [s.to_dict() for s in self.statistical_reports],
            "adversarial_audits": [a.to_dict() for a in self.adversarial_audits],
            "manuscript": self.manuscript.to_dict() if self.manuscript else None,
            "reproducibility_package": self.reproducibility_package.to_dict() if self.reproducibility_package else None,
            "audit_timeline": self.audit_timeline,
        }

    def dict(self) -> Dict[str, Any]:
        return self.to_dict()

