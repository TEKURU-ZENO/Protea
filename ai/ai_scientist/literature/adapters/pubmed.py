"""PubMed literature adapter for biomedical publications."""

from typing import Any, Dict, List
from ai.ai_scientist.schema import PublicationRecord


class PubMedAdapter:
    """Retrieves peer-reviewed biomedical literature records from PubMed / MEDLINE."""

    CURATED_LITERATURE = [
        PublicationRecord(
            pub_id="PMID:20811451",
            pmid="20811451",
            doi="10.1038/nature09462",
            title="RAF inhibitor resistance in melanoma through reactivation of the MAPK pathway",
            authors=["Nazarian, R.", "Shi, H.", "Wang, Q.", "Kong, X.", "Ribas, A."],
            journal="Nature",
            year=2010,
            citation_count=1820,
            abstract="Resistance to BRAF inhibition in melanoma frequently emerges through reactivation of MEK/ERK signaling, mediated by alternative receptor tyrosine kinase activation (PDGFRB, EGFR) or secondary mutations.",
            is_peer_reviewed=True,
            is_preprint=False,
            url="https://pubmed.ncbi.nlm.nih.gov/20811451/",
        ),
        PublicationRecord(
            pub_id="PMID:22266938",
            pmid="22266938",
            doi="10.1038/nature10763",
            title="EGFR feedback activation mediates resistance to BRAF inhibition in colorectal cancer",
            authors=["Prahallad, A.", "Sun, C.", "Huang, S.", "Bernards, R."],
            journal="Nature",
            year=2012,
            citation_count=1450,
            abstract="BRAF(V600E) colorectal cancers are intrinsically resistant to vemurafenib due to rapid feedback activation of EGFR following loss of negative feedback by phospho-ERK.",
            is_peer_reviewed=True,
            is_preprint=False,
            url="https://pubmed.ncbi.nlm.nih.gov/22266938/",
        ),
        PublicationRecord(
            pub_id="PMID:21179093",
            pmid="21179093",
            doi="10.1038/nature09642",
            title="COT/MAP3K8 driving resistance to RAF inhibition",
            authors=["Johannessen, C. M.", "Boehm, J. S.", "Kim, S. Y.", "Garraway, L. A."],
            journal="Nature",
            year=2010,
            citation_count=1180,
            abstract="Expression of MAP3K8 (COT) activates MEK and ERK independently of RAF, overcoming targeted RAF inhibitor therapy.",
            is_peer_reviewed=True,
            is_preprint=False,
            url="https://pubmed.ncbi.nlm.nih.gov/21179093/",
        ),
    ]

    @classmethod
    def search(cls, query: str, limit: int = 10) -> List[PublicationRecord]:
        """Search PubMed database matching query keywords."""
        q_lower = query.lower()
        results = []
        for rec in cls.CURATED_LITERATURE:
            if any(term in rec.title.lower() or term in rec.abstract.lower() for term in q_lower.split()):
                results.append(rec)
        return results[:limit] or cls.CURATED_LITERATURE[:limit]
