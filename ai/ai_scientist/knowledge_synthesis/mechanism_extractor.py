"""Biochemical and molecular mechanism extractor."""

from typing import Any, Dict, List
from ai.ai_scientist.schema import ScientificClaim


class MechanismExtractor:
    """Extracts causal biochemical mechanisms and regulatory loops from claims."""

    @staticmethod
    def extract_mechanisms(claims: List[ScientificClaim]) -> List[Dict[str, Any]]:
        """Identify functional mechanistic motifs (cascades, feedback, bypass loops)."""
        mechanisms = []

        # Detect feedback activation
        feedback_claims = [c for c in claims if "feedback" in c.predicate or "feedback" in "".join(c.evidence_records).lower()]
        for c in feedback_claims:
            mechanisms.append({
                "mechanism_type": "NEGATIVE_FEEDBACK_RELIEF",
                "trigger": "Inhibition of downstream kinase (ERK)",
                "mediator": c.subject,
                "consequence": "Compensatory upstream reactivation sustaining pathway flux",
                "confidence": c.confidence,
                "claims": [c.claim_id],
            })

        # Detect independent bypass
        bypass_claims = [c for c in claims if "independently" in c.predicate or "independently" in "".join(c.evidence_records).lower()]
        for c in bypass_claims:
            mechanisms.append({
                "mechanism_type": "PARALLEL_BYPASS_CASCADE",
                "trigger": "Target kinase inhibition",
                "mediator": c.subject,
                "consequence": f"Direct activation of {c.object} circumventing the inhibited node",
                "confidence": c.confidence,
                "claims": [c.claim_id],
            })

        # Default mechanism if none matched
        if not mechanisms:
            mechanisms.append({
                "mechanism_type": "CANONICAL_FORWARD_PROPAGATION",
                "trigger": "Upstream ligand binding",
                "mediator": claims[0].subject if claims else "BRAF",
                "consequence": "Forward cascade phosphorylation and transcriptional survival response",
                "confidence": 0.95,
                "claims": [c.claim_id for c in claims[:2]],
            })

        return mechanisms
