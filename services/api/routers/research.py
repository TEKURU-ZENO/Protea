"""
PROTEA Research Router - AI Scientist (Autonomous Biological Discovery Engine)
Exposes research investigation endpoints, literature retrieval, gap detection, hypothesis generation,
experiment planning, execution, statistical analysis, adversarial critique, and manuscript generation.
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from services.api.services.ai_scientist_service import ai_scientist_service

router = APIRouter(prefix="/research", tags=["AI Scientist"])


# --- Request & Response Models ---

class CreateInvestigationRequest(BaseModel):
    research_question: str
    investigator: str = "PROTEA_User"
    max_compute_budget_minutes: float = 30.0
    require_human_approval: bool = True


class AnalyzeQuestionRequest(BaseModel):
    question: str


class LiteratureSearchRequest(BaseModel):
    query: str
    max_results: int = 15


class SynthesizeKnowledgeRequest(BaseModel):
    publications: List[Dict[str, Any]]


class DetectGapsRequest(BaseModel):
    claims: List[Dict[str, Any]] = Field(default_factory=list)
    entities: List[str] = Field(default_factory=list)


class AuditNoveltyRequest(BaseModel):
    proposed_discovery: str
    publications: List[Dict[str, Any]] = Field(default_factory=list)


class GenerateHypothesesRequest(BaseModel):
    gap_id: str
    gap_description: str
    claims: List[Dict[str, Any]] = Field(default_factory=list)
    entities: List[str] = Field(default_factory=list)


class RankHypothesesRequest(BaseModel):
    hypotheses: List[Dict[str, Any]]


class DesignExperimentRequest(BaseModel):
    hypothesis: Dict[str, Any]
    target_entities: List[str]
    engine: str = "CellularSimulationEngine"


class ApproveExperimentRequest(BaseModel):
    investigation_id: str
    approved: bool = True


class ExecuteExperimentRequest(BaseModel):
    experiment_plan: Dict[str, Any]
    user_approved: bool = True


class RunAnalysisRequest(BaseModel):
    experiment_id: str
    hypothesis_id: str
    intervention_replicates: List[float]
    control_replicates: List[float]


class ReviewCriticismRequest(BaseModel):
    hypothesis_id: str
    hypothesis_statement: str
    falsification_criteria: List[str]
    experiment_design: Dict[str, Any]
    experimental_results: Dict[str, Any]
    pathway_context: Dict[str, Any] = Field(default_factory=dict)


class GenerateReportsRequest(BaseModel):
    investigation_id: str
    research_question: str
    gap_description: str
    primary_hypothesis: Dict[str, Any]
    experiment_plan: Dict[str, Any]
    statistical_report: Dict[str, Any]
    adversarial_report: Dict[str, Any]
    retrieved_publications: List[Dict[str, Any]] = Field(default_factory=list)
    random_seeds: List[int] = Field(default_factory=lambda: [42, 101, 2024])


class RunFullInvestigationRequest(BaseModel):
    research_question: str
    auto_approve_simulation: bool = True


class StepInvestigationRequest(BaseModel):
    investigation_id: str
    user_approved: bool = False


# --- Endpoints ---

@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_investigation(payload: CreateInvestigationRequest):
    """Initializes a new autonomous biological discovery investigation."""
    try:
        return ai_scientist_service.create_investigation(
            research_question=payload.research_question,
            investigator=payload.investigator,
            max_compute_budget_minutes=payload.max_compute_budget_minutes,
            require_human_approval=payload.require_human_approval,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/investigations")
async def list_investigations():
    """Returns all registered research investigations."""
    return ai_scientist_service.list_investigations()


@router.get("/investigations/{investigation_id}")
async def get_investigation(investigation_id: str):
    """Retrieves full details and trajectory of an investigation."""
    inv = ai_scientist_service.get_investigation(investigation_id)
    if not inv:
        raise HTTPException(status_code=404, detail="Investigation not found")
    return inv


@router.post("/question/analyze")
async def analyze_question(payload: AnalyzeQuestionRequest):
    """Parses scientific question into domain, entities, and feasibility score."""
    try:
        return ai_scientist_service.analyze_question(payload.question)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/literature/search")
async def search_literature(payload: LiteratureSearchRequest):
    """Searches scientific literature across PubMed, Europe PMC, and OpenAlex."""
    try:
        return ai_scientist_service.search_literature(query=payload.query, max_results=payload.max_results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/literature/synthesize")
async def synthesize_knowledge(payload: SynthesizeKnowledgeRequest):
    """Extracts claims and constructs evidence graph from literature."""
    try:
        return ai_scientist_service.synthesize_knowledge(payload.publications)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/gaps/detect")
async def detect_gaps(payload: DetectGapsRequest):
    """Detects research gaps across 7 biological taxonomy categories."""
    try:
        return ai_scientist_service.detect_gaps(payload.claims, payload.entities)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/novelty/audit")
async def audit_novelty(payload: AuditNoveltyRequest):
    """Performs systematic prior art audit against claims and publications."""
    try:
        return ai_scientist_service.audit_novelty(payload.proposed_discovery, payload.publications)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/hypotheses/generate")
async def generate_hypotheses(payload: GenerateHypothesesRequest):
    """Generates competing, falsifiable hypotheses with quantitative predictions."""
    try:
        return ai_scientist_service.generate_hypotheses(
            gap_id=payload.gap_id,
            gap_description=payload.gap_description,
            claims=payload.claims,
            entities=payload.entities,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/hypotheses/rank")
async def rank_hypotheses(payload: RankHypothesesRequest):
    """Ranks hypotheses using multi-criteria weighted scoring."""
    try:
        return ai_scientist_service.rank_hypotheses(payload.hypotheses)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/experiments/design")
async def design_experiment(payload: DesignExperimentRequest):
    """Designs controlled computational experiment with positive/negative/vehicle controls."""
    try:
        return ai_scientist_service.design_experiment(
            hypothesis=payload.hypothesis,
            target_entities=payload.target_entities,
            engine=payload.engine,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/experiments/approve")
async def approve_experiment(payload: ApproveExperimentRequest):
    """Human approval gate for in-silico experiment execution."""
    try:
        return ai_scientist_service.approve_experiment(
            investigation_id=payload.investigation_id,
            approved=payload.approved,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/experiments/execute")
async def execute_experiment(payload: ExecuteExperimentRequest):
    """Executes experiment across PROTEA engines with replicate tracking."""
    try:
        return ai_scientist_service.execute_experiment(
            experiment_plan=payload.experiment_plan,
            user_approved=payload.user_approved,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analysis/run")
async def run_analysis(payload: RunAnalysisRequest):
    """Runs statistical significance tests, FDR correction, and effect size calculation."""
    try:
        return ai_scientist_service.run_analysis(
            experiment_id=payload.experiment_id,
            hypothesis_id=payload.hypothesis_id,
            intervention_replicates=payload.intervention_replicates,
            control_replicates=payload.control_replicates,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/criticism/review")
async def review_criticism(payload: ReviewCriticismRequest):
    """Conducts adversarial Critic Agent audit on hypotheses, confounders, and data leakage."""
    try:
        return ai_scientist_service.review_criticism(
            hypothesis_id=payload.hypothesis_id,
            hypothesis_statement=payload.hypothesis_statement,
            falsification_criteria=payload.falsification_criteria,
            experiment_design=payload.experiment_design,
            experimental_results=payload.experimental_results,
            pathway_context=payload.pathway_context,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reports/generate")
async def generate_reports(payload: GenerateReportsRequest):
    """Generates publication-ready scientific manuscript, figures, and reproducibility package."""
    try:
        return ai_scientist_service.generate_reports(
            investigation_id=payload.investigation_id,
            research_question=payload.research_question,
            gap_description=payload.gap_description,
            primary_hypothesis=payload.primary_hypothesis,
            experiment_plan=payload.experiment_plan,
            statistical_report=payload.statistical_report,
            adversarial_report=payload.adversarial_report,
            retrieved_publications=payload.retrieved_publications,
            random_seeds=payload.random_seeds,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/step")
async def step_investigation(payload: StepInvestigationRequest):
    """Steps the investigation state machine forward by one transition."""
    try:
        return ai_scientist_service.orchestrator.step(
            investigation_id=payload.investigation_id,
            user_approved=payload.user_approved,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/run")
async def run_full_investigation(payload: RunFullInvestigationRequest):
    """Executes the complete 14-state scientific discovery loop autonomously end-to-end."""
    try:
        return ai_scientist_service.run_full_investigation(
            research_question=payload.research_question,
            auto_approve_simulation=payload.auto_approve_simulation,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
