"""Research objective decomposition into sequential research milestones."""

from typing import Any, Dict, List


class ObjectiveDecomposer:
    """Decomposes an overarching biological research question into ordered sub-objectives."""

    STANDARD_WORKFLOW_OBJECTIVES = [
        "1. Conduct literature review and extract cited experimental claims",
        "2. Synthesize known mechanisms and identify knowledge gaps",
        "3. Formulate competing testable hypotheses with falsification criteria",
        "4. Design in-silico computational experiments with proper controls",
        "5. Execute simulations and perturbations using PROTEA engines",
        "6. Perform statistical significance and effect size evaluation",
        "7. Subject findings to adversarial review by the Critic Agent",
        "8. Generate evidence-grounded scientific report and reproducibility package",
    ]

    @classmethod
    def decompose(cls, question: str, domain: str) -> List[str]:
        """Generate tailored sub-objectives based on domain and question context."""
        objectives = list(cls.STANDARD_WORKFLOW_OBJECTIVES)

        q_lower = question.lower()
        if "resistance" in q_lower or "compensatory" in q_lower:
            objectives.insert(3, "3b. Specifically map upstream/downstream bypass loops and feedback reactivation")
        if "metabolism" in q_lower or "flux" in q_lower:
            objectives.insert(4, "4b. Configure stoichiometric metabolic constraints and biomass yield objectives")

        return objectives
