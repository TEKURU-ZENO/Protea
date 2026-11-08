"""
PROTEA Phase 11: Modality Ingestion Adapters
Ingestion framework for heterogeneous multi-omics data preserving modality semantics, scale, and missingness.
"""

from __future__ import annotations
import uuid
from typing import Dict, List, Any, Optional
from ai.moeie.schema import OmicsDataset, BiologicalSample, OmicsModality, OmicsMeasurement


class ModalityIngestionAdapters:
    """Modality-specific data ingestors that preserve measurement semantics."""

    @classmethod
    def ingest_transcriptomics(
        cls,
        dataset_name: str,
        expression_matrix: Dict[str, Dict[str, float]],  # sample_id -> {gene_symbol: count}
        metadata: Optional[Dict[str, Any]] = None,
        organism_id: int = 9606
    ) -> Dict[str, Any]:
        """Ingests bulk or pseudobulk RNA-seq count data."""
        dataset_id = f"ds_rna_{uuid.uuid4().hex[:8]}"
        sample_ids = list(expression_matrix.keys())
        features = set()
        measurements: List[OmicsMeasurement] = []

        for sid, genes in expression_matrix.items():
            for gene, count in genes.items():
                features.add(gene)
                measurements.append(
                    OmicsMeasurement(
                        measurement_id=f"m_{uuid.uuid4().hex[:6]}",
                        sample_id=sid,
                        feature_id=gene,
                        modality=OmicsModality.TRANSCRIPTOMICS,
                        raw_value=float(count),
                        normalized_value=float(count),  # Preprocessing handles normalization
                        unit="raw_read_counts",
                        is_missing=False
                    )
                )

        dataset = OmicsDataset(
            dataset_id=dataset_id,
            name=dataset_name,
            modality=OmicsModality.TRANSCRIPTOMICS,
            source=metadata.get("source", "GEO") if metadata else "GEO",
            organism_taxonomy_id=organism_id,
            n_samples=len(sample_ids),
            n_features=len(features),
            metadata=metadata or {}
        )

        return {
            "dataset": dataset,
            "sample_ids": sample_ids,
            "features_count": len(features),
            "measurements_count": len(measurements),
            "measurements": measurements
        }

    @classmethod
    def ingest_proteomics(
        cls,
        dataset_name: str,
        intensity_matrix: Dict[str, Dict[str, Optional[float]]],  # sample_id -> {protein_id: intensity}
        metadata: Optional[Dict[str, Any]] = None,
        is_phosphoproteomics: bool = False,
        organism_id: int = 9606
    ) -> Dict[str, Any]:
        """Ingests MS-based proteomics or phosphoproteomics with explicit missing value preservation."""
        modality = OmicsModality.PHOSPHOPROTEOMICS if is_phosphoproteomics else OmicsModality.PROTEOMICS
        dataset_id = f"ds_prot_{uuid.uuid4().hex[:8]}"
        sample_ids = list(intensity_matrix.keys())
        features = set()
        measurements: List[OmicsMeasurement] = []

        for sid, proteins in intensity_matrix.items():
            for prot, intensity in proteins.items():
                features.add(prot)
                is_missing = intensity is None
                raw_val = 0.0 if is_missing else float(intensity)
                measurements.append(
                    OmicsMeasurement(
                        measurement_id=f"m_{uuid.uuid4().hex[:6]}",
                        sample_id=sid,
                        feature_id=prot,
                        modality=modality,
                        raw_value=raw_val,
                        normalized_value=raw_val,
                        unit="ms_intensity_log2",
                        is_missing=is_missing,
                        quality_flag="MISSING_VALUE" if is_missing else "PASS"
                    )
                )

        dataset = OmicsDataset(
            dataset_id=dataset_id,
            name=dataset_name,
            modality=modality,
            source=metadata.get("source", "CPTAC") if metadata else "CPTAC",
            organism_taxonomy_id=organism_id,
            n_samples=len(sample_ids),
            n_features=len(features),
            metadata=metadata or {}
        )

        return {
            "dataset": dataset,
            "sample_ids": sample_ids,
            "features_count": len(features),
            "measurements_count": len(measurements),
            "measurements": measurements
        }

    @classmethod
    def ingest_single_cell(
        cls,
        dataset_name: str,
        n_cells: int,
        n_genes: int,
        cell_types: List[str],
        metadata: Optional[Dict[str, Any]] = None,
        organism_id: int = 9606
    ) -> Dict[str, Any]:
        """Ingests single-cell metadata and cell population summary."""
        dataset_id = f"ds_sc_{uuid.uuid4().hex[:8]}"
        dataset = OmicsDataset(
            dataset_id=dataset_id,
            name=dataset_name,
            modality=OmicsModality.SINGLE_CELL,
            source=metadata.get("source", "CELLxGENE") if metadata else "CELLxGENE",
            organism_taxonomy_id=organism_id,
            n_samples=n_cells,
            n_features=n_genes,
            metadata={**(metadata or {}), "cell_types": cell_types}
        )
        return {
            "dataset": dataset,
            "n_cells": n_cells,
            "n_genes": n_genes,
            "cell_types": cell_types
        }

    @classmethod
    def ingest_spatial(
        cls,
        dataset_name: str,
        n_spots: int,
        n_genes: int,
        tissue_section: str,
        metadata: Optional[Dict[str, Any]] = None,
        organism_id: int = 9606
    ) -> Dict[str, Any]:
        """Ingests spatial transcriptomics / proteomics slice metadata."""
        dataset_id = f"ds_spat_{uuid.uuid4().hex[:8]}"
        dataset = OmicsDataset(
            dataset_id=dataset_id,
            name=dataset_name,
            modality=OmicsModality.SPATIAL,
            source=metadata.get("source", "10x_Visium") if metadata else "10x_Visium",
            organism_taxonomy_id=organism_id,
            n_samples=n_spots,
            n_features=n_genes,
            metadata={**(metadata or {}), "tissue_section": tissue_section}
        )
        return {
            "dataset": dataset,
            "n_spots": n_spots,
            "n_genes": n_genes,
            "tissue_section": tissue_section
        }
