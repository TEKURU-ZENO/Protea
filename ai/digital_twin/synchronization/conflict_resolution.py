"""Conflict Resolution Engine for discordant multi-sample measurements."""

from __future__ import annotations

import logging
from typing import Any, Dict, List
from ai.digital_twin.schema import MolecularObservation

logger = logging.getLogger(__name__)


class ConflictResolver:
    """Reconciles conflicting empirical observations from disparate studies or replicate discordance."""

    def resolve_conflicts(
        self,
        observations: List[MolecularObservation]
    ) -> List[MolecularObservation]:
        """Groups observations by entity and measurement type and resolves discordant values."""
        groups: Dict[tuple[str, str], List[MolecularObservation]] = {}
        for obs in observations:
            key = (obs.entity_id, obs.measurement_type)
            if key not in groups:
                groups[key] = []
            groups[key].append(obs)

        resolved: List[MolecularObservation] = []
        for (entity, m_type), group in groups.items():
            if len(group) == 1:
                resolved.append(group[0])
                continue

            # Multi-observation reconciliation via inverse-variance weighting
            weights = [1.0 / max(0.01, (o.uncertainty or 0.1) ** 2) for o in group]
            total_weight = sum(weights)
            weighted_val = sum((o.value or 0.0) * w for o, w in zip(group, weights)) / total_weight

            rep = group[0]
            rep.value = round(weighted_val, 3)
            rep.uncertainty = round(1.0 / (total_weight ** 0.5), 3)
            rep.provenance_id = f"RECONCILED:{len(group)}_SOURCES"
            resolved.append(rep)

        return resolved
