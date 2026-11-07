"""Natural language biological research question parser and domain classifier."""

import re
from typing import Any, Dict, List


class ResearchQuestionParser:
    """Parses open-ended scientific inquiries into structured research domains and intents."""

    DOMAIN_KEYWORDS = {
        "cancer_signaling": ["resistance", "compensatory", "kinase", "inhibitor", "tumor", "cancer", "mapk", "egfr", "braf", "stat3", "oncology", "nsclc"],
        "oncology": ["cancer", "tumor", "nsclc", "carcinoma", "melanoma", "leukemia", "egfr"],
        "metabolic_rewiring": ["metabolism", "flux", "glycolysis", "tca", "atp", "fermentation", "warburg"],
        "gene_regulation": ["transcription", "promoter", "repressor", "operon", "mrna", "translation", "expression"],
        "variant_effects": ["mutation", "variant", "missense", "structural stability", "pathogenic"],
        "signaling": ["crosstalk", "feedback", "synergy", "synthetic lethal", "cascade", "phosphorylation"],
    }

    @classmethod
    def parse_question(cls, question: str) -> Dict[str, Any]:
        """Parse natural language question into structured research parameters."""
        q_lower = question.lower()

        matched_domain = "oncology"
        max_matches = 0
        for domain, kws in cls.DOMAIN_KEYWORDS.items():
            matches = sum(1 for kw in kws if kw in q_lower)
            if matches > max_matches:
                max_matches = matches
                matched_domain = domain

        if matched_domain == "cancer_signaling":
            matched_domain = "oncology"

        intervention_type = "OBSERVATIONAL"
        if any(w in q_lower for w in ["inhibit", "inhibition", "block", "drug", "treatment"]):
            intervention_type = "PROTEIN_INHIBITION"
        elif any(w in q_lower for w in ["knockout", "ko", "loss of function", "null"]):
            intervention_type = "GENE_KNOCKOUT"
        elif any(w in q_lower for w in ["overexpress", "gain of function"]):
            intervention_type = "OVEREXPRESSION"
        elif any(w in q_lower for w in ["mutation", "variant"]):
            intervention_type = "MUTATION_EFFECT"

        is_underspecified = len(question.strip().split()) < 4

        # Extract capital abbreviations as candidate entities
        entities = [
            w for w in re.findall(r'\b[A-Z][A-Z0-9_]{1,7}\b', question)
            if w not in {"DOES", "WHAT", "HOW", "WHY", "THE", "AND", "FOR", "WITH", "IS", "IN", "OF", "TO"}
        ]

        return {
            "parsed_question": question.strip(),
            "raw_question": question.strip(),
            "domain": matched_domain,
            "intervention_intent": intervention_type,
            "extracted_entities": list(dict.fromkeys(entities)),
            "is_underspecified": is_underspecified,
            "requires_clarification": is_underspecified,
        }

    @classmethod
    def parse(cls, question: str) -> Dict[str, Any]:
        """Convenience alias for parse_question."""
        return cls.parse_question(question)


QuestionParser = ResearchQuestionParser
