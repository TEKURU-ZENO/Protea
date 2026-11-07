"""
PROTEA Phase 10: ACMG/AMP Variant Classifier
Automates standard ACMG/AMP variant interpretation guidelines combining PVS, PS, PM, PP, and Benign criteria.
"""

from __future__ import annotations
from typing import Dict, List, Any, Tuple
from ai.mutation_therapeutics.schema import ACMGClass, FunctionalClass


class ACMGClassifier:
    """Classifies genetic variants using ACMG/AMP evidence synthesis rules."""

    @classmethod
    def evaluate_criteria(
        cls,
        gene_symbol: str,
        wildtype_aa: str,
        position: int,
        mutant_aa: str,
        functional_effect: Optional[Dict[str, Any]] = None,
        annotation_info: Optional[Dict[str, Any]] = None,
        is_known_hotspot: bool = False
    ) -> Tuple[ACMGClass, List[str]]:
        """
        Evaluates applicable ACMG criteria and calculates classification.
        Rules:
        - Pathogenic:
          * 1 Very Strong (PVS1) AND >= 1 Strong (PS) OR >= 2 Moderate (PM) OR >= 1 Moderate and 1 Supporting (PP)
          * >= 2 Strong (PS)
          * 1 Strong (PS) AND >= 3 Moderate (PM)
        - Likely Pathogenic:
          * 1 Very Strong (PVS1) AND 1 Moderate (PM)
          * 1 Strong (PS) AND 1-2 Moderate (PM)
          * >= 3 Moderate (PM)
        - Benign / Likely Benign:
          * High population allele frequency (BA1 / BS1)
        - Uncertain Significance (VUS):
          * Criteria not meeting above rules or conflicting evidence
        """
        criteria: List[str] = []

        # Check population frequency in gnomAD
        gnomad_af = 0.0
        if annotation_info and "gnomad" in annotation_info:
            gnomad_af = annotation_info["gnomad"].get("af", 0.0)

        if gnomad_af > 0.05:
            criteria.append("BA1")  # Stand-alone benign allele frequency > 5%
            return ACMGClass.BENIGN, criteria
        elif gnomad_af > 0.01:
            criteria.append("BS1")  # Strong benign allele frequency > 1%
        elif gnomad_af < 0.0001:
            criteria.append("PM2")  # Extremely low frequency in controls / gnomAD

        # Check stop codon / null
        if mutant_aa == "*":
            if gene_symbol.upper() in ["TP53", "BRCA1", "BRCA2", "PTEN", "RB1"]:
                criteria.append("PVS1")  # Null variant in tumor suppressor where LoF is disease mechanism

        # Check mutational hotspot / functional domain (PM1)
        if is_known_hotspot or (gene_symbol.upper() in ["BRAF", "KRAS", "EGFR"] and position in [12, 13, 61, 600, 790, 858]):
            criteria.append("PM1")  # Located in mutational hotspot and/or critical domain

        # Check functional studies (PS3)
        if annotation_info and annotation_info.get("is_oncogenic_hotspot", False):
            criteria.append("PS3")  # Well-established in vitro / in vivo functional studies supportive of damaging effect
            criteria.append("PS4")  # Prevalence in affected individuals significantly increased

        # Check computational prediction (PP3)
        if functional_effect:
            esm_delta = functional_effect.get("esm_log_odds_delta", 0.0)
            if esm_delta < -5.0:
                criteria.append("PP3")  # Multiple lines of computational evidence support a deleterious effect

        # Check ClinVar / expert assertions (PP5)
        if annotation_info and "clinvar" in annotation_info:
            clin_sig = str(annotation_info["clinvar"].get("significance", "")).lower()
            if "pathogenic" in clin_sig:
                criteria.append("PP5")  # Reputable source reports variant as pathogenic

        # Evaluate composite ACMG matrix
        pvs = sum(1 for c in criteria if c.startswith("PVS"))
        ps = sum(1 for c in criteria if c.startswith("PS"))
        pm = sum(1 for c in criteria if c.startswith("PM"))
        pp = sum(1 for c in criteria if c.startswith("PP"))
        ba = sum(1 for c in criteria if c.startswith("BA"))
        bs = sum(1 for c in criteria if c.startswith("BS"))

        if ba > 0 or bs >= 2:
            classification = ACMGClass.BENIGN
        elif bs == 1:
            classification = ACMGClass.LIKELY_BENIGN
        elif (pvs >= 1 and (ps >= 1 or pm >= 2 or (pm >= 1 and pp >= 1))) or ps >= 2 or (ps >= 1 and pm >= 3):
            classification = ACMGClass.PATHOGENIC
        elif (pvs >= 1 and pm >= 1) or (ps >= 1 and pm >= 1) or pm >= 3 or (pm >= 2 and pp >= 2):
            classification = ACMGClass.LIKELY_PATHOGENIC
        else:
            classification = ACMGClass.VUS

        return classification, criteria
