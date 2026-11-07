"""
PROTEA Phase 10: Drug Resistance Predictor
Detects secondary gatekeeper mutations, steric hindrance, and bypass activation driving clinical resistance.
"""

from __future__ import annotations
from typing import Dict, List, Any, Optional
from ai.mutation_therapeutics.schema import ResistanceMechanism

# Established clinical resistance mechanisms
RESISTANCE_DATABASE: Dict[str, Dict[str, Any]] = {
    "EGFR_T790M": {
        "drug_id": "DRUG_GEFITINIB",
        "target_id": "TGT_EGFR",
        "mechanism_type": "gatekeeper_mutation",
        "ic50_fold_change": 63.6,
        "alternative_targets": ["EGFR", "MET", "ERBB2"],
        "recommended_strategy": "Switch to 3rd generation mutant-selective irreversible inhibitor (Osimertinib)."
    },
    "EGFR_C797S": {
        "drug_id": "DRUG_OSIMERTINIB",
        "target_id": "TGT_EGFR",
        "mechanism_type": "covalent_anchoring_disruption",
        "ic50_fold_change": 120.0,
        "alternative_targets": ["MET", "EGFR_ALLOSTERIC"],
        "recommended_strategy": "4th generation allosteric EGFR inhibitor or dual 1st/3rd gen combination if T790M/C797S are in trans."
    },
    "BRAF_V600E_MONOTHERAPY": {
        "drug_id": "DRUG_VEMURAFENIB",
        "target_id": "TGT_BRAF",
        "mechanism_type": "craf_paradoxical_activation_and_bypass",
        "ic50_fold_change": 14.5,
        "alternative_targets": ["MAP2K1", "MAP2K2", "EGFR"],
        "recommended_strategy": "Dual MAPK vertical inhibition with MEK inhibitor (Trametinib) or EGFR antibody (Cetuximab)."
    },
    "KRAS_G12C_SECONDARY": {
        "drug_id": "DRUG_SOTORASIB",
        "target_id": "TGT_KRAS",
        "mechanism_type": "bypass_rtk_reactivation",
        "ic50_fold_change": 8.5,
        "alternative_targets": ["SOS1", "SHP2", "EGFR"],
        "recommended_strategy": "Co-inhibition of upstream nucleotide exchanger SOS1 or SHP2 phosphatase."
    }
}


class ResistancePredictor:
    """Predicts acquired and intrinsic resistance mechanisms for targeted drugs."""

    @classmethod
    def predict_resistance(
        cls,
        mutation_label: str,
        drug_id: str,
        target_id: str
    ) -> ResistanceMechanism:
        """Evaluates whether the mutation or drug pair triggers known resistance phenotypes."""
        # Check direct lookup
        key = mutation_label
        if key not in RESISTANCE_DATABASE:
            for k in RESISTANCE_DATABASE:
                if k in mutation_label or mutation_label in k:
                    key = k
                    break

        record = RESISTANCE_DATABASE.get(key)
        if record:
            return ResistanceMechanism(
                mutation_label=mutation_label,
                drug_id=drug_id,
                target_id=target_id,
                mechanism_type=record["mechanism_type"],
                ic50_fold_change=record["ic50_fold_change"],
                alternative_targets=record["alternative_targets"],
                recommended_strategy=record["recommended_strategy"]
            )

        # Default prediction
        return ResistanceMechanism(
            mutation_label=mutation_label,
            drug_id=drug_id,
            target_id=target_id,
            mechanism_type="unclassified_sensitivity_modulation",
            ic50_fold_change=1.5,
            alternative_targets=[target_id],
            recommended_strategy="Monitor dose-response trajectory and parallel pathway biomarkers."
        )
