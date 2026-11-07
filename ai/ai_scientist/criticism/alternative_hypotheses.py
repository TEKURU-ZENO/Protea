"""
PROTEA AI Scientist - Alternative Hypotheses Evaluator
Explores whether alternative pathways, parallel mechanisms, or compensatory signaling explain results.
"""

from typing import Dict, Any, List


class AlternativeHypothesisEvaluator:
    """
    Formulates and evaluates alternative mechanistic explanations that could account
    for experimental observations without invoking the primary hypothesis.
    """

    KNOWN_COMPENSATORY_PATTERNS = [
        {
            "name": "Bypass Signaling Pathway",
            "description": "Downstream activation occurs via a parallel receptor tyrosine kinase or bypass cascade rather than direct target mediation.",
            "indicator": "Residual phosphorylation/activity remains upon selective target knockdown.",
        },
        {
            "name": "Non-Specific Metabolic Degradation",
            "description": "Observed phenotype stems from metabolic stress or general proteasomal overload rather than specific target engagement.",
            "indicator": "Vehicle or scrambled control displays dose-dependent stress markers.",
        },
        {
            "name": "Feedback Loop Reactivation",
            "description": "Short-term inhibition induces transcriptional rebound via negative feedback relief (e.g. ERK/MAPK rebound).",
            "indicator": "Transient suppression followed by rebound expression at late time points.",
        },
        {
            "name": "Direct Allosteric Cross-Talk",
            "description": "Effector change is mediated by steric or crowding effects in multiprotein complex rather than catalytic inhibition.",
            "indicator": "Catalytically inactive mutant retains partial regulatory activity.",
        },
    ]

    def evaluate_alternatives(
        self,
        hypothesis_statement: str,
        experimental_results: Dict[str, Any],
        pathway_context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Evaluates plausible alternative explanations for the observed findings.
        """
        evaluated_alternatives = []
        observed_p_val = experimental_results.get("p_value", 0.05)
        effect_size = abs(experimental_results.get("effect_size", 0.0))

        for pattern in self.KNOWN_COMPENSATORY_PATTERNS:
            # Calculate plausibility of alternative based on effect size and pathway connectivity
            plausibility = 0.35  # baseline alternative plausibility
            if effect_size < 1.0:
                plausibility += 0.25  # moderate effect sizes are easier to explain by bypass
            if pathway_context.get("has_parallel_pathways", False):
                plausibility += 0.2

            plausibility = min(0.95, round(plausibility, 2))

            evaluated_alternatives.append({
                "mechanism_name": pattern["name"],
                "description": pattern["description"],
                "indicator": pattern["indicator"],
                "plausibility_score": plausibility,
                "discriminating_experiment_needed": f"Test {pattern['name']} by selective co-inhibition or rescue assays.",
            })

        # Rank alternatives by plausibility
        evaluated_alternatives.sort(key=lambda x: x["plausibility_score"], reverse=True)
        top_alternative = evaluated_alternatives[0] if evaluated_alternatives else None

        return {
            "alternatives_evaluated": len(evaluated_alternatives),
            "alternative_explanations": evaluated_alternatives,
            "top_competing_alternative": top_alternative,
            "is_ruled_out": bool(top_alternative and top_alternative["plausibility_score"] < 0.5),
            "critical_warning": (
                f"Primary hypothesis must be tested against '{top_alternative['mechanism_name']}' before claiming definitive discovery."
                if top_alternative and top_alternative["plausibility_score"] >= 0.5
                else "No high-plausibility competing alternative identified."
            ),
        }
