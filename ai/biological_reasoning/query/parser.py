"""
PROTEA BRE - Biological Question Parser & Query Planner
Parses natural language questions into structured queries and generates multi-step reasoning plans.
"""

import re
from typing import Dict, List, Any
from ai.biological_reasoning.schema import BiologicalQuestion
from ai.biological_reasoning.query.entity_resolution import BiologicalEntityResolver

class BiologicalQuestionParser:
    """Translates natural language questions into structured biological tasks."""

    def __init__(self):
        self.resolver = BiologicalEntityResolver()

    def parse(self, raw_query: str) -> BiologicalQuestion:
        clean_text = raw_query.strip()
        context = self.resolver.extract_context(clean_text)

        # Identify target protein by symbol or synonym
        target_protein = "TP53" # Default fallback
        ambiguities = []

        # Find uppercase token or recognized synonym
        tokens = re.findall(r'[A-Za-z0-9_-]+', clean_text)
        for token in tokens:
            resolved, possible_ambiguities = self.resolver.resolve_protein(token)
            if resolved:
                target_protein = resolved
                if possible_ambiguities:
                    ambiguities.append({"token": token, "candidates": possible_ambiguities})
                break

        # Classify task
        text_lower = clean_text.lower()
        if "upstream" in text_lower or "regulator" in text_lower or "what causes" in text_lower:
            task = "upstream_regulator_analysis"
            outputs = ["candidate_regulators", "affected_pathways", "supporting_evidence"]
        elif "downstream" in text_lower or "affect" in text_lower or "consequence" in text_lower:
            task = "downstream_pathway_impact"
            outputs = ["affected_pathways", "downstream_targets", "supporting_evidence"]
        elif "mechanism" in text_lower or "how does" in text_lower or "cascade" in text_lower:
            task = "mechanism_reconstruction"
            outputs = ["molecular_mechanism", "reaction_steps", "supporting_evidence"]
        elif "knockout" in text_lower or "inhibit" in text_lower or "what happens if" in text_lower:
            task = "counterfactual_perturbation"
            outputs = ["perturbed_network", "affected_pathways", "counterfactual_predictions"]
        else:
            task = "competing_hypotheses"
            outputs = ["candidate_hypotheses", "evidence_rankings", "suggested_experiments"]

        return BiologicalQuestion(
            raw_query=clean_text,
            task=task,
            target=target_protein,
            organism=context.get("organism", "Homo sapiens"),
            context=context,
            requested_outputs=outputs,
            ambiguities=ambiguities
        )


class BiologicalQueryPlanner:
    """Generates deterministic, auditable multi-step execution plans."""

    def create_plan(self, question: BiologicalQuestion) -> List[Dict[str, Any]]:
        """Construct sequential steps required to resolve the question."""
        plan = [
            {
                "step_index": 1,
                "stage": "EVIDENCE_RETRIEVAL",
                "action": "retrieve_multimodal_evidence",
                "parameters": {
                    "target": question.target,
                    "tissue": question.context.get("tissue"),
                    "organism": question.organism
                }
            },
            {
                "step_index": 2,
                "stage": "MECHANISTIC_REASONING",
                "action": "reconstruct_molecular_mechanisms",
                "parameters": {
                    "task": question.task,
                    "target": question.target,
                    "observation": question.context.get("observation")
                }
            },
            {
                "step_index": 3,
                "stage": "HYPOTHESIS_GENERATION",
                "action": "generate_competing_hypotheses",
                "parameters": {
                    "target": question.target,
                    "max_hypotheses": 3
                }
            },
            {
                "step_index": 4,
                "stage": "VALIDATION_AND_CRITIQUE",
                "action": "validate_biological_constraints",
                "parameters": {
                    "organism": question.organism,
                    "tissue": question.context.get("tissue")
                }
            },
            {
                "step_index": 5,
                "stage": "SCIENTIFIC_SYNTHESIS",
                "action": "generate_evidence_backed_report",
                "parameters": {
                    "question_id": question.question_id
                }
            }
        ]
        return plan
