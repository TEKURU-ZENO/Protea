"""
PROTEA Multi-Omics Ingestion Module
"""

from ai.moeie.ingestion.adapters import ModalityIngestionAdapters
from ai.moeie.ingestion.identifiers import CrossSpeciesIdentifierResolver, CURATED_ID_MAP
from ai.moeie.ingestion.registry import DatasetRegistry

__all__ = [
    "ModalityIngestionAdapters",
    "CrossSpeciesIdentifierResolver",
    "CURATED_ID_MAP",
    "DatasetRegistry"
]
