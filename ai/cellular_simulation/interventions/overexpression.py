"""Target overexpression and gain-of-function interventions."""

import copy
from ai.cellular_simulation.schema import SimulationModel, InterventionSpec


class OverexpressionIntervention:
    """Simulates gain-of-function or ectopic overexpression of target species."""

    @staticmethod
    def apply(model: SimulationModel, spec: InterventionSpec) -> SimulationModel:
        perturbed = copy.deepcopy(model)
        # Strength multiplier: e.g. 2.0 = 2x fold overexpression
        fold = max(1.0, spec.strength)

        for target in spec.target_entities:
            if target in perturbed.species:
                perturbed.species[target].initial_amount *= fold

            # Also increase synthesis reactions for this target if present
            for rxn in perturbed.reactions:
                if target in rxn.products and not rxn.reactants:
                    for p in ["Vmax", "k_f", "alpha_m"]:
                        if p in rxn.parameters:
                            rxn.parameters[p] *= fold

        return perturbed
