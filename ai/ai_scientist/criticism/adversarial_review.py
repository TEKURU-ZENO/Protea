"""
PROTEA AI Scientist - Adversarial Reviewer (Critic Agent)
Synthesizes comprehensive adversarial audits across alternatives, confounders, leakage, and falsification.
"""

from typing import Dict, Any, List, Optional
import uuid
from ai.ai_scientist.schema import AdversarialAuditReport
from ai.ai_scientist.criticism.alternative_hypotheses import AlternativeHypothesisEvaluator
from ai.ai_scientist.criticism.confounder_detection import ConfounderDetector
from ai.ai_scientist.criticism.leakage_detection import LeakageDetector
from ai.ai_scientist.criticism.falsification_review import FalsificationReviewer


class AdversarialReviewer:
    """
    Acts as the adversarial Critic Agent.
    Systematically attempts to challenge, falsify, and expose weaknesses in proposed discoveries.
    """

    def __init__(self):
        self.alternative_evaluator = AlternativeHypothesisEvaluator()
        self.confounder_detector = ConfounderDetector()
        self.leakage_detector = LeakageDetector()
        self.falsification_reviewer = FalsificationReviewer()

    def conduct_audit(
        self,
        hypothesis_id: str,
        hypothesis_statement: str,
        falsification_criteria: List[str],
        experiment_design: Dict[str, Any],
        experimental_results: Dict[str, Any],
        pathway_context: Dict[str, Any],
        training_database_edges: Optional[set] = None,
        predicted_pairs: Optional[List[Dict[str, str]]] = None,
        robustness_score: float = 0.85,
    ) -> AdversarialAuditReport:
        """
        Runs complete adversarial audit of a hypothesis and its experimental validation.
        """
        audit_id = f"audit_{uuid.uuid4().hex[:8]}"

        # 1. Alternative Hypotheses
        alt_res = self.alternative_evaluator.evaluate_alternatives(
            hypothesis_statement=hypothesis_statement,
            experimental_results=experimental_results,
            pathway_context=pathway_context,
        )

        # 2. Confounder Detection
        conf_res = self.confounder_detector.audit_confounders(experiment_design)

        # 3. Leakage Detection
        leak_res = self.leakage_detector.audit_leakage(
            predicted_pairs=predicted_pairs or [],
            training_database_edges=training_database_edges or set(),
            validation_engine_name=experiment_design.get("validation_engine", "CSE"),
            inference_engine_name=experiment_design.get("inference_engine", "IPE"),
        )

        # 4. Falsification Review
        fals_res = self.falsification_reviewer.review_falsification(
            falsification_criteria=falsification_criteria,
            observed_outcomes=experimental_results,
            statistical_significance=experimental_results.get("statistically_significant", True),
        )

        # Determine Recommendation
        critical_flaws = []
        if fals_res["is_falsified"]:
            critical_flaws.append("Hypothesis triggered pre-registered falsification criteria.")
        if not leak_res["passed_leakage_audit"]:
            critical_flaws.append(leak_res["critical_warning"])
        if not conf_res["is_valid"]:
            critical_flaws.append("High-severity experimental confounders detected.")
        if robustness_score < 0.5:
            critical_flaws.append("Simulation results fragile to small kinetic/topological shifts.")

        warnings = []
        if not alt_res["is_ruled_out"]:
            warnings.append(alt_res["critical_warning"])
        if conf_res["confounders"]:
            warnings.extend([c["description"] for c in conf_res["confounders"]])

        if critical_flaws:
            recommendation = "REJECTED_HYPOTHESIS"
            passed = False
        elif warnings:
            recommendation = "REQUIRES_REVISION"
            passed = True  # conditionally passed
        else:
            recommendation = "APPROVED_FOR_PUBLICATION"
            passed = True

        return AdversarialAuditReport(
            audit_id=audit_id,
            hypothesis_id=hypothesis_id,
            critic_agent="PROTEA_Critic_Agent_v1",
            recommendation=recommendation,
            passed_audit=passed,
            alternative_hypotheses_evaluated=[a["mechanism_name"] for a in alt_res["alternative_explanations"]],
            confounders_detected=[c["name"] for c in conf_res["confounders"]],
            leakage_detected=not leak_res["passed_leakage_audit"],
            falsification_tested=True,
            robustness_score=robustness_score,
            critical_flaws=critical_flaws,
            recommendation_notes=warnings or ["All adversarial checks passed without disqualifying flaws."],
        )
