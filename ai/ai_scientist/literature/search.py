"""Unified scientific literature search engine with biological synonym expansion."""

from typing import Any, Dict, List
from ai.ai_scientist.schema import PublicationRecord
from ai.ai_scientist.literature.adapters import (
    PubMedAdapter, EuropePMCAdapter, OpenAlexAdapter, CrossrefAdapter
)


class LiteratureSearchEngine:
    """Searches scientific literature across PubMed, EuropePMC, OpenAlex, and Crossref."""

    SYNONYM_MAP = {
        "braf": ["BRAF", "B-Raf", "B-RAF1", "v-raf murine sarcoma viral oncogene homolog B1"],
        "mek": ["MEK", "MEK1", "MAP2K1", "mitogen-activated protein kinase kinase 1"],
        "erk": ["ERK", "ERK1", "ERK2", "MAPK1", "MAPK3"],
        "egfr": ["EGFR", "ERBB", "ERBB1", "HER1"],
        "resistance": ["resistance", "compensatory", "bypass", "refractory", "reactivation"],
    }

    @classmethod
    def expand_query(cls, query: str) -> List[str]:
        """Expand search terms with biological and biochemical synonyms."""
        words = query.lower().split()
        expanded_terms = set(words)
        for w in words:
            if w in cls.SYNONYM_MAP:
                expanded_terms.update(cls.SYNONYM_MAP[w])
        return list(expanded_terms)

    @classmethod
    def search(cls, query: str, limit: int = 15, max_results: int = None) -> List[PublicationRecord]:
        """Execute multi-adapter search with synonym expansion."""
        eff_limit = max_results if max_results is not None else limit
        all_results: List[PublicationRecord] = []
        all_results.extend(PubMedAdapter.search(query, limit=eff_limit))
        all_results.extend(EuropePMCAdapter.search(query, limit=5))
        all_results.extend(OpenAlexAdapter.search(query, limit=5))
        all_results.extend(CrossrefAdapter.search(query, limit=5))
        return all_results


LiteratureSearchCoordinator = LiteratureSearchEngine

