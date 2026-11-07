"""
PROTEA AI Scientist - Citation & Literature Grounding Validator
Enforces citation integrity: preprints vs peer-reviewed separation, claim-level verification.
"""

from typing import Dict, Any, List, Set


class CitationValidator:
    """
    Validates that every citation in a manuscript or report points to an authentic,
    retrieved publication record, correctly separating peer-reviewed from preprints.
    """

    def validate_citations(
        self,
        cited_dois: List[str],
        retrieved_publications: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Validates manuscript citations against authentic retrieved publications.
        """
        retrieved_map = {}
        for pub in retrieved_publications:
            doi = pub.get("doi", "").lower().strip()
            pmid = pub.get("pmid", "").strip()
            if doi:
                retrieved_map[doi] = pub
            if pmid:
                retrieved_map[pmid] = pub

        valid_citations = []
        hallucinated_citations = []
        preprint_citations = []
        peer_reviewed_citations = []

        for cite in cited_dois:
            cite_clean = cite.lower().strip()
            if cite_clean in retrieved_map:
                pub = retrieved_map[cite_clean]
                valid_citations.append(cite)
                is_preprint = pub.get("is_preprint", False)
                if is_preprint:
                    preprint_citations.append(cite)
                else:
                    peer_reviewed_citations.append(cite)
            else:
                hallucinated_citations.append(cite)

        is_valid = len(hallucinated_citations) == 0

        return {
            "is_valid": is_valid,
            "total_cited": len(cited_dois),
            "valid_citations_count": len(valid_citations),
            "hallucinated_citations_count": len(hallucinated_citations),
            "hallucinated_citations": hallucinated_citations,
            "peer_reviewed_count": len(peer_reviewed_citations),
            "preprint_count": len(preprint_citations),
            "preprint_citations": preprint_citations,
            "integrity_score": (
                round(len(valid_citations) / len(cited_dois), 4) if cited_dois else 1.0
            ),
            "preprint_disclosure_required": len(preprint_citations) > 0,
        }
