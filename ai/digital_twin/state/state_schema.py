"""Biological State Schema defining multidimensional molecular state spaces."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from ai.digital_twin.schema import StateStatus


@dataclass
class StateDimensionMetadata:
    """Metadata describing a specific biological state dimension."""
    dimension_name: str
    unit: str
    assay_type: str
    normalization: str
    typical_range: tuple[float, float]
    description: str


# Canonical definitions establishing scientific boundaries between dimensions
STATE_DIMENSIONS: Dict[str, StateDimensionMetadata] = {
    "gene_expression": StateDimensionMetadata(
        dimension_name="gene_expression",
        unit="log2(TPM + 1)",
        assay_type="RNA-seq",
        normalization="log2_tpm",
        typical_range=(0.0, 16.0),
        description="Steady-state transcript abundance (mRNA level). Does NOT equate to protein concentration."
    ),
    "protein_abundance": StateDimensionMetadata(
        dimension_name="protein_abundance",
        unit="log2(LFQ intensity)",
        assay_type="LC-MS/MS",
        normalization="median_polish",
        typical_range=(0.0, 18.0),
        description="Physical translated protein copy number. Does NOT equate to active enzymatic state."
    ),
    "protein_activity": StateDimensionMetadata(
        dimension_name="protein_activity",
        unit="inferred_score [-1.0, 1.0]",
        assay_type="Activity-based probe / Kinase substrate enrichment",
        normalization="zscore",
        typical_range=(-1.0, 1.0),
        description="Active biochemical / signaling capacity (e.g. phosphorylation state, ligand binding)."
    ),
    "phosphorylation": StateDimensionMetadata(
        dimension_name="phosphorylation",
        unit="occupancy_fraction [0.0, 1.0]",
        assay_type="Phosphoproteomics",
        normalization="site_stoichiometry",
        typical_range=(0.0, 1.0),
        description="Post-translational phosphorylation site occupancy."
    ),
    "pathway_activity": StateDimensionMetadata(
        dimension_name="pathway_activity",
        unit="ssGSEA / AUCell score",
        assay_type="Pathway signature aggregation",
        normalization="rank_normalized",
        typical_range=(-2.0, 2.0),
        description="Integrated functional module throughput. Does NOT equate to simple ORA enrichment."
    )
}
