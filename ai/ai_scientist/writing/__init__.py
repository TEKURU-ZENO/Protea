"""
PROTEA AI Scientist - Scientific Writing & Reporting Module
Manuscript generation, citation validation, publication figures, and evidence dossiers.
"""

from ai.ai_scientist.writing.citation_validator import CitationValidator
from ai.ai_scientist.writing.figure_generator import FigureGenerator
from ai.ai_scientist.writing.report_builder import ReportBuilder
from ai.ai_scientist.writing.manuscript_generator import ScientificManuscriptGenerator

__all__ = [
    "CitationValidator",
    "FigureGenerator",
    "ReportBuilder",
    "ScientificManuscriptGenerator",
]
