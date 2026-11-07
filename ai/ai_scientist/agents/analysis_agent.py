"""
PROTEA AI Scientist - Statistical Analysis Agent
Performs statistical hypothesis testing, effect size estimation, and time-series dynamics.
"""

from typing import Dict, Any, List
from ai.ai_scientist.analysis.statistical_analysis import StatisticalAnalyzer
from ai.ai_scientist.analysis.effect_sizes import EffectSizeCalculator
from ai.ai_scientist.analysis.time_series import TimeSeriesAnalyzer
from ai.ai_scientist.analysis.robustness import RobustnessAnalyzer
from ai.ai_scientist.schema import StatisticalAnalysisReport


class AnalysisAgent:
    """
    Executes rigorous statistical evaluation of computational experiment outputs.
    """

    def __init__(self):
        self.stat_analyzer = StatisticalAnalyzer()
        self.effect_calc = EffectSizeCalculator()
        self.time_analyzer = TimeSeriesAnalyzer()
        self.robustness_analyzer = RobustnessAnalyzer()

    def run(
        self,
        experiment_id: str,
        hypothesis_id: str,
        intervention_replicates: List[float],
        control_replicates: List[float],
    ) -> Dict[str, Any]:
        """
        Runs comprehensive statistical evaluation across replicates.
        """
        stat_report = self.stat_analyzer.evaluate_significance(
            experiment_id=experiment_id,
            hypothesis_id=hypothesis_id,
            intervention_replicates=intervention_replicates,
            control_replicates=control_replicates,
        )

        fold_change = self.effect_calc.fold_change(
            intervention_mean=stat_report.metric_means.get("intervention", 0.0),
            control_mean=stat_report.metric_means.get("control", 1.0),
        )

        stability = self.robustness_analyzer.evaluate_perturbation_stability(intervention_replicates)

        return {
            "statistical_report": stat_report.dict() if hasattr(stat_report, "dict") else stat_report,
            "effect_size": stat_report.effect_size,
            "p_value": stat_report.p_value,
            "statistically_significant": stat_report.statistically_significant,
            "fold_change": fold_change,
            "solver_stability": stability,
        }
