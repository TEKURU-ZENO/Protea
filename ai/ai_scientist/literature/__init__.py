"""Literature Intelligence Engine."""

from ai.ai_scientist.literature.search import LiteratureSearchEngine, LiteratureSearchCoordinator
from ai.ai_scientist.literature.deduplication import PublicationDeduplicator, LiteratureDeduplicator
from ai.ai_scientist.literature.fulltext_parser import FullTextParser
from ai.ai_scientist.literature.citation_graph import CitationGraphBuilder

__all__ = [
    "LiteratureSearchEngine",
    "LiteratureSearchCoordinator",
    "PublicationDeduplicator",
    "LiteratureDeduplicator",
    "FullTextParser",
    "CitationGraphBuilder",
]
