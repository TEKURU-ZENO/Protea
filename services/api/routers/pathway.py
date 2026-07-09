from fastapi import APIRouter

router = APIRouter(prefix="/pathway", tags=["Pathway Intelligence"])

@router.get("/enrichment/{pathway_id}")
def get_pathway_enrichment(pathway_id: str):
    # Stub response matching Phase 5 deliverables
    return {
        "pathway_id": pathway_id,
        "name": f"Mock enriched pathway {pathway_id}",
        "go_terms": ["GO:0006468", "GO:0000166"],
        "p_value": 0.00034,
        "active_nodes": ["P53", "AKT1", "MTOR"],
        "message": "Pathway discovery, community detection and GO mapping will be available in Phase 5."
    }
