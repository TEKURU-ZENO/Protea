"""
PROTEA Phase 10: Variant Parser
Handles VCF line-by-line parsing, multi-allelic splitting, and HGVS nomenclature parsing.
"""

from __future__ import annotations
import re
from typing import List, Dict, Any, Optional, Tuple
from ai.mutation_therapeutics.schema import GenomicVariant

# Standard 3-to-1 and 1-to-3 amino acid code mappings
AA_3_TO_1 = {
    "ALA": "A", "CYS": "C", "ASP": "D", "GLU": "E", "PHE": "F",
    "GLY": "G", "HIS": "H", "ILE": "I", "LYS": "K", "LEU": "L",
    "MET": "M", "ASN": "N", "PRO": "P", "GLN": "Q", "ARG": "R",
    "SER": "S", "THR": "T", "VAL": "V", "TRP": "W", "TYR": "Y",
    "TER": "*", "SEC": "U", "PYL": "O"
}
AA_1_TO_3 = {v: k for k, v in AA_3_TO_1.items()}


class VariantParser:
    """Parses VCF inputs and HGVS variant descriptions."""

    @staticmethod
    def parse_vcf_content(vcf_text: str, split_multiallelic: bool = True) -> List[GenomicVariant]:
        """
        Parses VCF lines into GenomicVariant objects.
        Automatically handles comments (#) and splits multi-allelic sites if requested.
        """
        variants: List[GenomicVariant] = []
        lines = vcf_text.strip().splitlines()

        for line in lines:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            fields = line.split("\t")
            if len(fields) < 5:
                # Fallback to space-split if tab was formatted as spaces
                fields = line.split()
                if len(fields) < 5:
                    continue

            chrom = fields[0]
            pos = int(fields[1])
            var_id = fields[2]
            ref = fields[3].upper()
            alt_field = fields[4].upper()
            qual = float(fields[5]) if len(fields) > 5 and fields[5] != "." else 100.0
            filter_val = fields[6] if len(fields) > 6 else "PASS"

            # Parse INFO fields
            info_dict: Dict[str, Any] = {}
            if len(fields) > 7 and fields[7] != ".":
                for item in fields[7].split(";"):
                    if "=" in item:
                        k, v = item.split("=", 1)
                        info_dict[k] = v
                    else:
                        info_dict[item] = True

            # Split multiallelic if needed
            alts = alt_field.split(",") if split_multiallelic else [alt_field]
            for alt in alts:
                variant = GenomicVariant(
                    chrom=chrom,
                    pos=pos,
                    ref=ref,
                    alt=alt.strip(),
                    id=var_id,
                    qual=qual,
                    filter=filter_val,
                    info=info_dict,
                    build="GRCh38"
                )
                variants.append(variant)

        return variants

    @staticmethod
    def parse_hgvs_p(hgvs_p: str) -> Dict[str, Any]:
        """
        Parses HGVS protein notation (e.g., 'p.Val600Glu', 'p.V600E', 'V600E', 'p.Thr790Met').
        Returns structured dict with wildtype, position, and mutant amino acids.
        """
        cleaned = hgvs_p.strip()
        if cleaned.startswith("p."):
            cleaned = cleaned[2:]

        # Case 1: 3-letter codes like Val600Glu or Val600*
        match_3 = re.match(r"^([A-Za-z]{3})([0-9]+)([A-Za-z]{3}|\*|=)$", cleaned)
        if match_3:
            wt_3 = match_3.group(1).upper()
            pos = int(match_3.group(2))
            mut_3 = match_3.group(3).upper()

            wt_1 = AA_3_TO_1.get(wt_3, wt_3)
            mut_1 = "*" if mut_3 in ["*", "TER"] else AA_3_TO_1.get(mut_3, mut_3)
            return {
                "wildtype_1": wt_1,
                "wildtype_3": wt_3,
                "position": pos,
                "mutant_1": mut_1,
                "mutant_3": mut_3,
                "mutation_type": "synonymous" if wt_1 == mut_1 else ("nonsense" if mut_1 == "*" else "missense"),
                "canonical_hgvs": f"p.{wt_3.capitalize()}{pos}{mut_3.capitalize() if mut_3 != '*' else '*'}"
            }

        # Case 2: 1-letter codes like V600E or T790M
        match_1 = re.match(r"^([A-Za-z])([0-9]+)([A-Za-z]|\*|=)$", cleaned)
        if match_1:
            wt_1 = match_1.group(1).upper()
            pos = int(match_1.group(2))
            mut_1 = match_1.group(3).upper()

            wt_3 = AA_1_TO_3.get(wt_1, wt_1)
            mut_3 = "Ter" if mut_1 == "*" else AA_1_TO_3.get(mut_1, mut_1)
            return {
                "wildtype_1": wt_1,
                "wildtype_3": wt_3,
                "position": pos,
                "mutant_1": mut_1,
                "mutant_3": mut_3,
                "mutation_type": "synonymous" if wt_1 == mut_1 else ("nonsense" if mut_1 == "*" else "missense"),
                "canonical_hgvs": f"p.{wt_3.capitalize()}{pos}{mut_3.capitalize() if mut_3 != '*' else '*'}"
            }

        # Case 3: Deletion/Insertion heuristics
        if "del" in cleaned:
            return {
                "wildtype_1": "X",
                "wildtype_3": "Unk",
                "position": 0,
                "mutant_1": "-",
                "mutant_3": "Del",
                "mutation_type": "inframe_indel",
                "canonical_hgvs": f"p.{cleaned}"
            }

        return {
            "wildtype_1": "X",
            "wildtype_3": "Unk",
            "position": 1,
            "mutant_1": "X",
            "mutant_3": "Unk",
            "mutation_type": "missense",
            "canonical_hgvs": f"p.{cleaned}"
        }

    @staticmethod
    def parse_hgvs_c(hgvs_c: str) -> Dict[str, Any]:
        """Parses coding DNA HGVS notation (e.g., 'c.1799T>A')."""
        cleaned = hgvs_c.strip()
        if cleaned.startswith("c."):
            cleaned = cleaned[2:]

        match = re.match(r"^([0-9+\-_]+)([A-Za-z]+)>([A-Za-z]+)$", cleaned)
        if match:
            return {
                "position_str": match.group(1),
                "ref_allele": match.group(2).upper(),
                "alt_allele": match.group(3).upper(),
                "canonical_hgvs": f"c.{cleaned}"
            }
        return {
            "position_str": "unknown",
            "ref_allele": "",
            "alt_allele": "",
            "canonical_hgvs": f"c.{cleaned}"
        }
