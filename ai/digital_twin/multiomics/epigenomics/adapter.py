"""Epigenomics modality adapter (ATAC-seq chromatin accessibility)."""

from __future__ import annotations

from typing import Any, Dict, List
from ai.digital_twin.schema import Modality, MolecularObservation


class EpigenomicsAdapter:
    """Ingests promoter chromatin accessibility and epigenetic states."""

    def process_observations(
        self,
        promoter_peaks: Dict[str, float],
        sample_id: str,
        organism_id: str = "NCBI:9606",
        tissue_id: str = "liver"
    ) -> List[MolecularObservation]:
        observations: List[MolecularObservation] = []

        for gene, peak_score in promoter_peaks.items():
            obs = MolecularObservation(
                observation_id=f"OBS-EP-{sample_id}-{gene}",
                entity_id=gene,
                modality=Modality.EPIGENOMICS.value,
                measurement_type="chromatin_accessibility",
                value=round(peak_score, 3),
                unit="RPKM peak signal",
                organism_id=organism_id,
                tissue_id=tissue_id,
                cell_type_id="hepatocyte",
                sample_id=sample_id,
                condition="observed",
                timepoint=0.0,
                assay="ATAC-seq",
                source_dataset="ENCODE:ATAC",
                normalization_method="quantile_normalized",
                uncertainty=0.12,
                provenance_id=f"PRV-{sample_id}"
            )
            observations.append(obs)

        return observations
