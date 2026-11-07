"""Literature source adapters."""

from ai.ai_scientist.literature.adapters.pubmed import PubMedAdapter
from ai.ai_scientist.literature.adapters.europe_pmc import EuropePMCAdapter
from ai.ai_scientist.literature.adapters.openalex import OpenAlexAdapter
from ai.ai_scientist.literature.adapters.crossref import CrossrefAdapter

__all__ = [
    "PubMedAdapter",
    "EuropePMCAdapter",
    "OpenAlexAdapter",
    "CrossrefAdapter",
]
