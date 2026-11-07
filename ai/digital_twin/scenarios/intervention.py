"""Intervention specification models."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional
from ai.digital_twin.schema import InterventionType


@dataclass
class InterventionSpec:
    """Specification of an in silico biological intervention."""
    intervention_type: str
    target_entities: List[str]
    strength: float = 1.0  # Fraction (e.g. 1.0 for complete knockout, 0.5 for knockdown)
    duration_hours: Optional[float] = None
    small_molecule_name: Optional[str] = None
    target_pathway: Optional[str] = None
