"""
PROTEA Phase 10: Compensatory Detector
Detects feedback loops, relief of negative feedback, and secondary bypass signaling.
"""

from __future__ import annotations
from typing import Dict, List, Any


COMPENSATORY_NETWORKS: Dict[str, List[Dict[str, Any]]] = {
    "BRAF": [
        {
            "mechanism": "CRAF Heterodimerization Bypass",
            "trigger": "BRAF Monomer Inhibition (Vemurafenib / Dabrafenib)",
            "description": "Loss of ERK-mediated feedback inhibition on RTKs promotes RAS-GTP loading, inducing CRAF-BRAF dimerization and 'paradoxical activation'.",
            "alternative_targets": ["MAP2K1", "MAP2K2", "EGFR"],
            "recommended_strategy": "Combined BRAF inhibitor + MEK inhibitor (e.g. Dabrafenib + Trametinib)."
        },
        {
            "mechanism": "Receptor Tyrosine Kinase (EGFR/MET) Upregulation",
            "trigger": "Downstream ERK pathway suppression in colorectal cancer",
            "description": "Rapid loss of negative feedback relief triggers rapid EGFR phosphorylation, sustaining parallel survival signaling.",
            "alternative_targets": ["EGFR", "PIK3CA"],
            "recommended_strategy": "Triple combination: BRAF inhibitor + EGFR monoclonal antibody (Cetuximab) + MEK inhibitor."
        }
    ],
    "EGFR": [
        {
            "mechanism": "Secondary Gatekeeper Mutation (T790M / C797S)",
            "trigger": "1st/2nd generation TKI selective pressure",
            "description": "Steric hindrance prevents 1st gen TKI binding while preserving ATP affinity; C797S blocks covalent bond formation of 3rd gen TKIs.",
            "alternative_targets": ["MET", "ERBB2", "ERBB3"],
            "recommended_strategy": "Switch to 3rd generation TKI (Osimertinib) or 4th generation allosteric EGFR inhibitors."
        },
        {
            "mechanism": "MET Gene Amplification Bypass",
            "trigger": "Chronic EGFR kinase inhibition",
            "description": "MET receptor amplification independently activates ERBB3-mediated PI3K/AKT cascade bypassing EGFR block.",
            "alternative_targets": ["MET"],
            "recommended_strategy": "Co-administration of MET inhibitor (Capmatinib / Tepotinib) with EGFR inhibitor."
        }
    ],
    "KRAS": [
        {
            "mechanism": "Feedback RTK Rebound Activation",
            "trigger": "Direct KRAS G12C inhibition (Sotorasib / Adagrasib)",
            "description": "Suppression of KRAS triggers upstream RTK (EGFR, HER2, FGFR) activation which drives wildtype RAS nucleotide exchange.",
            "alternative_targets": ["SOS1", "SHP2 (PTPN11)", "EGFR"],
            "recommended_strategy": "Combine KRAS G12C inhibitor with SHP2 inhibitor (TNO155) or anti-EGFR antibody."
        }
    ]
}


class CompensatoryBypassDetector:
    """Detects alternative resistance pathways and compensatory signaling circuits."""

    @classmethod
    def detect_bypass_mechanisms(cls, gene_symbol: str) -> List[Dict[str, Any]]:
        """Identifies known bypass and compensatory feedback relief mechanisms."""
        gene = gene_symbol.upper()
        return COMPENSATORY_NETWORKS.get(gene, [
            {
                "mechanism": "Generic Signaling Rewiring",
                "trigger": "Targeted inhibition",
                "description": "Cellular adaptation through parallel kinase cascades or epigenetic rewiring.",
                "alternative_targets": ["PIK3CA", "MAP2K1"],
                "recommended_strategy": "Combination therapy targeting downstream or orthogonal survival pathways."
            }
        ])
