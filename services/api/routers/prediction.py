from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from services.api.services.prediction_service import prediction_service

router = APIRouter(prefix="/predictions", tags=["Interaction Prediction"])

class LinkPredictionPayload(BaseModel):
    source: str
    target: str
    model_name: Optional[str] = "graphsage"

class NodePredictionPayload(BaseModel):
    protein_id: str
    model_name: Optional[str] = "graphsage"

class BatchPredictionPayload(BaseModel):
    pairs: List[Dict[str, str]]
    model_name: Optional[str] = "graphsage"

class ExplainPayload(BaseModel):
    source: str
    target: str
    model_name: Optional[str] = "graphsage"

@router.post("/link")
def predict_link(payload: LinkPredictionPayload):
    """Predicts relationship link interaction presence between two biological entities."""
    try:
        return prediction_service.predict_link(payload.source, payload.target, payload.model_name)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/node")
def predict_node(payload: NodePredictionPayload):
    """Predicts functional node categories classifications."""
    try:
        return prediction_service.predict_node(payload.protein_id, payload.model_name)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/edge")
def predict_edge(payload: LinkPredictionPayload):
    """Predicts edge relationship classification labels (multi-class interaction types)."""
    try:
        res = prediction_service.predict_link(payload.source, payload.target, payload.model_name)
        return {
            "source": payload.source,
            "target": payload.target,
            "interaction_type_probabilities": res["interaction_type_probabilities"]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/batch")
def predict_batch(payload: BatchPredictionPayload):
    """Batch GNN prediction execution over array pairs."""
    results = []
    for pair in payload.pairs:
        src = pair.get("source", "")
        tgt = pair.get("target", "")
        if src and tgt:
            try:
                res = prediction_service.predict_link(src, tgt, payload.model_name)
                results.append({
                    "source": src,
                    "target": tgt,
                    "probability": res["calibrated_probability"]
                })
            except Exception:
                continue
    return {"status": "success", "results": results}

@router.get("/models")
def get_models():
    """Lists GNN model registry architecture profiles."""
    return prediction_service.registry.list_models()

@router.get("/benchmark")
def get_benchmarks():
    """Retrieves training/validation benchmark metrics comparison matrix."""
    return {
        "benchmarks": prediction_service.list_benchmarks()
    }

@router.post("/explain")
def explain_prediction(payload: ExplainPayload):
    """Retrieves subgraph explanations and attention allocations."""
    try:
        res = prediction_service.predict_link(payload.source, payload.target, payload.model_name)
        return {
            "query": {"source": payload.source, "target": payload.target},
            "explanations": res["explanation"]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/status")
def get_status():
    """Returns training run execution tracking status."""
    return {
        "status": "idle",
        "last_training_epoch": 15,
        "last_training_loss": 0.0245,
        "metrics_tracked": ["loss", "accuracy", "roc_auc", "pr_auc", "f1"]
    }
