"""Phosphoproteomics modality adapter (phosphosite occupancy and kinase activity)."""

from __future__ import annotations

from typing import Any, Dict, List
from ai.digital_twin.schema import Modality, MolecularObservation


class PhosphoproteomicsAdapter:
    """Ingests site-level phosphorylation stoichiometries and kinase targets."""

    def process_observations(
        self,
        phospho_sites: Dict[str, float],
        sample_id: str,
        organism_id: str = "NCBI:9606",
        tissue_id: str = "liver"
    ) -> List[MolecularObservation]:
        """Maps phosphorylation stoichiometries [0.0 - 1.0] to protein targets."""
        observations: List[MolecularObservation] = []

        for site_key, ratio in phospho_sites.items():
            protein = site_key.split("_")[0] if "_" in site_key else site_key

            obs = MolecularObservation(
                observation_id=f"OBS-PH-{sample_id}-{site_key}",
                entity_id=protein,
                modality=Modality.PHOSPHOPROTEOMICS.value,
                measurement_type="phosphorylation",
                value=round(min(1.0, max(0.0, ratio)), 3),
                unit="stoichiometry [0.0, 1.0]",
                organism_id=organism_id,
                tissue_id=tissue_id,
                cell_type_id="hepatocyte",
                sample_id=sample_id,
                condition="observed",
                timepoint=0.0,
                assay="Phosphopeptide LC-MS/MS",
                source_dataset="CPTAC:PHOSPHO",
                normalization_method="site_stoichiometry",
                uncertainty=0.10,
                provenance_id=f"PRV-{sample_id}"
            )
            observations.append(obs)

        return observations
