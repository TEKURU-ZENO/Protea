"""
PROTEA AI Scientist - Scientific Report & Evidence Dossier Builder
Generates executive research summaries, evidence dossiers, and translational takeaway cards.
"""

from typing import Dict, Any, List


class ReportBuilder:
    """
    Constructs high-level executive summaries and dossiers for researchers and stakeholders.
    """

    def build_executive_summary(
        self,
        investigation_id: str,
        question: str,
        top_hypothesis: Dict[str, Any],
        adversarial_result: Dict[str, Any],
        key_findings: List[str],
    ) -> Dict[str, Any]:
        """
        Creates a concise executive briefing document.
        """
        status = "Discovery Validated" if adversarial_result.get("passed_audit", False) else "Inconclusive / Falsified"

        return {
            "investigation_id": investigation_id,
            "research_question": question,
            "overall_status": status,
            "lead_hypothesis": top_hypothesis.get("statement", ""),
            "confidence_score": top_hypothesis.get("confidence", 0.0),
            "key_findings": key_findings,
            "adversarial_audit_verdict": adversarial_result.get("recommendation", "UNKNOWN"),
            "critical_caveats": adversarial_result.get("critical_flaws", []),
            "next_experimental_step": (
                "Proceed to in-vitro / wet-lab validation targeting the predicted interaction."
                if status == "Discovery Validated"
                else "Revise mechanistic model or address detected confounders."
            ),
        }

    def build_evidence_dossier(
        self,
        claims: List[Dict[str, Any]],
        gaps: List[Dict[str, Any]],
        hypotheses: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Builds a comprehensive evidence dossier synthesizing all supporting literature and gap analyses.
        """
        return {
            "total_extracted_claims": len(claims),
            "claims_summary": [
                {
                    "claim_id": c.get("claim_id"),
                    "statement": c.get("statement"),
                    "confidence": c.get("confidence"),
                    "citations_count": len(c.get("citations", [])),
                }
                for c in claims[:10]
            ],
            "identified_gaps": [
                {
                    "gap_id": g.get("gap_id"),
                    "gap_type": g.get("gap_type"),
                    "description": g.get("description"),
                }
                for g in gaps
            ],
            "competing_hypotheses_evaluated": len(hypotheses),
        }
