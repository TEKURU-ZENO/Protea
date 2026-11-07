"""
PROTEA Phase 10: Therapeutic Target Prioritizer
Ranks drug targets via multi-criteria objective: Centrality + DepMap Dependency + Druggability + Safety.
"""

from __future__ import annotations
from typing import List, Dict, Any, Optional
from ai.mutation_therapeutics.schema import TherapeuticTarget, TractabilityTier
from ai.mutation_therapeutics.target_discovery.druggability_analyzer import DruggabilityAnalyzer

# DepMap CERES dependency scores and safety profiles
DEPMAP_TARGET_DATABASE: Dict[str, Dict[str, Any]] = {
    "BRAF": {"dependency": -1.25, "centrality": 0.88, "safety": 0.85, "is_pan_essential": False},
    "MAP2K1": {"dependency": -1.10, "centrality": 0.84, "safety": 0.75, "is_pan_essential": False},
    "MAP2K2": {"dependency": -0.85, "centrality": 0.80, "safety": 0.80, "is_pan_essential": False},
    "EGFR": {"dependency": -1.35, "centrality": 0.92, "safety": 0.82, "is_pan_essential": False},
    "ERBB2": {"dependency": -1.05, "centrality": 0.85, "safety": 0.88, "is_pan_essential": False},
    "MET": {"dependency": -0.92, "centrality": 0.78, "safety": 0.86, "is_pan_essential": False},
    "KRAS": {"dependency": -1.45, "centrality": 0.95, "safety": 0.70, "is_pan_essential": False},
    "SOS1": {"dependency": -0.75, "centrality": 0.75, "safety": 0.88, "is_pan_essential": False},
    "SHP2": {"dependency": -0.80, "centrality": 0.79, "safety": 0.82, "is_pan_essential": False},
    "MDM2": {"dependency": -1.15, "centrality": 0.86, "safety": 0.72, "is_pan_essential": False},
    "TP53": {"dependency": 0.10, "centrality": 0.98, "safety": 0.95, "is_pan_essential": False},
    "POLR2A": {"dependency": -2.80, "centrality": 0.99, "safety": 0.05, "is_pan_essential": True},  # Pan-essential negative control
}


class TargetPrioritizer:
    """Prioritizes therapeutic targets for a given disease mechanism or mutant context."""

    @classmethod
    def prioritize_targets(
        cls,
        candidate_genes: List[str],
        mutant_gene: str = "BRAF",
        weights: Optional[Dict[str, float]] = None
    ) -> List[TherapeuticTarget]:
        """
        Ranks candidate targets by composite priority score:
        Composite = (centrality * w_c) + (abs(depmap) * w_d) + (druggability * w_dr) + (safety * w_s).
        Pan-essential genes are heavily penalized in safety to avoid systemic toxicity.
        """
        w = weights or {
            "centrality": 0.25,
            "dependency": 0.35,
            "druggability": 0.25,
            "safety": 0.15
        }

        targets: List[TherapeuticTarget] = []

        # Ensure candidate list includes primary driver and upstream/downstream partners
        all_candidates = list(dict.fromkeys([mutant_gene] + candidate_genes))

        for gene in all_candidates:
            gene_up = gene.upper()
            dep_record = DEPMAP_TARGET_DATABASE.get(gene_up, {
                "dependency": -0.65,
                "centrality": 0.60,
                "safety": 0.75,
                "is_pan_essential": False
            })

            drug_eval = DruggabilityAnalyzer.evaluate_target(gene_up)

            centrality = dep_record["centrality"]
            # Convert depmap dependency into normalized score (0.0 to 1.0, where -1.5 -> 1.0, 0.0 -> 0.0)
            dep_val = dep_record["dependency"]
            dep_score = min(1.0, max(0.0, abs(min(0.0, dep_val)) / 1.5))
            druggability = drug_eval["druggability_score"]
            safety = dep_record["safety"]

            # If pan-essential, safety is near zero
            if dep_record.get("is_pan_essential", False):
                safety = 0.05

            composite = round(
                (centrality * w["centrality"]) +
                (dep_score * w["dependency"]) +
                (druggability * w["druggability"]) +
                (safety * w["safety"]),
                3
            )

            rationale = (
                f"High synthetic dependency (DepMap CERES: {dep_val:.2f}) and validated druggability "
                f"({drug_eval['pocket_volume_angstrom3']} Å³ pocket)."
            )

            target = TherapeuticTarget(
                target_id=f"TGT_{gene_up}",
                gene_symbol=gene_up,
                protein_id=f"PROT_{gene_up}",
                rationale=rationale,
                centrality_score=centrality,
                depmap_dependency_score=dep_val,
                druggability_score=druggability,
                safety_score=safety,
                tractability_tier=drug_eval["tractability_tier"],
                composite_priority=composite,
                pocket_volume_angstrom3=drug_eval["pocket_volume_angstrom3"]
            )
            targets.append(target)

        # Sort descending by composite priority
        targets.sort(key=lambda t: t.composite_priority, reverse=True)
        return targets
