"""
PROTEA AI Scientist - Hypothesis Agent
Generates competing, falsifiable hypotheses with quantitative predictions and Popperian falsification criteria.
"""

from typing import Dict, Any, List
from ai.ai_scientist.hypothesis.generator import HypothesisGenerator
from ai.ai_scientist.hypothesis.hypothesis_ranker import HypothesisRanker
from ai.ai_scientist.hypothesis.prediction_generator import PredictionGenerator


class HypothesisAgent:
    """
    Formulates and ranks scientific hypotheses against gaps and evidence.
    """

    def __init__(self):
        self.generator = HypothesisGenerator()
        self.ranker = HypothesisRanker()
        self.prediction_gen = PredictionGenerator()

    def run(
        self,
        gap: Any,
        claims: List[Any],
        entities: List[str],
        prior_knowledge: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Executes hypothesis generation, prediction formulation, and ranking.
        """
        gap_id = getattr(gap, "gap_id", "gap_default")
        gap_desc = getattr(gap, "description", str(gap))

        hypotheses = self.generator.generate_competing_hypotheses(
            gap_id=gap_id,
            gap_description=gap_desc,
            claims=claims,
            entities=entities,
            prior_knowledge=prior_knowledge,
        )

        # Generate predictions for each
        for h in hypotheses:
            preds = self.prediction_gen.generate_predictions(h)
            h.predictions.extend(preds)

        ranked = self.ranker.rank_hypotheses(hypotheses)

        return {
            "hypotheses": [h.dict() if hasattr(h, "dict") else h for h in ranked],
            "total_hypotheses": len(ranked),
            "top_hypothesis": ranked[0].dict() if ranked and hasattr(ranked[0], "dict") else (ranked[0] if ranked else None),
        }
