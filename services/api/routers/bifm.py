"""
PROTEA Phase 12: Biological Intelligence Foundation Model (BIFM) - API Router
Provides comprehensive REST endpoints connecting universal representations,
multimodal encoders, multi-task predictions, world model forecasting,
counterfactual interventions, and autonomous scientific investigations.
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel, Field

from services.api.services.bifm_service import BIFMService

router = APIRouter(prefix="/bifm", tags=["Biological Intelligence Foundation Model (BIFM)"])
service = BIFMService()


# --- Pydantic Request Models ---

class EncodeEntityRequest(BaseModel):
    entity_id: str = Field(..., description="Unique entity identifier (e.g. uniprot:P15056 or BRAF)")
    entity_type: str = Field("protein", description="Biological domain (protein, gene, metabolite, etc.)")
    modality: str = Field("sequence", description="Modality (sequence, structure, interaction, omics, etc.)")
    raw_input: Any = Field(..., description="Raw sequence, graph, structure, or matrix data")
    organism_id: str = Field("9606", description="NCBI taxonomy ID")
    context: Optional[Dict[str, Any]] = Field(None, description="Biological context dictionary")


class AlignEntityRequest(BaseModel):
    entity_id: str = Field(..., description="Entity identifier whose available modalities will be fused")


class ImputeModalityRequest(BaseModel):
    entity_id: str = Field(..., description="Entity identifier")
    target_modality: str = Field("phosphoproteomics", description="Missing modality to impute")


class ContextualizeRequest(BaseModel):
    entity_id: str = Field(..., description="Entity identifier")
    context: Dict[str, Any] = Field(..., description="Conditioning context (tissue, cell type, disease, mutation)")


class PredictTaskRequest(BaseModel):
    task_name: str = Field("protein_function", description="Task name (protein_function, protein_interaction, etc.)")
    entity_id: str = Field(..., description="Focal biological entity")
    partner_id: Optional[str] = Field(None, description="Partner entity for interaction tasks")
    mutation: Optional[str] = Field(None, description="Mutation string for variant tasks, e.g. V600E")
    target_taxid: int = Field(10090, description="Target taxonomy ID for evolution transfer")


class BatchPredictRequest(BaseModel):
    requests: List[PredictTaskRequest] = Field(..., description="Batch list of prediction tasks")


class WorldModelPredictRequest(BaseModel):
    system_id: str = Field("sys_melanoma", description="Biological system state identifier")
    target_entity: str = Field("BRAF", description="Intervention target entity")
    intervention_type: str = Field("small_molecule_inhibition", description="Intervention type")
    magnitude: float = Field(0.10, description="Intervention magnitude (0.0=KO, 0.1=Inhibition)")
    steps: int = Field(3, description="Simulation steps")


class CounterfactualRequest(BaseModel):
    target_entity: str = Field("BRAF", description="Target gene/protein")
    intervention_type: str = Field("gene_knockout", description="Intervention type")
    magnitude: float = Field(0.0, description="Magnitude")


class ReasonRequest(BaseModel):
    question: str = Field(..., description="Biological or mechanistic research question")
    focal_gene: str = Field(..., description="Focal gene symbol")
    partner_gene: Optional[str] = Field(None, description="Partner gene symbol")
    context: Optional[Dict[str, Any]] = Field(None, description="Conditioning biological context")


class InvestigateRequest(BaseModel):
    research_question: str = Field(..., description="High-ambition research question")
    focal_gene: str = Field(..., description="Focal gene symbol")
    partner_gene: Optional[str] = Field(None, description="Partner gene symbol")


class AdapterSubmitRequest(BaseModel):
    domain: str = Field(..., description="Domain specialization (oncology, immunology, neuroscience)")
    task: str = Field(..., description="Task name")
    datasets: List[str] = Field(..., description="Training dataset IDs")


class AdapterEvaluateRequest(BaseModel):
    adapter_id: str = Field(..., description="Registered adapter ID")
    benchmark_pass_rate: float = Field(0.98, description="Benchmark regression pass rate (0.0 to 1.0)")


# --- REST Endpoints ---

# 1. Representation Layer
@router.post("/representations/encode", summary="Encode biological entity using modality-specific encoder")
async def encode_entity(payload: EncodeEntityRequest):
    return service.encode_entity(
        payload.entity_id,
        payload.entity_type,
        payload.modality,
        payload.raw_input,
        payload.context,
        payload.organism_id
    )


@router.get("/representations/{entity_id}", summary="Retrieve multimodal profile for an entity")
async def get_multimodal_profile(entity_id: str):
    prof = service.get_multimodal_profile(entity_id)
    if not prof:
        raise HTTPException(status_code=404, detail=f"Multimodal profile for '{entity_id}' not found.")
    return prof


@router.post("/representations/align", summary="Align and fuse multi-modal representations into unified space")
async def align_entity(payload: AlignEntityRequest):
    return service.align_entity_modalities(payload.entity_id)


@router.post("/representations/impute", summary="Impute missing modality vector with Bayesian uncertainty")
async def impute_modality(payload: ImputeModalityRequest):
    return service.impute_missing_modality(payload.entity_id, payload.target_modality)


# 2. Context Conditioning
@router.post("/contextualize", summary="Specialize universal representation with biological context via FiLM")
async def contextualize_entity(payload: ContextualizeRequest):
    return service.contextualize(payload.entity_id, payload.context)


# 3. Multi-Task Predictions
@router.post("/predict", summary="Execute specialized prediction task over shared BIFM representation")
async def predict_task(payload: PredictTaskRequest):
    return service.predict(
        payload.task_name,
        payload.entity_id,
        payload.partner_id,
        payload.mutation,
        payload.target_taxid
    )


@router.post("/predict/batch", summary="Batch multi-task predictions")
async def predict_batch(payload: BatchPredictRequest):
    results = [
        service.predict(
            req.task_name,
            req.entity_id,
            req.partner_id,
            req.mutation,
            req.target_taxid
        )
        for req in payload.requests
    ]
    return {"count": len(results), "predictions": results}


# 4. Biological World Model & Counterfactuals
@router.post("/world-model/predict", summary="Forecast biological system state transitions under intervention")
async def forecast_world_model(payload: WorldModelPredictRequest):
    return service.forecast_world_model(
        payload.system_id,
        payload.target_entity,
        payload.intervention_type,
        payload.magnitude,
        payload.steps
    )


@router.post("/counterfactuals", summary="Evaluate model-predicted counterfactual perturbation")
async def evaluate_counterfactual(payload: CounterfactualRequest):
    return service.evaluate_counterfactual(
        payload.target_entity,
        payload.intervention_type,
        payload.magnitude
    )


@router.post("/interventions/evaluate", summary="Evaluate intervention scenario across models")
async def evaluate_intervention(payload: CounterfactualRequest):
    return service.evaluate_counterfactual(
        payload.target_entity,
        payload.intervention_type,
        payload.magnitude
    )


# 5. Scientific Reasoning & Autonomous Research
@router.post("/reason", summary="Synthesize evidence-grounded scientific explanation and mechanisms")
async def reason_scientifically(payload: ReasonRequest):
    return service.reason(
        payload.question,
        payload.focal_gene,
        payload.partner_gene,
        payload.context
    )


@router.post("/research/investigate", summary="Launch autonomous ABDE scientific discovery investigation")
async def launch_investigation(payload: InvestigateRequest):
    return service.launch_investigation(
        payload.research_question,
        payload.focal_gene,
        payload.partner_gene
    )


# 6. Continual Learning & Governance
@router.post("/adaptation/submit", summary="Register parameter-efficient LoRA adaptation")
async def submit_adaptation(payload: AdapterSubmitRequest):
    return service.register_adapter(payload.domain, payload.task, payload.datasets)


@router.post("/adaptation/evaluate", summary="Audit adaptation release gate against regression benchmarks")
async def evaluate_adaptation(payload: AdapterEvaluateRequest):
    return service.audit_adapter(payload.adapter_id, payload.benchmark_pass_rate)


@router.get("/models", summary="List BIFM foundation models and release status")
async def list_models():
    card = service.get_model_card()
    return {"models": [card]}


@router.get("/models/{model_id}", summary="Retrieve model card and license manifest")
async def get_model_details(model_id: str):
    card = service.get_model_card()
    return card


@router.post("/models/{model_id}/release", summary="Promote model checkpoint to production")
async def release_model(model_id: str):
    return {"model_id": model_id, "status": "RELEASED_TO_PRODUCTION", "timestamp": "2026-11-08T00:00:00Z"}


@router.get("/benchmarks", summary="Run all 10 BIFM standardized scientific research benchmarks")
async def run_benchmarks():
    return service.run_benchmarks()
