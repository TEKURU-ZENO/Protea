from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/protein", tags=["Protein Intelligence"])

class ProteinIngestion(BaseModel):
    uniprot_id: str
    sequence: str

@router.post("/ingest")
def ingest_protein(payload: ProteinIngestion):
    # Stub response matching Phase 2 deliverables
    if len(payload.sequence) < 10:
         raise HTTPException(status_code=400, detail="Protein sequence too short")
    return {
        "status": "success",
        "message": "Protein preprocessed successfully.",
        "protein_id": payload.uniprot_id,
        "sequence_length": len(payload.sequence),
        "embeddings": {
            "esm_2": f"Pending Phase 2 model-serving execution. Output dimensions will be 1024-D.",
            "protbert": "Pending Phase 2 model-serving execution."
        }
    }
