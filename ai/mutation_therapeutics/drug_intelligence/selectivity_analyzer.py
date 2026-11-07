"""
PROTEA Phase 10: Target Selectivity & Off-Target Analyzer
Profiles small molecule selectivity across kinase panels and flags off-target liabilities.
"""

from __future__ import annotations
from typing import Dict, List, Any

# Off-target kinase panel liabilities
OFF_TARGET_PROFILES: Dict[str, Dict[str, Any]] = {
    "DRUG_VEMURAFENIB": {
        "selectivity_ratio": 15.2,
        "off_target_risks": [
            "Moderate off-target inhibition of ZAK (sterility/cardiotoxicity marker)",
            "Low micromolar activity against CRAF (paradoxical activation risk)"
        ]
    },
    "DRUG_DABRAFENIB": {
        "selectivity_ratio": 22.5,
        "off_target_risks": [
            "Weak inhibition of CDK16 and NEK9"
        ]
    },
    "DRUG_TRAMETINIB": {
        "selectivity_ratio": 85.0,
        "off_target_risks": [
            "Extremely high selectivity for MEK1/2 over non-MEK protein kinases"
        ]
    },
    "DRUG_GEFITINIB": {
        "selectivity_ratio": 8.4,
        "off_target_risks": [
            "Cross-reactivity with ERBB2 and ERBB4",
            "Inhibition of ABCG2 efflux transporter"
        ]
    },
    "DRUG_OSIMERTINIB": {
        "selectivity_ratio": 45.0,
        "off_target_risks": [
            "High selectivity for EGFR T790M/L858R over wild-type EGFR (~10-fold sparing)",
            "Minor covalent labeling of ERBB2"
        ]
    },
    "DRUG_SOTORASIB": {
        "selectivity_ratio": 120.0,
        "off_target_risks": [
            "Selective covalent labeling of Cys12 in mutant KRAS; near zero wildtype kinase off-target hits"
        ]
    }
}


class SelectivityAnalyzer:
    """Analyzes selectivity ratios and potential toxic off-target interactions."""

    @classmethod
    def analyze_selectivity(cls, drug_id: str) -> Dict[str, Any]:
        """Returns selectivity ratio and known off-target risks."""
        profile = OFF_TARGET_PROFILES.get(drug_id, {
            "selectivity_ratio": 10.0,
            "off_target_risks": ["Standard kinase panel cross-reactivity"]
        })
        return {
            "drug_id": drug_id,
            "selectivity_ratio": profile["selectivity_ratio"],
            "off_target_risks": profile["off_target_risks"],
            "is_highly_selective": profile["selectivity_ratio"] >= 20.0
        }
