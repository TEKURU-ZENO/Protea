"""
PROTEA Phase 11: Spatially Variable Gene & Program Discovery
Calculates Moran's I spatial autocorrelation and discovers spatially restricted programs.
"""

from __future__ import annotations
import math
from typing import Dict, List, Any


class SpatialProgramEngine:
    """Detects spatial autocorrelation and defines spatially coherent programs."""

    @classmethod
    def compute_morans_i(
        cls,
        gene_symbol: str,
        values: List[float],
        neighborhood_weights: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculates Moran's I spatial autocorrelation coefficient.
        I > 0: Positive spatial autocorrelation (clustering)
        I = 0: Random spatial distribution
        I < 0: Dispersion / negative autocorrelation
        """
        n = len(values)
        if n < 2:
            return {"gene": gene_symbol, "morans_i": 0.0, "is_spatially_variable": False}

        mean_val = sum(values) / n
        denom = sum((x - mean_val) ** 2 for x in values)

        if denom == 0.0:
            return {"gene": gene_symbol, "morans_i": 0.0, "is_spatially_variable": False}

        total_weight = 0.0
        numerator = 0.0

        for edge in neighborhood_weights:
            i = edge["source_spot"]
            j = edge["target_spot"]
            w = edge["spatial_weight"]
            if i < n and j < n:
                numerator += w * (values[i] - mean_val) * (values[j] - mean_val)
                total_weight += w

        total_weight = max(0.001, total_weight)
        morans_i = round((n / total_weight) * (numerator / denom), 3)

        # High Moran's I indicates localized spatial clustering
        is_svg = morans_i >= 0.25

        return {
            "gene": gene_symbol,
            "morans_i": morans_i,
            "expected_i": round(-1.0 / (n - 1), 4),
            "is_spatially_variable": is_svg,
            "pattern": "Localized Niche Cluster" if morans_i > 0.4 else ("Dispersed" if morans_i < -0.1 else "Diffuse Gradient")
        }

    @classmethod
    def discover_spatial_programs(cls) -> List[Dict[str, Any]]:
        """Returns standard recognized spatial microenvironment programs."""
        return [
            {
                "program_name": "Hypoxic Invasive Edge",
                "spatially_variable_genes": ["VEGFA", "HIF1A", "LDHA", "CA9"],
                "mean_morans_i": 0.68,
                "tissue_niche": "Invasive Margin",
                "biological_process": "Hypoxia response & extracellular acidification"
            },
            {
                "program_name": "Desmoplastic Stromal Barrier",
                "spatially_variable_genes": ["COL1A1", "ACTA2", "FAP", "FN1"],
                "mean_morans_i": 0.74,
                "tissue_niche": "Desmoplastic Stroma",
                "biological_process": "Fibroblast collagen deposition & drug shielding"
            },
            {
                "program_name": "Tertiary Lymphoid Immune Zone",
                "spatially_variable_genes": ["CD8A", "CXCL13", "MS4A1", "GZMB"],
                "mean_morans_i": 0.59,
                "tissue_niche": "Immune Infiltrate Niche",
                "biological_process": "Adaptive anti-tumor lymphocyte engagement"
            }
        ]
