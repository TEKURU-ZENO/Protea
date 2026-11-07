"""
PROTEA Phase 10: Functional Classifier
Categorizes mutations into Loss-of-Function, Gain-of-Function, Dominant-Negative, or Neutral.
Enforces Scientific Guardrail: Pathogenicity != Mechanism.
"""

from __future__ import annotations
from typing import Dict, Any, Optional
from ai.mutation_therapeutics.schema import FunctionalClass, ProteinMutation

# Curated gene mechanistic modes (oncogenes vs tumor suppressors)
GENE_MECHANISTIC_CLASSES: Dict[str, str] = {
    "BRAF": "oncogene_kinase",
    "EGFR": "oncogene_rtk",
    "KRAS": "oncogene_gtpase",
    "PIK3CA": "oncogene_kinase",
    "MYC": "oncogene_tf",
    "TP53": "tumor_suppressor_tf",
    "PTEN": "tumor_suppressor_phosphatase",
    "RB1": "tumor_suppressor_cellcycle",
    "BRCA1": "tumor_suppressor_dna_repair",
    "BRCA2": "tumor_suppressor_dna_repair",
    "APC": "tumor_suppressor_wnt"
}

# Known activating gain-of-function mutation signatures
KNOWN_GOF_SIGNATURES = {
    ("BRAF", 600),
    ("KRAS", 12),
    ("KRAS", 13),
    ("KRAS", 61),
    ("EGFR", 858),
    ("EGFR", 790),  # resistance & constitutive activity
    ("PIK3CA", 542),
    ("PIK3CA", 545),
    ("PIK3CA", 1047),
}


class FunctionalClassifier:
    """
    Classifies mutation mechanistic consequence.
    Distinguishes Loss-of-Function from Gain-of-Function and Dominant-Negative.
    """

    @classmethod
    def classify_mechanism(
        cls,
        gene_symbol: str,
        wildtype_aa: str,
        position: int,
        mutant_aa: str,
        domain_info: Optional[Dict[str, Any]] = None,
        missense_scores: Optional[Dict[str, Any]] = None,
        clinvar_significance: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Classifies functional mode using gene role context, domain position, and structural clues.
        """
        gene = gene_symbol.upper()
        gene_class = GENE_MECHANISTIC_CLASSES.get(gene, "unknown")

        # Check for synonymous change first
        if wildtype_aa.upper() == mutant_aa.upper():
            return {
                "functional_class": FunctionalClass.NEUTRAL_BENIGN,
                "confidence": 0.98,
                "rationale": "Synonymous substitution preserving wildtype amino acid identity."
            }

        # Check stop gain (nonsense)
        if mutant_aa == "*":
            return {
                "functional_class": FunctionalClass.LOSS_OF_FUNCTION,
                "confidence": 0.95,
                "rationale": "Premature termination codon causing truncated non-functional protein or nonsense-mediated decay."
            }

        # Check known GoF signatures
        if (gene, position) in KNOWN_GOF_SIGNATURES:
            return {
                "functional_class": FunctionalClass.GAIN_OF_FUNCTION,
                "confidence": 0.96,
                "rationale": f"Established oncogenic activating hotspot in {gene} disrupting auto-inhibition or hydrolysis."
            }

        # Tumor suppressor logic
        if "tumor_suppressor" in gene_class:
            if domain_info and domain_info.get("is_catalytic_site", False):
                return {
                    "functional_class": FunctionalClass.LOSS_OF_FUNCTION,
                    "confidence": 0.91,
                    "rationale": f"Disruption of essential catalytic or DNA-binding core in tumor suppressor {gene}."
                }
            if gene == "TP53" and position in [175, 248, 273]:
                return {
                    "functional_class": FunctionalClass.DOMINANT_NEGATIVE,
                    "confidence": 0.92,
                    "rationale": "Conformational destabilization exhibiting dominant-negative inhibition over wildtype tetramers."
                }
            return {
                "functional_class": FunctionalClass.LOSS_OF_FUNCTION,
                "confidence": 0.82,
                "rationale": f"Deleterious variant in tumor suppressor {gene} impairing protective growth arrest or repair."
            }

        # Oncogene kinase / receptor logic
        if "oncogene" in gene_class:
            if domain_info and (domain_info.get("is_activation_loop") or domain_info.get("is_gatekeeper")):
                return {
                    "functional_class": FunctionalClass.GAIN_OF_FUNCTION,
                    "confidence": 0.89,
                    "rationale": f"Mutation in regulatory activation segment or gatekeeper in oncogene {gene}."
                }

        # Default fallback
        is_del = missense_scores.get("predicted_deleterious", False) if missense_scores else False
        if is_del:
            return {
                "functional_class": FunctionalClass.LOSS_OF_FUNCTION,
                "confidence": 0.70,
                "rationale": "Deleterious missense change predicted to reduce protein stability or native activity."
            }

        return {
            "functional_class": FunctionalClass.NEUTRAL_BENIGN,
            "confidence": 0.75,
            "rationale": "Conservative change with minimal predicted perturbation to native function."
        }
