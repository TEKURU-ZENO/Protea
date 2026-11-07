"""Metabolomics modality adapter (metabolite abundances)."""

from __future__ import annotations

from typing import Any, Dict, List
from ai.digital_twin.schema import Modality, MolecularObservation


class MetabolomicsAdapter:
    """Ingests targeted and untargeted metabolite concentrations."""

    def process_observations(
        self,
        metabolites: Dict[str, float],
        sample_id: str,
        organism_id: str = "NCBI:9606",
        tissue_id: str = "liver"
    ) -> List[MolecularObservation]:
        observations: List[MolecularObservation] = []

        for met_id, conc in metabolites.items():
            obs = MolecularObservation(
                observation_id=f"OBS-MB-{sample_id}-{met_id}",
                entity_id=met_id,
                modality=Modality.METABOLOMICS.value,
                measurement_type="metabolite_concentration",
                value=round(conc, 3),
                unit="uM concentration",
                organism_id=organism_id,
                tissue_id=tissue_id,
                cell_type_id="hepatocyte",
                sample_id=sample_id,
                condition="observed",
                timepoint=0.0,
                assay="LC-MS Metabolomics",
                source_dataset="HMDB:METABO",
                normalization_method="median_normalized",
                uncertainty=0.15,
                provenance_id=f"PRV-{sample_id}"
            )
            observations.append(obs)

        return observations
