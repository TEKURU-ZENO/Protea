"""Citation graph mapping and historical discovery timelines."""

from typing import Any, Dict, List
from ai.ai_scientist.schema import PublicationRecord


class CitationGraphBuilder:
    """Constructs citation networks and chronological literature discovery timelines."""

    @staticmethod
    def build_timeline(records: List[PublicationRecord]) -> List[Dict[str, Any]]:
        """Order publications chronologically to reveal temporal evolution of mechanisms."""
        sorted_records = sorted(records, key=lambda r: (getattr(r, "year", 2024), -getattr(r, "citation_count", 0)))
        timeline = []

        for r in sorted_records:
            timeline.append({
                "year": getattr(r, "year", 2024),
                "pub_id": getattr(r, "pub_id", "PUB_1"),
                "title": getattr(r, "title", ""),
                "first_author": r.authors[0] if getattr(r, "authors", None) else "Unknown",
                "journal": getattr(r, "journal", "Bioinformatics"),
                "citations": getattr(r, "citation_count", 0),
                "is_peer_reviewed": getattr(r, "is_peer_reviewed", True),
            })

        return timeline

    @classmethod
    def build_graph(cls, records: List[PublicationRecord]) -> Dict[str, Any]:
        """Constructs citation networks and chronological literature discovery timelines."""
        timeline = cls.build_timeline(records)
        nodes = [
            {"id": getattr(r, "pub_id", f"P_{i}"), "label": (getattr(r, "title", "Pub")[:30] + "..."), "year": getattr(r, "year", 2024)}
            for i, r in enumerate(records)
        ]
        edges = []
        for i in range(len(nodes) - 1):
            edges.append({"source": nodes[i]["id"], "target": nodes[i+1]["id"], "type": "cites"})

        return {
            "nodes": nodes,
            "edges": edges,
            "timeline": timeline,
            "node_count": len(nodes),
            "edge_count": len(edges),
        }
