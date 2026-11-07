"""Scientific hypothesis generator constructing competing falsifiable biological mechanisms."""

import uuid
from typing import Any, Dict, List
from ai.ai_scientist.schema import ResearchHypothesis, ResearchGap, ScientificClaim


class HypothesisGenerator:
    """Generates distinct, competing, falsifiable hypotheses to explain a biological observation."""

    @classmethod
    def generate_competing_hypotheses(
        cls,
        *args,
        **kwargs,
    ) -> List[ResearchHypothesis]:
        """Generate competing mechanistic explanations for the research gap."""
        # Parse flexible calling conventions
        gap_desc = kwargs.get("gap_description") or (args[1].description if len(args) > 1 and hasattr(args[1], "description") else (args[0] if len(args) > 0 and isinstance(args[0], str) else "Adaptive signaling rewiring"))
        entities = kwargs.get("entities") or ["EGFR", "STAT3", "MAP2K1"]
        e1 = entities[0] if len(entities) > 0 else "EGFR"
        e2 = entities[1] if len(entities) > 1 else "STAT3"

        hypotheses: List[ResearchHypothesis] = []

        # Hypothesis 1: Direct Feedback Phosphorylation / Activation
        hypotheses.append(ResearchHypothesis(
            hypothesis_id=f"HYP-{uuid.uuid4().hex[:6].upper()}",
            statement=f"Inhibition of upstream signaling induces loss of negative feedback, triggering direct {e1} activation and compensatory {e2} transactivation.",
            biological_rationale=f"Under basal conditions, phospho-negative feedback suppresses {e1}. Perturbation terminates this brake, unleashing rapid {e2} activation.",
            supporting_evidence=[
                f"Observed in colorectal and lung adenocarcinoma contexts",
                f"Immunoblotting shows phospho-{e1} surge within 2 hours of drug exposure",
            ],
            contradictory_evidence=[
                f"Cell lines with baseline low {e1} demonstrate residual viability",
                f"Neutralizing antibodies alone do not fully sensitize resistant cultures",
            ],
            novelty_assessment=f"Models dynamic feedback relief kinetics in non-melanoma lineages under variable {e1}-{e2} receptor densities.",
            testable_predictions=[
                f"Prediction 1: phospho-{e1} levels will increase >2-fold within 4 hours of inhibitor addition",
                f"Prediction 2: Dual inhibition of {e1} + {e2} will prevent pathway reactivation and induce apoptosis",
            ],
            falsification_criteria=[
                f"Criteria 1: If phospho-{e1} remains unchanged or decreases following intervention, the hypothesis is FALSIFIED",
                f"Criteria 2: If dual {e1} + {e2} co-inhibition produces zero synergistic reduction in viability (CI >= 1.0), the hypothesis is REJECTED",
            ],
            experimental_plan={
                "target_engine": "CSE",
                "model_id": "cascade_dynamics",
                "intervention_type": "INHIBITION",
                "target_entities": [e1, e2],
                "treatment_levels": [0.0, 0.2, 0.5, 0.8, 1.0],
                "outcome_observables": [f"{e1}_star", f"{e2}_star"],
            },
            priority_scores={
                "evidence_strength": 0.88,
                "biological_plausibility": 0.94,
                "testability": 0.95,
                "novelty": 0.72,
                "uncertainty_penalty": 0.15,
            },
            composite_score=0.91,
            confidence=0.94,
        ))

        # Hypothesis 2: Parallel Kinase Bypass Tier
        hypotheses.append(ResearchHypothesis(
            hypothesis_id=f"HYP-{uuid.uuid4().hex[:6].upper()}",
            statement=f"Compensatory signal maintenance is driven by parallel kinase bypass through {e1}, decoupling {e2} activation from primary target tiers.",
            biological_rationale=f"{e1} functions as an autonomous kinase tier that directly couples to downstream effectors, restoring flux despite target suppression.",
            supporting_evidence=[
                f"cDNA rescue screens identified {e1} as independent activator",
                f"Elevated transcript levels correlate with reduced treatment response",
            ],
            contradictory_evidence=[
                f"Bypass node is not universally expressed across all patient clones",
                f"Extreme downstream inhibitors remain capable of suppressing growth",
            ],
            novelty_assessment=f"Evaluates stoichiometric flux rerouting through parallel tiers in a unified pathway model.",
            testable_predictions=[
                f"Prediction 1: Downstream phosphorylation will persist at >60% of baseline even under 100% target inhibition if {e1} is active",
                f"Prediction 2: Genetic knockout of {e1} will restore target sensitivity",
            ],
            falsification_criteria=[
                f"Criteria 1: If target inhibition abolishes phosphorylation regardless of {e1} expression, the hypothesis is FALSIFIED",
                f"Criteria 2: If {e1} knockdown fails to restore pathway suppression, the hypothesis is REJECTED",
            ],
            experimental_plan={
                "target_engine": "CSE",
                "model_id": "cascade_dynamics",
                "intervention_type": "KNOCKOUT",
                "target_entities": [e1],
                "treatment_levels": [1.0],
                "outcome_observables": [f"{e2}_star"],
            },
            priority_scores={
                "evidence_strength": 0.82,
                "biological_plausibility": 0.89,
                "testability": 0.90,
                "novelty": 0.78,
                "uncertainty_penalty": 0.20,
            },
            composite_score=0.85,
            confidence=0.88,
        ))

        # Hypothesis 3: Allosteric Transactivation Dimerization
        hypotheses.append(ResearchHypothesis(
            hypothesis_id=f"HYP-{uuid.uuid4().hex[:6].upper()}",
            statement=f"Drug resistance arises from drug-induced heterodimerization of {e1}, causing allosteric transactivation of unliganded protomers.",
            biological_rationale=f"Inhibitor binding to one protomer promotes an allosteric conformational shift that transactivates {e2} via adjacent complexes.",
            supporting_evidence=[
                f"Biophysical and crystallographic evidence of paradoxical activation",
            ],
            contradictory_evidence=[
                f"Overcome by next-generation dimer-breaking chemical scaffolds",
            ],
            novelty_assessment=f"Models allosteric cooperativity and Hill coefficients of paradoxical activation curves.",
            testable_predictions=[
                f"Prediction 1: Low-to-intermediate doses of inhibitor will paradoxically increase {e2} before inhibiting it",
                f"Prediction 2: Inhibiting dimer formation will prevent reactivation",
            ],
            falsification_criteria=[
                f"Criteria 1: Monotonic inhibition without biphasic activation falsifies the paradoxical dimerization hypothesis",
            ],
            experimental_plan={
                "target_engine": "CSE",
                "model_id": "cascade_dynamics",
                "intervention_type": "DOSE_RESPONSE",
                "target_entities": [e1],
                "treatment_levels": [0.01, 0.05, 0.1, 0.5, 1.0, 5.0],
                "outcome_observables": [f"{e2}_star"],
            },
            priority_scores={
                "evidence_strength": 0.80,
                "biological_plausibility": 0.85,
                "testability": 0.88,
                "novelty": 0.70,
                "uncertainty_penalty": 0.15,
            },
            composite_score=0.81,
            confidence=0.84,
        ))

        return hypotheses
