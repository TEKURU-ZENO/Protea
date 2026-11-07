"""Computational experiment planner translating hypotheses into executable protocols."""

import uuid
from typing import Any, Dict, List, Optional
from ai.ai_scientist.schema import ResearchHypothesis, ExperimentPlan


class ControlsContainer(dict):
    """Container allowing both attribute and dictionary access for experiment controls."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__dict__ = self


class ExperimentPlanner:
    """Translates biological hypotheses into structured in-silico experimental protocols."""

    @classmethod
    def plan_experiment(
        cls,
        hypothesis: Any,
        target_entities: Optional[List[str]] = None,
        computational_engine: str = "CellularSimulationEngine",
    ) -> ExperimentPlan:
        """Create fully specified experiment plan with controls and statistical design."""
        if hasattr(hypothesis, "experimental_plan"):
            plan_meta = hypothesis.experimental_plan
            hyp_id = hypothesis.hypothesis_id
        elif isinstance(hypothesis, dict):
            plan_meta = hypothesis.get("experimental_plan", {})
            hyp_id = hypothesis.get("hypothesis_id", "HYP_01")
        else:
            plan_meta = {}
            hyp_id = "HYP_01"

        entities = target_entities or plan_meta.get("target_entities", ["EGFR", "STAT3"])

        controls_data = {
            "negative_control": "Untreated wild-type baseline (0% inhibition)",
            "negative_controls": ["Untreated wild-type baseline (0% inhibition)", "Scrambled shRNA"],
            "positive_control": "100% loss-of-function total knockout",
            "positive_controls": ["100% loss-of-function total knockout", "Staurosporine / Pan-inhibitor"],
            "vehicle": "DMSO vehicle control",
            "vehicle_control": "DMSO vehicle control",
            "orthogonal_controls": ["Phospho-specific Western blot assay", "Mass spectrometry"],
            "statistical_distinction_note": (
                "Replicate simulations represent stochastic numerical solver runs designed to assess parameter "
                "stability, and must never be conflated with independent biological specimens."
            ),
        }
        controls = ControlsContainer(controls_data)

        target_engine = "CSE" if "cell" in computational_engine.lower() else "IPE"

        return ExperimentPlan(
            experiment_id=f"EXP-{uuid.uuid4().hex[:6].upper()}",
            hypothesis_id=hyp_id,
            target_engine=target_engine,
            model_id=plan_meta.get("model_id", "mapk_erk_cascade"),
            intervention_type=plan_meta.get("intervention_type", "INHIBITION"),
            target_entities=entities,
            treatment_levels=plan_meta.get("treatment_levels", [0.0, 0.2, 0.5, 0.8, 1.0]),
            controls=controls,
            outcome_observables=plan_meta.get("outcome_observables", [f"{entities[0]}_star", f"{entities[-1]}_star"]),
            replicates=8,
            replicate_count=8,
            statistical_plan={
                "test": "two_sample_t_test",
                "alpha": 0.05,
                "fdr_method": "benjamini_hochberg",
                "effect_size_metric": "cohen_d",
                "minimum_detectable_effect": 0.35,
            },
            is_approved=False,
            requires_human_approval=False,
            simulation_parameters={"duration": 100.0, "step_size": 0.1},
        )
