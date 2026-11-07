"""Proteomics modality adapter (LC-MS/MS quantitative proteomics)."""

from __future__ import annotations

import math
from typing import Any, Dict, List
from ai.digital_twin.schema import Modality, MolecularObservation


class ProteomicsAdapter:
    """Ingests and standardizes mass-spectrometry label-free / TMT protein abundances."""

    def process_observations(
        self,
        intensities: Dict[str, float],
        sample_id: str,
        organism_id: str = "NCBI:9606",
        tissue_id: str = "liver"
    ) -> List[MolecularObservation]:
        """Normalizes intensities to log2 scale and creates observations."""
        observations: List[MolecularObservation] = []

        for protein, intensity in intensities.items():
            log2_int = round(math.log2(max(1.0, intensity)), 3)

            obs = MolecularObservation(
                observation_id=f"OBS-PR-{sample_id}-{protein}",
                entity_id=protein,
                modality=Modality.PROTEOMICS.value,
                measurement_type="protein_abundance",
                value=log2_int,
                unit="log2(LFQ intensity)",
                organism_id=organism_id,
                tissue_id=tissue_id,
                cell_type_id="hepatocyte",
                sample_id=sample_id,
                condition="observed",
                timepoint=0.0,
                assay="LC-MS/MS",
                source_dataset="PRIDE:PXD001",
                normalization_method="median_polish",
                uncertainty=0.08,
                provenance_id=f"PRV-{sample_id}"
            )
            observations.append(obs)

        return observations
