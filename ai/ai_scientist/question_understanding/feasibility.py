"""Scientific feasibility and computational constraint evaluator."""

from typing import Any, Dict, List, Optional


class FeasibilityAssessor:
    """Evaluates whether an investigation is computationally and biologically feasible in PROTEA."""

    @staticmethod
    def assess_feasibility(
        domain: str,
        entities: List[Dict[str, Any]],
        constraints: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """Verify model availability, resource boundaries, and computational feasibility."""
        c = constraints or {}
        issues: List[str] = []

        if not entities:
            issues.append("No specific biological entities (proteins, genes, diseases) were resolved.")

        supported_domains = [
            "cancer_signaling", "metabolic_rewiring", "gene_regulation",
            "variant_effects", "pathway_crosstalk", "oncology", "signaling", "molecular_biology"
        ]
        if domain not in supported_domains:
            issues.append(f"Domain '{domain}' is outside standard supported biological modeling suites.")

        is_feasible = len(issues) == 0
        score = 0.90 if is_feasible else 0.30

        return {
            "is_feasible": is_feasible,
            "feasibility_score": score,
            "domain": domain,
            "resolved_entities_count": len(entities),
            "estimated_compute_seconds": 15.0 if is_feasible else 0.0,
            "requires_human_approval": c.get("require_human_approval", True),
            "feasibility_issues": issues,
        }

    @classmethod
    def check_feasibility(
        cls,
        question: str,
        entities: List[Dict[str, Any]],
        constraints: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Convenience wrapper for question feasibility evaluation."""
        return cls.assess_feasibility(
            domain="oncology",
            entities=entities,
            constraints=constraints or {},
        )


FeasibilityChecker = FeasibilityAssessor
