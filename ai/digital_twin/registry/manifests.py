"""Reproducible Twin Manifest generator and exporter."""

from __future__ import annotations

import json
from typing import Any, Dict
from ai.digital_twin.schema import DigitalTwin, TwinVersion


class TwinManifestGenerator:
    """Produces structured, reproducible manifests describing twin configurations and lineages."""

    def generate_manifest(self, twin: DigitalTwin, version_id: str) -> Dict[str, Any]:
        """Generates an exportable, self-contained provenance manifest for a twin version."""
        version = twin.versions.get(version_id)
        if not version:
            raise ValueError(f"Version {version_id} not found in twin {twin.twin_id}.")

        return {
            "manifest_version": "1.0.0",
            "twin": {
                "id": twin.twin_id,
                "name": twin.name,
                "organism": twin.organism,
                "primary_tissue": twin.primary_tissue,
                "primary_cell_type": twin.primary_cell_type
            },
            "version": {
                "id": version.version_id,
                "tag": version.version_tag,
                "parent_version": version.parent_version_id,
                "content_hash": version.content_hash,
                "initialization_mode": version.initialization_mode,
                "created_at": version.created_at
            },
            "context": version.context.to_dict(),
            "layers": version.layers,
            "topology_summary": {
                "nodes_count": len(version.snapshot.nodes) if version.snapshot else 0,
                "edges_count": len(version.snapshot.edges) if version.snapshot else 0
            },
            "states_summary": {
                "entity_count": len(version.states),
                "observed_count": sum(1 for s in version.states.values() if s.status == "OBSERVED"),
                "estimated_count": sum(1 for s in version.states.values() if s.status == "ESTIMATED")
            },
            "validation_status": version.validation_report.is_valid if version.validation_report else None
        }
