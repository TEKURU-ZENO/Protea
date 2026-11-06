"""
PROTEA PaIE Functional Annotation Package
"""

from ai.pathway_intelligence.annotation.gene_ontology import go_engine, GeneOntologyEngine
from ai.pathway_intelligence.annotation.functional_annotation import (
    annotation_manager,
    localization_mapper,
    FunctionalAnnotationManager,
    SubcellularLocalizationMapper
)

__all__ = [
    "go_engine",
    "GeneOntologyEngine",
    "annotation_manager",
    "localization_mapper",
    "FunctionalAnnotationManager",
    "SubcellularLocalizationMapper"
]
