"""Intervention experiment manager and in-silico perturbation comparator."""

import copy
from typing import Any, Dict, List, Optional, Tuple
import numpy as np

from ai.cellular_simulation.schema import SimulationModel, SimulationResult, InterventionSpec, InterventionType
from ai.cellular_simulation.deterministic.ode_engine import ODEDynamicsEngine
from ai.cellular_simulation.interventions.knockout import KnockoutIntervention
from ai.cellular_simulation.interventions.inhibition import ChemicalInhibitionIntervention
from ai.cellular_simulation.interventions.overexpression import OverexpressionIntervention


class InSilicoInterventionManager:
    """Manages perturbation application and computes delta comparisons with wild-type."""

    def __init__(self, model: SimulationModel):
        self.wild_type_model = model

    def apply_intervention(self, spec: InterventionSpec) -> SimulationModel:
        """Apply intervention specification to produce a perturbed SimulationModel."""
        t_type = spec.intervention_type.upper()
        if t_type in [InterventionType.KNOCKOUT.value, InterventionType.KNOCKDOWN.value]:
            return KnockoutIntervention.apply(self.wild_type_model, spec)
        elif t_type in [InterventionType.INHIBITION.value, "DRUG_INHIBITION"]:
            return ChemicalInhibitionIntervention.apply(self.wild_type_model, spec)
        elif t_type == InterventionType.OVEREXPRESSION.value:
            return OverexpressionIntervention.apply(self.wild_type_model, spec)
        else:
            # Custom parameter modifications
            perturbed = copy.deepcopy(self.wild_type_model)
            for p, v in spec.parameters_modified.items():
                if p in perturbed.parameters:
                    perturbed.parameters[p].value = v
            return perturbed

    def run_comparative_experiment(
        self,
        spec: InterventionSpec,
        t_span: Tuple[float, float] = (0.0, 50.0),
        dt: float = 0.2,
    ) -> Dict[str, Any]:
        """Simulate wild-type and perturbed systems, returning comparative trajectories and delta metrics."""
        # 1. Simulate wild-type
        wt_engine = ODEDynamicsEngine(self.wild_type_model)
        wt_res = wt_engine.simulate(t_span=t_span, dt=dt, solver="LSODA")

        # 2. Simulate perturbed
        perturbed_model = self.apply_intervention(spec)
        pert_engine = ODEDynamicsEngine(perturbed_model)
        pert_res = pert_engine.simulate(t_span=t_span, dt=dt, solver="LSODA")

        # 3. Calculate deltas for each species
        deltas = {}
        for s_id in self.wild_type_model.species.keys():
            wt_series = wt_res.trajectory.species_trajectories[s_id]
            pert_series = pert_res.trajectory.species_trajectories[s_id]

            final_wt = wt_series[-1]
            final_pert = pert_series[-1]
            diff = final_pert - final_wt
            fold_change = (final_pert / max(1e-9, final_wt)) if final_wt > 0 else 0.0

            deltas[s_id] = {
                "wild_type_final": final_wt,
                "perturbed_final": final_pert,
                "delta": diff,
                "fold_change": fold_change,
            }

        return {
            "intervention_spec": spec.to_dict(),
            "wild_type_result": wt_res.to_dict(),
            "perturbed_result": pert_res.to_dict(),
            "species_deltas": deltas,
        }
