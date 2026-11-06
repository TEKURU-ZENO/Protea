"""
PROTEA PaIE Ingestion Package
"""

from ai.pathway_intelligence.ingestion.reactome import ReactomeAdapter
from ai.pathway_intelligence.ingestion.kegg import KEGGAdapter, WikiPathwaysAdapter, PathwayCommonsAdapter

__all__ = [
    "ReactomeAdapter",
    "KEGGAdapter",
    "WikiPathwaysAdapter",
    "PathwayCommonsAdapter"
]
