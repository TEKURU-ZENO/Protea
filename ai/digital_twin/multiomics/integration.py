"""Multi-Omics Harmonization and Cross-Modal Integration."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional
from ai.digital_twin.schema import Modality, MolecularObservation, MolecularState, StateStatus

logger = logging.getLogger(__name__)


class MultiOmicsIntegrator:
    """Harmonizes multiple molecular data modalities into unified, multi-attribute MolecularState vectors."""

    def __init__(self) -> None:
        pass

    def integrate_observations(
        self,
        base_states: Dict[str, MolecularState],
        observations: List[MolecularObservation]
    ) -> Dict[str, MolecularState]:
        """Overlays and reconciles multi-omics empirical measurements onto the twin's existing states."""
        updated = {k: MolecularState(**v.to_dict()) for k, v in base_states.items()}

        for obs in observations:
            entity = obs.entity_id
            if entity not in updated:
                updated[entity] = MolecularState(
                    entity_id=entity,
                    status=StateStatus.OBSERVED.value,
                    cell_condition=obs.condition or "observed",
                    confidence=1.0 - (obs.uncertainty or 0.05)
                )

            st = updated[entity]
            st.status = StateStatus.OBSERVED.value

            # Route by modality and measurement type
            if obs.modality == Modality.TRANSCRIPTOMICS.value or obs.measurement_type == "gene_expression":
                st.gene_expression = obs.value
            elif obs.modality == Modality.PROTEOMICS.value or obs.measurement_type == "protein_abundance":
                st.protein_abundance = obs.value
            elif obs.modality == Modality.PHOSPHOPROTEOMICS.value or obs.measurement_type == "phosphorylation":
                st.phosphorylation = obs.value
                # Phosphorylation can inform active protein state
                if obs.value is not None and st.protein_activity is None:
                    st.protein_activity = round((obs.value - 0.5) * 2.0, 2)
            elif obs.measurement_type == "protein_activity":
                st.protein_activity = obs.value

            # Adjust confidence based on uncertainty
            if obs.uncertainty:
                st.confidence = min(st.confidence, 1.0 - obs.uncertainty)

        logger.info(f"Integrated {len(observations)} multi-omics observations across {len(updated)} entities.")
        return updated

    def compute_cross_modal_concordance(
        self,
        states: Dict[str, MolecularState]
    ) -> Dict[str, float]:
        """Calculates concordance between mRNA expression and protein abundance where both are measured."""
        paired_diffs: List[float] = []
        for s in states.values():
            if s.gene_expression is not None and s.protein_abundance is not None:
                diff = abs(s.gene_expression - s.protein_abundance)
                paired_diffs.append(diff)

        if not paired_diffs:
            return {"concordance_score": 1.0, "paired_count": 0}

        mean_diff = sum(paired_diffs) / len(paired_diffs)
        # Score normalized: low difference means high concordance
        concordance = round(max(0.0, 1.0 - (mean_diff / 5.0)), 3)
        return {
            "concordance_score": concordance,
            "mean_absolute_difference": round(mean_diff, 3),
            "paired_count": len(paired_diffs)
        }
