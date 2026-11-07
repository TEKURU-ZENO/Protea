"""Publication deduplication and preprint audit manager."""

from typing import Dict, List, Tuple, Any
from ai.ai_scientist.schema import PublicationRecord


class PublicationDeduplicator:
    """Deduplicates publication records by DOI / PMID and ensures peer-reviewed provenance."""

    @staticmethod
    def deduplicate(records: List[PublicationRecord]) -> List[PublicationRecord]:
        """Deduplicate records by DOI or PMID while preserving citation counts and peer-reviewed status."""
        seen_keys = set()
        unique_records = []

        for r in records:
            # Primary key: DOI if available, else PMID, else pub_id
            doi = getattr(r, "doi", None)
            pmid = getattr(r, "pmid", None)
            pub_id = getattr(r, "pub_id", None)
            key = (doi.lower() if doi else None) or pmid or pub_id or str(r)
            if key not in seen_keys:
                seen_keys.add(key)
                unique_records.append(r)

        return unique_records

    @staticmethod
    def partition_by_review_status(
        records: List[PublicationRecord]
    ) -> Tuple[List[PublicationRecord], List[PublicationRecord]]:
        """Strictly separate peer-reviewed publications from preprints (e.g. bioRxiv)."""
        peer_reviewed = [
            r for r in records
            if getattr(r, "is_peer_reviewed", True) and not getattr(r, "is_preprint", False)
        ]
        preprints = [
            r for r in records
            if getattr(r, "is_preprint", False) or not getattr(r, "is_peer_reviewed", True)
        ]
        return peer_reviewed, preprints


class LiteratureDeduplicator:
    """Coordinator returning structured deduplication metrics."""

    @classmethod
    def deduplicate(cls, records: List[PublicationRecord]) -> Dict[str, Any]:
        unique = PublicationDeduplicator.deduplicate(records)
        peer, pre = PublicationDeduplicator.partition_by_review_status(unique)
        return {
            "unique_records": unique,
            "unique_count": len(unique),
            "peer_reviewed_count": len(peer),
            "preprint_count": len(pre),
            "peer_reviewed": peer,
            "preprints": pre,
        }
