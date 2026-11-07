"""
PROTEA AI Scientist - Critic Agent (Adversarial Auditor)
Conducts adversarial audits, tests bypass mechanisms, checks data leakage, and enforces falsification.
"""

from typing import Dict, Any, List, Optional
from ai.ai_scientist.criticism.adversarial_review import AdversarialReviewer
from ai.ai_scientist.schema import AdversarialAuditReport


class CriticAgent:
    """
    Independent adversarial reviewer designed to actively challenge and falsify proposed discoveries.
    """

    def __init__(self):
        self.reviewer = AdversarialReviewer()

    def run(
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
    ) -> Dict[str, Any]:
        """
        Executes complete adversarial audit.
        """
        audit_report = self.reviewer.conduct_audit(
            hypothesis_id=hypothesis_id,
            hypothesis_statement=hypothesis_statement,
            falsification_criteria=falsification_criteria,
            experiment_design=experiment_design,
            experimental_results=experimental_results,
            pathway_context=pathway_context,
            training_database_edges=training_database_edges,
            predicted_pairs=predicted_pairs,
            robustness_score=robustness_score,
        )

        return {
            "audit_report": audit_report.dict() if hasattr(audit_report, "dict") else audit_report,
            "passed_audit": audit_report.passed_audit,
            "recommendation": audit_report.recommendation,
            "critical_flaws": audit_report.critical_flaws,
        }
