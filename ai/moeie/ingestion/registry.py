"""
PROTEA Phase 11: Dataset Registry & Metadata Manager
Tracks dataset versions, quality-control status, provenance, and experimental metadata.
"""

from __future__ import annotations
import uuid
import datetime
from typing import Dict, List, Any, Optional
from ai.moeie.schema import OmicsDataset, OmicsModality


class DatasetRegistry:
    """In-memory and persistent registry for multi-omics datasets."""

    def __init__(self):
        self._datasets: Dict[str, OmicsDataset] = {}
        self._provenance_logs: Dict[str, List[Dict[str, Any]]] = {}

    def register_dataset(self, dataset: OmicsDataset, user_metadata: Optional[Dict[str, Any]] = None) -> OmicsDataset:
        """Registers a new dataset with versioning and provenance tracking."""
        if user_metadata:
            dataset.metadata.update(user_metadata)

        self._datasets[dataset.dataset_id] = dataset
        self._provenance_logs[dataset.dataset_id] = [
            {
                "event": "dataset_registered",
                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "dataset_id": dataset.dataset_id,
                "modality": dataset.modality.value if hasattr(dataset.modality, "value") else str(dataset.modality),
                "source": dataset.source
            }
        ]
        return dataset

    def get_dataset(self, dataset_id: str) -> Optional[OmicsDataset]:
        return self._datasets.get(dataset_id)

    def list_datasets(self, modality: Optional[OmicsModality] = None) -> List[OmicsDataset]:
        if not modality:
            return list(self._datasets.values())
        return [d for d in self._datasets.values() if d.modality == modality]

    def log_transformation(self, dataset_id: str, action: str, details: Dict[str, Any]) -> None:
        if dataset_id not in self._provenance_logs:
            self._provenance_logs[dataset_id] = []
        self._provenance_logs[dataset_id].append({
            "event": action,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "details": details
        })

    def get_provenance(self, dataset_id: str) -> List[Dict[str, Any]]:
        return self._provenance_logs.get(dataset_id, [])
