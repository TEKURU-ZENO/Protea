"""
PROTEA Phase 10: PPI Interface Disruption Analyzer
Maps mutations onto protein-protein interaction contact interfaces.
"""

from __future__ import annotations
from typing import Dict, List, Any

# Curated PPI interface contact hotspots
PPI_INTERFACE_MAPS: Dict[str, Dict[str, List[int]]] = {
    "BRAF": {
        "MAP2K1": [471, 479, 595, 600, 602],
        "MAP2K2": [471, 479, 595, 600, 602],
        "HRAS": [156, 160, 166, 178],
        "KRAS": [156, 160, 166, 178],
        "YWHAZ": [365, 729],  # 14-3-3 auto-inhibition binding
        "CRAF": [501, 505, 510]  # Dimerization interface
    },
    "EGFR": {
        "GRB2": [1068, 1086, 1173],
        "SHC1": [1148, 1173],
        "STAT3": [705, 858],
        "ERBB2": [250, 265, 700, 715]
    },
    "KRAS": {
        "BRAF": [31, 33, 35, 39],
        "RAF1": [31, 33, 35, 39],
        "PIK3CA": [38, 40, 42],
        "RALGDS": [32, 34, 38],
        "NF1": [12, 13, 61]  # GAP catalytic cleft interaction
    },
    "TP53": {
        "MDM2": [19, 23, 26],
        "MDM4": [19, 23, 26],
        "TP53BP1": [178, 181, 248],
        "EP300": [370, 372, 378]
    }
}


class PPIInterfaceDisruptionAnalyzer:
    """Detects whether a residue change directly disrupts specific protein partners' binding interfaces."""

    @classmethod
    def check_partner_interfaces(cls, gene_symbol: str, position: int) -> Dict[str, Any]:
        """Identifies which interaction partners have interfaces overlapping the mutated position."""
        gene = gene_symbol.upper()
        partner_interfaces = PPI_INTERFACE_MAPS.get(gene, {})

        disrupted_partners: List[str] = []
        intact_partners: List[str] = []

        for partner, contact_residues in partner_interfaces.items():
            # If position is directly in interface or +/- 2 residues
            if any(abs(position - cr) <= 2 for cr in contact_residues):
                disrupted_partners.append(partner)
            else:
                intact_partners.append(partner)

        return {
            "gene": gene,
            "mutated_position": position,
            "disrupted_partners": disrupted_partners,
            "intact_partners": intact_partners,
            "interface_disrupted": len(disrupted_partners) > 0
        }
