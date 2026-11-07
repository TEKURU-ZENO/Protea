"""
PROTEA AI Scientist - Literature Intelligence Agent
Retrieves, deduplicates, and structures scientific literature across PubMed, Europe PMC, and OpenAlex.
"""

from typing import Dict, Any, List
from ai.ai_scientist.literature.search import LiteratureSearchCoordinator
from ai.ai_scientist.literature.deduplication import LiteratureDeduplicator
from ai.ai_scientist.literature.citation_graph import CitationGraphBuilder
from ai.ai_scientist.schema import PublicationRecord


class LiteratureAgent:
    """
    Autonomous agent responsible for literature search, deduplication, and citation topology.
    """

    def __init__(self):
        self.search_coordinator = LiteratureSearchCoordinator()
        self.deduplicator = LiteratureDeduplicator()
        self.citation_builder = CitationGraphBuilder()

    def run(self, query: str, max_records: int = 15) -> Dict[str, Any]:
        """
        Executes end-to-end literature retrieval workflow.
        """
        raw_pubs = self.search_coordinator.search(query=query, max_results=max_records)
        dedup_result = self.deduplicator.deduplicate(raw_pubs)
        unique_pubs = dedup_result["unique_records"]

        citation_graph = self.citation_builder.build_graph(unique_pubs)

        return {
            "query": query,
            "total_found": len(raw_pubs),
            "unique_count": len(unique_pubs),
            "peer_reviewed_count": dedup_result["peer_reviewed_count"],
            "preprint_count": dedup_result["preprint_count"],
            "publications": [p.dict() if hasattr(p, "dict") else p for p in unique_pubs],
            "citation_graph": citation_graph,
        }
