"""Evidence Integrator harmonizing empirical assays, curated knowledge, and predictions."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional
from ai.digital_twin.schema import EdgeStatus, EdgeType, NetworkEdgeEvidence

logger = logging.getLogger(__name__)


class EvidenceIntegrator:
    """Harmonizes and weights multi-source interaction evidence for twin construction."""

    def __init__(self, include_predictions: bool = True, default_threshold: float = 0.50):
        self.include_predictions = include_predictions
        self.default_threshold = default_threshold

    def harmonize_edge(
        self,
        source: str,
        target: str,
        evidence_records: List[Dict[str, Any]],
        context_tissue: Optional[str] = None
    ) -> Optional[NetworkEdgeEvidence]:
        """Synthesizes multiple evidence records for a single candidate edge."""
        if not evidence_records:
            return None

        # Check for direct wet-lab assay
        has_experimental = any(r.get("status") == EdgeStatus.OBSERVED.value or r.get("assay_type") == "EXP" for r in evidence_records)
        has_curated = any(r.get("status") == EdgeStatus.CURATED.value or r.get("source_db") in ["IntAct", "BioGRID", "Reactome"] for r in evidence_records)
        
        # Edge status determination
        if has_experimental:
            edge_status = EdgeStatus.OBSERVED.value
        elif has_curated:
            edge_status = EdgeStatus.CURATED.value
        elif any(r.get("status") == EdgeStatus.INFERRED.value for r in evidence_records):
            edge_status = EdgeStatus.INFERRED.value
        else:
            edge_status = EdgeStatus.PREDICTED.value

        if edge_status == EdgeStatus.PREDICTED.value and not self.include_predictions:
            return None

        # Determine edge type & directionality
        # CRITICAL RULE: Undirected physical PPI must NOT automatically become directed regulation
        directed = False
        edge_type = EdgeType.PHYSICAL_INTERACTION.value
        sign: Optional[int] = None
        mechanisms: List[str] = []

        for rec in evidence_records:
            if rec.get("directed", False) or rec.get("edge_type") in [
                EdgeType.TRANSCRIPTIONAL_REGULATION.value,
                EdgeType.PHOSPHORYLATION.value,
                EdgeType.TRANSLOCATION.value
            ]:
                directed = True
                edge_type = rec.get("edge_type", EdgeType.TRANSCRIPTIONAL_REGULATION.value)
                if rec.get("sign") is not None:
                    sign = rec.get("sign")
            if rec.get("mechanism"):
                mechanisms.append(rec["mechanism"])

        # Aggregate confidence
        confidences = [float(r.get("confidence", 0.5)) for r in evidence_records]
        avg_confidence = sum(confidences) / len(confidences)
        
        # Boost confidence for multi-source validation
        source_dbs = list({r.get("source_db", "PROTEA_UBKG") for r in evidence_records})
        if len(source_dbs) > 1:
            avg_confidence = min(1.0, avg_confidence * 1.15)

        if avg_confidence < self.default_threshold:
            return None

        return NetworkEdgeEvidence(
            source=source,
            target=target,
            edge_type=edge_type,
            directed=directed,
            sign=sign,
            confidence=round(avg_confidence, 4),
            edge_status=edge_status,
            evidence_sources=source_dbs,
            tissue=context_tissue,
            mechanism="; ".join(set(mechanisms)) if mechanisms else None
        )
