from fastapi import APIRouter, Depends
from services.api.core.config import settings

router = APIRouter(prefix="/system", tags=["System"])

@router.get("/info")
def get_system_info():
    return {
        "platform": "PROTEA AI-Native Computational Interactomics Platform",
        "version": "2.0.0",
        "environment": settings.ENVIRONMENT,
        "debug_mode": settings.DEBUG,
        "api_docs_url": "/docs"
    }
