"""Contradiction detector and disagreement preservation engine."""

from typing import Any, Dict, List
from ai.ai_scientist.schema import ScientificClaim, ClaimStatus


class ContradictionResolver:
    """Detects and documents scientific disagreements without forcing artificial consensus."""

    @staticmethod
    def identify_contradictions(claims: List[ScientificClaim]) -> List[Dict[str, Any]]:
        """Identify conflicting claims (e.g. claim A activates vs claim B inhibits)."""
        contradictions = []

        # Example: compare claims with identical subject & object but opposing predicates
        for i in range(len(claims)):
            for j in range(i + 1, len(claims)):
                c1 = claims[i]
                c2 = claims[j]
                if c1.subject == c2.subject and c1.object == c2.object:
                    if ("activat" in c1.predicate and "inhibit" in c2.predicate) or \
                       ("activat" in c2.predicate and "inhibit" in c1.predicate):
                        c1.claim_status = ClaimStatus.UNRESOLVED.value
                        c2.claim_status = ClaimStatus.UNRESOLVED.value
                        contradictions.append({
                            "claim_a_id": c1.claim_id,
                            "claim_b_id": c2.claim_id,
                            "subject": c1.subject,
                            "object": c1.object,
                            "conflict_type": "OPPOSING_REGULATORY_EFFECT",
                            "preservation_policy": "MAINTAIN_UNRESOLVED_DISAGREEMENT",
                            "possible_causes": [
                                "Different cellular / tissue contexts",
                                "Varying inhibitor dosage regimes",
                                "Presence of co-occurring mutations",
                            ],
                        })

        return contradictions

    @classmethod
    def detect_contradictions(cls, claims: List[ScientificClaim]) -> List[Dict[str, Any]]:
        return cls.identify_contradictions(claims)

