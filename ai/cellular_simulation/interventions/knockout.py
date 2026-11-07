"""Gene and protein knockout interventions."""

import copy
from ai.cellular_simulation.schema import SimulationModel, InterventionSpec


class KnockoutIntervention:
    """Applies genetic or protein knockout by nullifying initial concentration and catalytic reactions."""

    @staticmethod
    def apply(model: SimulationModel, spec: InterventionSpec) -> SimulationModel:
        perturbed = copy.deepcopy(model)
        for target in spec.target_entities:
            # 1. Zero initial concentration
            if target in perturbed.species:
                perturbed.species[target].initial_amount = 0.0

            # 2. Inactivate reactions catalyzed by or producing this species
            for rxn in perturbed.reactions:
                if target in rxn.reactants or target in rxn.products:
                    # If knockout strength is 1.0, eliminate rate completely
                    factor = max(0.0, 1.0 - spec.strength)
                    for p in ["k_f", "kcat", "Vmax", "ub"]:
                        if p in rxn.parameters:
                            rxn.parameters[p] *= factor

        return perturbed
