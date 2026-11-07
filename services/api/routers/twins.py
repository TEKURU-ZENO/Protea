"""FastAPI Router for Digital Interactome Twin (DIT) endpoints."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from services.api.services.digital_twin_service import DigitalTwinService

router = APIRouter(prefix="/twins", tags=["Digital Interactome Twin"])
service = DigitalTwinService()


class CreateTwinRequest(BaseModel):
    name: str = Field(default="Human Liver Hepatocyte Twin")
    organism: str = Field(default="NCBI:9606")
    tissue: str = Field(default="liver")
    cell_type: str = Field(default="hepatocyte")
    condition: str = Field(default="healthy")
    mode: str = Field(default="hybrid")


class BuildInteractomeRequest(BaseModel):
    twin_id: Optional[str] = None
    min_expression: float = 1.0


class IntegrateOmicsRequest(BaseModel):
    twin_id: Optional[str] = None
    observations: List[Dict[str, Any]] = Field(default_factory=list)


class UpdateTwinRequest(BaseModel):
    twin_id: Optional[str] = None
    version_tag: Optional[str] = None
    observations: List[Dict[str, Any]] = Field(default_factory=list)


class EstimateStateRequest(BaseModel):
    twin_id: Optional[str] = None


class CompareTwinsRequest(BaseModel):
    twin_id: Optional[str] = None
    baseline_version_id: Optional[str] = None
    perturbed_version_id: Optional[str] = None


class TemporalAnalysisRequest(BaseModel):
    twin_id: Optional[str] = None


class CreateScenarioRequest(BaseModel):
    twin_id: Optional[str] = None
    name: str = Field(default="Target Knockout Scenario")
    intervention_type: str = Field(default="KNOCKDOWN")
    target_entities: List[str] = Field(default_factory=lambda: ["METTL3"])
    strength: float = 1.0
    description: str = ""


class ValidateTwinRequest(BaseModel):
    twin_id: Optional[str] = None
    version_id: Optional[str] = None


# 1. Twin Creation & Lifecycle
@router.post("/create", summary="Create a new digital twin instance")
def create_twin(req: CreateTwinRequest):
    return service.create_twin(req.dict())


@router.post("/initialize", summary="Initialize twin from biological knowledge & context")
def initialize_twin(req: CreateTwinRequest):
    return service.create_twin(req.dict())


@router.get("/", summary="List all registered biological digital twins")
def list_twins():
    twins = service.list_twins()
    return {"twins": twins, "count": len(twins)}


@router.get("/benchmarks", summary="Execute and retrieve digital twin benchmark metrics")
def get_benchmarks():
    return service.run_benchmarks()


@router.get("/{twin_id}", summary="Retrieve digital twin metadata")
def get_twin(twin_id: str):
    res = service.get_twin(twin_id)
    if not res:
        raise HTTPException(status_code=404, detail="Twin not found")
    return res


@router.get("/{twin_id}/versions", summary="Retrieve version history for a twin")
def get_versions(twin_id: str):
    return {"twin_id": twin_id, "versions": service.get_versions(twin_id)}


@router.get("/{twin_id}/state", summary="Retrieve multi-attribute molecular state vector")
def get_state(twin_id: str, version_id: Optional[str] = Query(None)):
    return service.get_molecular_state(twin_id, version_id)


@router.get("/{twin_id}/network", summary="Retrieve context-filtered interactome topology")
def get_network(twin_id: str, version_id: Optional[str] = Query(None)):
    return service.get_network(twin_id, version_id)


@router.get("/{twin_id}/timeline", summary="Retrieve dynamic longitudinal state history")
def get_timeline(twin_id: str, version_id: Optional[str] = Query(None)):
    return {"twin_id": twin_id, "timeline": service.get_timeline(twin_id, version_id)}


@router.get("/{twin_id}/scenarios", summary="List scenario branches for a twin")
def get_scenarios(twin_id: str, version_id: Optional[str] = Query(None)):
    return {"twin_id": twin_id, "scenarios": service.get_scenarios(twin_id, version_id)}


@router.get("/{twin_id}/validation", summary="Retrieve multi-dimensional validation fidelity report")
def get_validation(twin_id: str, version_id: Optional[str] = Query(None)):
    return service.get_validation(twin_id, version_id)


# 2. Operations & Calculations
@router.post("/build-interactome", summary="Assemble context-aware interactome")
def build_interactome(req: BuildInteractomeRequest):
    return service.build_interactome(req.dict())


@router.post("/integrate-omics", summary="Integrate multi-omics empirical observations")
def integrate_omics(req: IntegrateOmicsRequest):
    return service.integrate_omics(req.dict())


@router.post("/update", summary="Assimilate new observations into a child version")
def update_twin(req: UpdateTwinRequest):
    return service.update_twin(req.dict())


@router.post("/estimate-state", summary="Estimate missing or latent state variables")
def estimate_state(req: EstimateStateRequest):
    return service.estimate_state(req.dict())


@router.post("/compare", summary="Compare two twin states (e.g. healthy vs disease)")
def compare_twins(req: CompareTwinsRequest):
    return service.compare_twins(req.dict())


@router.post("/temporal-analysis", summary="Analyze trajectory inflection points")
def temporal_analysis(req: TemporalAnalysisRequest):
    return service.temporal_analysis(req.dict())


@router.post("/scenarios", summary="Create and execute an in silico intervention scenario")
def create_scenario(req: CreateScenarioRequest):
    return service.create_scenario(req.dict())


@router.post("/scenarios/{scenario_id}/run", summary="Re-run an existing scenario branch")
def run_scenario(scenario_id: str, req: CreateScenarioRequest):
    return service.create_scenario(req.dict())


@router.post("/validate", summary="Run multi-dimensional fidelity checks on a twin")
def validate_twin(req: ValidateTwinRequest):
    return service.validate_twin(req.dict())
