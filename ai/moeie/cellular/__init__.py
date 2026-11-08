"""
PROTEA Single-Cell Intelligence Module
"""

from ai.moeie.cellular.cell_annotation import CellAnnotationEngine, REFERENCE_CELL_MARKERS
from ai.moeie.cellular.trajectory import TrajectoryEngine
from ai.moeie.cellular.cell_communication import CellCommunicationEngine, CURATED_LR_PAIRS

__all__ = [
    "CellAnnotationEngine",
    "REFERENCE_CELL_MARKERS",
    "TrajectoryEngine",
    "CellCommunicationEngine",
    "CURATED_LR_PAIRS"
]
