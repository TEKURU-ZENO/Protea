"""Context Builder resolving taxonomy, tissue, cell type, and experimental conditions."""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional
from ai.digital_twin.schema import BiologicalContext

logger = logging.getLogger(__name__)

ORGANISM_MAP = {
    "human": "NCBI:9606",
    "homo sapiens": "NCBI:9606",
    "9606": "NCBI:9606",
    "mouse": "NCBI:10090",
    "mus musculus": "NCBI:10090",
    "10090": "NCBI:10090"
}

TISSUE_MAP = {
    "liver": {"id": "UBERON:0002107", "name": "liver", "primary_cells": ["hepatocyte", "kupffer_cell"]},
    "brain": {"id": "UBERON:0000955", "name": "brain", "primary_cells": ["neuron", "astrocyte", "microglia"]},
    "lung": {"id": "UBERON:0002048", "name": "lung", "primary_cells": ["pneumocyte", "alveolar_macrophage"]},
    "kidney": {"id": "UBERON:0002113", "name": "kidney", "primary_cells": ["podocyte", "tubule_cell"]},
    "heart": {"id": "UBERON:0000948", "name": "heart", "primary_cells": ["cardiomyocyte", "cardiac_fibroblast"]}
}

CELL_TYPE_MAP = {
    "hepatocyte": "CL:0000182",
    "kupffer_cell": "CL:0000091",
    "neuron": "CL:0000540",
    "astrocyte": "CL:0000127",
    "cardiomyocyte": "CL:0000746"
}


class ContextBuilder:
    """Standardizes and enriches contextual descriptors for digital twin initialization."""

    def build_context(
        self,
        organism: str = "NCBI:9606",
        tissue: str = "liver",
        cell_type: str = "hepatocyte",
        condition: str = "healthy",
        treatment: Optional[str] = None,
        timepoint: Optional[float] = None,
        extra_metadata: Optional[Dict[str, Any]] = None
    ) -> BiologicalContext:
        org_id = ORGANISM_MAP.get(organism.lower().strip(), organism)
        tissue_clean = tissue.lower().strip()
        cell_clean = cell_type.lower().strip()

        tissue_meta = TISSUE_MAP.get(tissue_clean, {"id": f"CUSTOM:{tissue_clean}", "name": tissue_clean})
        cell_meta_id = CELL_TYPE_MAP.get(cell_clean, f"CUSTOM:{cell_clean}")

        meta = extra_metadata or {}
        meta["tissue_ontology_id"] = tissue_meta.get("id")
        meta["cell_ontology_id"] = cell_meta_id

        return BiologicalContext(
            organism_id=org_id,
            tissue_id=tissue_clean,
            cell_type_id=cell_clean,
            condition=condition.lower().strip(),
            treatment=treatment,
            timepoint=timepoint,
            metadata=meta
        )
