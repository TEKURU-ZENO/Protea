"""State Updater creating synchronized versioned releases of the twin."""

from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from ai.digital_twin.schema import DigitalTwin, MolecularObservation, MolecularState, TwinVersion
from ai.digital_twin.synchronization.assimilation import DataAssimilator
from ai.digital_twin.synchronization.conflict_resolution import ConflictResolver

logger = logging.getLogger(__name__)


class TwinStateUpdater:
    """Orchestrates state assimilation and creates immutable child twin versions."""

    def __init__(self) -> None:
        self.conflict_resolver = ConflictResolver()
        self.assimilator = DataAssimilator()

    def update_twin_with_observations(
        self,
        twin: DigitalTwin,
        new_observations: List[MolecularObservation],
        new_version_tag: Optional[str] = None
    ) -> TwinVersion:
        """Assimilates new observations into the active version and registers an immutable child version."""
        parent_version = twin.get_active_version()
        if not parent_version:
            raise ValueError(f"Twin {twin.twin_id} has no active version to update.")

        # 1. Resolve multi-source observation conflicts
        clean_obs = self.conflict_resolver.resolve_conflicts(new_observations)

        # 2. Clone parent states
        updated_states: Dict[str, MolecularState] = {
            k: MolecularState(**v.to_dict()) for k, v in parent_version.states.items()
        }

        # 3. Assimilate
        for obs in clean_obs:
            if obs.entity_id not in updated_states:
                updated_states[obs.entity_id] = MolecularState(
                    entity_id=obs.entity_id,
                    gene_expression=obs.value if obs.measurement_type == "gene_expression" else None,
                    protein_abundance=obs.value if obs.measurement_type == "protein_abundance" else None,
                    cell_condition=obs.condition or parent_version.context.condition
                )
            else:
                st = updated_states[obs.entity_id]
                m_type = obs.measurement_type
                if m_type in ["gene_expression", "protein_abundance", "protein_activity"]:
                    self.assimilator.assimilate_kalman(
                        prior_state=st,
                        measurement_value=obs.value or 0.0,
                        measurement_variance=(obs.uncertainty or 0.15) ** 2,
                        feature=m_type
                    )

        # 4. Generate new version tag and ID
        v_idx = len(twin.versions) + 1
        tag = new_version_tag or f"v1.{v_idx - 1}"
        child_version_id = f"VER-{twin.twin_id}-{tag}"

        child_version = TwinVersion(
            version_id=child_version_id,
            version_tag=tag,
            twin_id=twin.twin_id,
            parent_version_id=parent_version.version_id,
            context=parent_version.context,
            initialization_mode=parent_version.initialization_mode,
            layers=list(parent_version.layers),
            snapshot=parent_version.snapshot,
            states=updated_states,
            temporal_series=list(parent_version.temporal_series),
            created_at=datetime.utcnow().isoformat()
        )
        child_version.compute_hash()

        # Update twin
        twin.versions[child_version_id] = child_version
        twin.active_version_id = child_version_id
        twin.updated_at = datetime.utcnow().isoformat()

        logger.info(f"Updated twin {twin.twin_id} to child version {child_version_id} ({tag})")
        return child_version
