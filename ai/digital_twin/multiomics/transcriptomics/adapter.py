"""Transcriptomics modality adapter (bulk and single-cell RNA-seq)."""

from __future__ import annotations

import math
from typing import Any, Dict, List
from ai.digital_twin.schema import Modality, MolecularObservation


class TranscriptomicsAdapter:
    """Ingests and standardizes RNA-seq transcript abundance profiles."""

    def process_observations(
        self,
        raw_counts: Dict[str, float],
        sample_id: str,
        organism_id: str = "NCBI:9606",
        tissue_id: str = "liver"
    ) -> List[MolecularObservation]:
        """Normalizes counts to log2(TPM + 1) and yields typed observations."""
        total_counts = sum(raw_counts.values()) or 1.0
        observations: List[MolecularObservation] = []

        for gene, count in raw_counts.items():
            tpm = (count / total_counts) * 1e6
            log2_tpm = round(math.log2(tpm + 1.0), 3)

            obs = MolecularObservation(
                observation_id=f"OBS-TX-{sample_id}-{gene}",
                entity_id=gene,
                modality=Modality.TRANSCRIPTOMICS.value,
                measurement_type="gene_expression",
                value=log2_tpm,
                unit="log2(TPM + 1)",
                organism_id=organism_id,
                tissue_id=tissue_id,
                cell_type_id="hepatocyte",
                sample_id=sample_id,
                condition="observed",
                timepoint=0.0,
                assay="RNA-seq",
                source_dataset="GEO:GSE_TRANSCRIPTOME",
                normalization_method="log2_tpm_tmm",
                uncertainty=0.05,
                provenance_id=f"PRV-{sample_id}"
            )
            observations.append(obs)

        return observations
