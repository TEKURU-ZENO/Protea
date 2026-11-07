"""Claim-level citation and evidence provenance linker."""

from typing import Dict, List, Any
from ai.ai_scientist.schema import ScientificClaim, PublicationRecord


class EvidenceLinker:
    """Links scientific claims to exact supporting publication records and evidence sentences."""

    @staticmethod
    def link_claims_to_publications(
        claims: List[ScientificClaim],
        publications: List[Any],
    ) -> Dict[str, Dict[str, Any]]:
        """Construct grounded citation map for each claim."""
        pub_map = {}
        for p in publications:
            pid = getattr(p, "pub_id", p.get("pub_id", p.get("doi", "PUB_1")) if isinstance(p, dict) else "PUB_1")
            pub_map[pid] = p

        linked = {}
        for c in claims:
            supporting_pubs = []
            for pid in getattr(c, "publication_ids", []):
                if pid in pub_map:
                    pub_obj = pub_map[pid]
                    if hasattr(pub_obj, "to_dict"):
                        supporting_pubs.append(pub_obj.to_dict())
                    elif isinstance(pub_obj, dict):
                        supporting_pubs.append(pub_obj)
                    else:
                        supporting_pubs.append({"pub_id": pid})

            linked[c.claim_id] = {
                "claim": f"{c.subject} {c.predicate} {c.object}",
                "status": c.claim_status,
                "confidence": c.confidence,
                "evidence_count": len(c.evidence_records),
                "supporting_publications": supporting_pubs,
            }

        return linked

    @classmethod
    def link_evidence(cls, claims, publications):
        return cls.link_claims_to_publications(claims, publications)
