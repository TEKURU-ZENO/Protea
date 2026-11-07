"""
PROTEA Therapeutic Target Discovery Module
"""

from ai.mutation_therapeutics.target_discovery.druggability_analyzer import (
    DruggabilityAnalyzer,
    TARGET_POCKET_METRICS
)
from ai.mutation_therapeutics.target_discovery.target_prioritizer import (
    TargetPrioritizer,
    DEPMAP_TARGET_DATABASE
)

__all__ = [
    "DruggabilityAnalyzer",
    "TARGET_POCKET_METRICS",
    "TargetPrioritizer",
    "DEPMAP_TARGET_DATABASE"
]
