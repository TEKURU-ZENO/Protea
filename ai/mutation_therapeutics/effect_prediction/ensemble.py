"""
PROTEA Phase 10: Ensemble Effect Predictor
Combines sequence language models, evolutionary conservation, domain maps, and functional classification.
"""

from __future__ import annotations
from typing import Dict, Any, Optional
from ai.mutation_therapeutics.schema import FunctionalEffect, FunctionalClass, StabilityClass, ProteinMutation
from ai.mutation_therapeutics.effect_prediction.missense_scorer import MissenseScorer
from ai.mutation_therapeutics.effect_prediction.domain_disruption import DomainDisruptionAnalyzer
from ai.mutation_therapeutics.effect_prediction.functional_classifier import FunctionalClassifier
from ai.mutation_therapeutics.stability.folding_stability import FoldingStabilityPredictor


class EnsembleEffectPredictor:
    """Predicts composite effect of amino acid substitutions."""

    @classmethod
    def predict_effect(
        cls,
        gene_symbol: str,
        wildtype_aa: str,
        position: int,
        mutant_aa: str,
        protein_id: Optional[str] = None
    ) -> FunctionalEffect:
        """Runs the complete effect prediction pipeline."""
        pid = protein_id or f"PROT_{gene_symbol}"
        mutation_label = f"{gene_symbol}_{wildtype_aa}{position}{mutant_aa}"

        wt = wildtype_aa.upper()
        mut = mutant_aa.upper()

        # 1. Missense scoring (ESM & conservation)
        scorer_res = MissenseScorer.score_mutation(wt, mut, position)
        esm_delta = scorer_res["esm_log_odds_delta"]
        conservation = scorer_res["conservation_score"]

        # 2. Domain disruption
        domain_res = DomainDisruptionAnalyzer.analyze_disruption(gene_symbol, position)

        # 3. Functional classification
        func_res = FunctionalClassifier.classify_mechanism(
            gene_symbol=gene_symbol,
            wildtype_aa=wt,
            position=position,
            mutant_aa=mut,
            domain_info=domain_res,
            missense_scores=scorer_res
        )

        # 4. Thermodynamic folding DeltaDeltaG
        if wt == mut:
            ddg = 0.0
            stability_class = StabilityClass.NEUTRAL
            agg_delta = 0.0
        else:
            stab_res = FoldingStabilityPredictor.predict_ddg(wt, mut, burial_fraction=0.6)
            ddg = stab_res["ddg_kcal_mol"]
            # Boost ddg if catalytic core or zinc finger disrupted (e.g. TP53 R175H)
            if domain_res.get("is_catalytic_site", False):
                ddg = round(ddg + 1.2, 2)
            stability_class = stab_res["stability_class"]
            if ddg >= 3.0:
                stability_class = StabilityClass.SEVERELY_DESTABILIZING
            elif ddg >= 1.2:
                stability_class = StabilityClass.DESTABILIZING

            # Aggregation delta
            agg_delta = round(0.1 + (0.3 if mut in ["I", "L", "V", "F", "W", "Y"] else 0.0), 2)

        confidence = round((scorer_res["confidence"] + func_res["confidence"]) / 2.0, 2)

        return FunctionalEffect(
            protein_id=pid,
            mutation_label=mutation_label,
            ddg_kcal_mol=ddg,
            stability_classification=stability_class,
            functional_classification=func_res["functional_class"],
            esm_log_odds_delta=esm_delta,
            evolutionary_conservation_score=conservation,
            catalytic_site_disrupted=domain_res["is_catalytic_site"],
            aggregation_propensity_delta=agg_delta,
            confidence_score=confidence
        )
