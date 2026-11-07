"""
PROTEA API - Biological Reasoning Engine (BRE) Router
Exposes production REST endpoints for biological question answering, mechanism reconstruction,
competing hypothesis generation, counterfactual simulation, and multi-agent workflows.
"""

from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
import uuid

from services.api.services.biological_reasoning_service import biological_reasoning_service

router = APIRouter(prefix="/reasoning", tags=["Biological Reasoning Engine (BRE)"])

# Request Schemas
class ReasoningQueryRequest(BaseModel):
    query: str = Field(..., example="A protein is downregulated in liver cancer. Which upstream regulators could explain this change?")
    tissue: Optional[str] = Field(None, example="liver")
    organism: Optional[str] = Field("Homo sapiens", example="Homo sapiens")

class MechanismReconstructRequest(BaseModel):
    chain: List[str] = Field(..., min_items=2, example=["MDM2", "TP53", "BAX", "CASP3"])

class IdentifyRegulatorsRequest(BaseModel):
    target: str = Field(..., example="TP53")
    observation: Optional[str] = Field("downregulated", example="downregulated")

class GenerateHypothesesRequest(BaseModel):
    query: str = Field(..., example="Why is TP53 downregulated in hepatic carcinoma?")
    max_count: Optional[int] = Field(3, ge=1, le=10)

class FuseEvidenceRequest(BaseModel):
    target: str = Field(..., example="TP53")

class CounterfactualRequest(BaseModel):
    target_protein: str = Field(..., example="TP53")
    perturbation_type: Optional[str] = Field("knockout", example="knockout") # knockout, knockdown, overexpression, inhibition
    tissue: Optional[str] = Field(None, example="liver")

class ValidateMechanismRequest(BaseModel):
    chain: List[str] = Field(..., min_items=2, example=["TP53", "BAX", "CASP3"])

class CompareExplanationsRequest(BaseModel):
    target: str = Field(..., example="TP53")
    competing_regulators: List[str] = Field(..., min_items=2, example=["MDM2", "ATM", "SIRT1"])


# 1. Execute full biological reasoning task
@router.post("/query")
def execute_reasoning_query(req: ReasoningQueryRequest):
    """Execute end-to-end biological question answering with multi-agent orchestration."""
    report = biological_reasoning_service.execute_reasoning_query(req.query)
    return report.model_dump()


# 2. Reconstruct molecular mechanism
@router.post("/mechanism/reconstruct")
def reconstruct_mechanism(req: MechanismReconstructRequest):
    """Reconstruct a multi-hop molecular chain with signed causality and compartment validation."""
    return biological_reasoning_service.reconstruct_mechanism(req.chain)


# 3. Identify candidate upstream regulators
@router.post("/regulators/identify")
def identify_regulators(req: IdentifyRegulatorsRequest):
    """Identify candidate upstream regulators explaining target overexpression or suppression."""
    return biological_reasoning_service.identify_regulators(req.target, req.observation or "downregulated")


# 4. Generate competing hypotheses
@router.post("/hypotheses/generate")
def generate_hypotheses(req: GenerateHypothesesRequest):
    """Formulate multiple competing, testable biological hypotheses."""
    return biological_reasoning_service.generate_hypotheses(req.query, req.max_count or 3)


# 5. Rank hypotheses by evidence
@router.post("/hypotheses/rank")
def rank_hypotheses(req: GenerateHypothesesRequest):
    """Rank competing hypotheses by composite evidence score, biological consistency, and uncertainty."""
    return biological_reasoning_service.rank_hypotheses(req.query)


# 6. Fuse multi-source evidence
@router.post("/evidence/fuse")
def fuse_evidence(req: FuseEvidenceRequest):
    """Fuse heterogeneous observations with source reliability profiles and deduplicated citations."""
    return biological_reasoning_service.fuse_evidence(req.target)


# 7. Counterfactual perturbation simulation
@router.post("/counterfactual/simulate")
def simulate_counterfactual(req: CounterfactualRequest):
    """Simulate in silico gene knockout, knockdown, or overexpression on downstream networks."""
    return biological_reasoning_service.simulate_counterfactual(
        target=req.target_protein,
        perturbation_type=req.perturbation_type or "knockout",
        tissue=req.tissue
    )


# 8. Downstream pathway impact analysis
@router.post("/pathways/impact")
def analyze_pathway_impact(req: CounterfactualRequest):
    """Analyze which downstream signaling pathways are affected by perturbing a target."""
    scenario = biological_reasoning_service.simulate_counterfactual(
        target=req.target_protein,
        perturbation_type=req.perturbation_type or "inhibition",
        tissue=req.tissue
    )
    return {
        "target": req.target_protein,
        "affected_pathways": scenario.get("affected_pathways", []),
        "perturbed_nodes_count": len(scenario.get("perturbed_nodes", {}))
    }


# 9. Validate proposed mechanism
@router.post("/validate")
def validate_mechanism(req: ValidateMechanismRequest):
    """Audit proposed mechanism for cellular compartment compatibility and reaction validity."""
    return biological_reasoning_service.validate_mechanism(req.chain)


# 10. Compare competing explanations
@router.post("/compare")
def compare_competing_explanations(req: CompareExplanationsRequest):
    """Contrast evidence strength and mechanism plausibility between alternative regulators."""
    comparisons = []
    for reg in req.competing_regulators:
        mech = biological_reasoning_service.reconstruct_mechanism([reg, req.target])
        val = biological_reasoning_service.validate_mechanism([reg, req.target])
        comparisons.append({
            "regulator": reg,
            "net_effect": mech.get("net_effect"),
            "confidence": mech.get("cumulative_confidence"),
            "is_valid": val.get("is_biologically_valid")
        })
    return {"target": req.target, "comparisons": comparisons}


# 11. Run orchestrated multi-agent workflow
@router.post("/agents/run")
def run_agents(req: ReasoningQueryRequest):
    """Run controlled multi-agent state machine with full provenance audit trace."""
    report = biological_reasoning_service.execute_reasoning_query(req.query)
    return {
        "report_id": report.report_id,
        "agent_trace_steps": [t.model_dump() for t in report.reasoning_trace],
        "executive_summary": report.executive_summary
    }


# 12. List available models & agents
@router.get("/models")
def get_reasoning_models():
    """Retrieve catalog of active reasoning engines, agents, and evidence sources."""
    return biological_reasoning_service.get_models()


# 13. Get reasoning result by ID
@router.get("/results/{result_id}")
def get_reasoning_result(result_id: str):
    """Retrieve complete reasoning report by report_id."""
    res = biological_reasoning_service.get_result(result_id)
    if not res:
        raise HTTPException(status_code=404, detail=f"Reasoning report '{result_id}' not found.")
    return res.model_dump()


# 14. Get reasoning provenance trace
@router.get("/results/{result_id}/trace")
def get_reasoning_trace(result_id: str):
    """Inspect detailed provenance and agent step trace for an execution."""
    res = biological_reasoning_service.get_result(result_id)
    if not res:
        raise HTTPException(status_code=404, detail=f"Reasoning report '{result_id}' not found.")
    return {
        "report_id": result_id,
        "trace": [t.model_dump() for t in res.reasoning_trace]
    }
