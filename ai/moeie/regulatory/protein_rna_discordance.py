"""
PROTEA Phase 11: Protein vs. Transcript Discordance & Phosphorylation Flux
Identifies post-transcriptional buffering, translation divergence, and phosphorylation-dependent signaling.
"""

from __future__ import annotations
from typing import Dict, List, Any


class ProteinRNADiscordanceAnalyzer:
    """Analyzes non-linear divergence between RNA expression, protein abundance, and phosphorylation."""

    @classmethod
    def analyze_discordance(
        cls,
        rna_expression: Dict[str, float],
        protein_abundance: Dict[str, float],
        phospho_abundance: Optional[Dict[str, float]] = None
    ) -> List[Dict[str, Any]]:
        """
        Calculates discordance z-score between RNA and protein.
        High discordance indicates post-transcriptional regulation, translational control, or protein degradation.
        High phospho ratio indicates post-translational signaling activation.
        """
        results: List[Dict[str, Any]] = []

        shared_genes = set(rna_expression.keys()).intersection(set(protein_abundance.keys()))
        for gene in sorted(shared_genes):
            rna_val = rna_expression[gene]
            prot_val = protein_abundance[gene]
            diff = prot_val - rna_val

            # Post-translational phosphorylation
            phospho_val = phospho_abundance.get(gene) if phospho_abundance else None
            is_hyperphosphorylated = (phospho_val is not None) and (phospho_val > prot_val + 1.2)

            # Categorize regulatory mode
            if diff > 1.5:
                reg_mode = "High Protein Stability / Enhanced Translation"
            elif diff < -1.5:
                reg_mode = "Rapid Proteasomal Degradation / RNA Buffering"
            else:
                reg_mode = "Concordant Synthesis"

            results.append({
                "gene": gene,
                "rna_log2": rna_val,
                "protein_log2": prot_val,
                "discordance_delta": round(diff, 2),
                "phospho_log2": phospho_val,
                "is_hyperphosphorylated": is_hyperphosphorylated,
                "regulatory_mode": reg_mode,
                "ptm_flux_active": is_hyperphosphorylated
            })

        return results
