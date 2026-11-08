"""
PROTEA Phase 11: Provenance & Evidence Stratification Tracker
Classifies evidence into Observed, Curated, Inferred, Predicted, or Simulated tiers.
"""

from __future__ import annotations
import datetime
from typing import Dict, List, Any
from ai.moeie.schema import EvidenceProvenance


class ProvenanceTracker:
    """Attaches formal epistemological provenance and calibration metadata to scientific outputs."""

    @classmethod
    def create_provenance_envelope(
        cls,
        analysis_type: str,
        result_payload: Dict[str, Any],
        provenance_tier: EvidenceProvenance,
        dataset_versions: List[str],
        organism_taxonomy_id: int = 9606,
        model_version: str = "moeie_v1.0"
    ) -> Dict[str, Any]:
        """Wraps any MOEIE output in a versioned, verifiable provenance envelope."""
        return {
            "analysis_type": analysis_type,
            "provenance_tier": provenance_tier.value if hasattr(provenance_tier, "value") else str(provenance_tier),
            "organism_taxonomy_id": organism_taxonomy_id,
            "dataset_versions": dataset_versions,
            "model_version": model_version,
            "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "is_experimental_observation": provenance_tier == EvidenceProvenance.OBSERVED,
            "is_computational_hypothesis": provenance_tier in [EvidenceProvenance.INFERRED, EvidenceProvenance.PREDICTED, EvidenceProvenance.SIMULATED],
            "result": result_payload
        }
