"""Chemical and targeted small-molecule inhibition interventions."""

import copy
from ai.cellular_simulation.schema import SimulationModel, InterventionSpec


class ChemicalInhibitionIntervention:
    """Simulates chemical inhibitors reducing target enzymatic activity."""

    @staticmethod
    def apply(model: SimulationModel, spec: InterventionSpec) -> SimulationModel:
        perturbed = copy.deepcopy(model)
        # Fraction inhibited = strength in [0, 1]
        inhibition_fraction = max(0.0, min(1.0, spec.strength))
        remaining_activity = 1.0 - inhibition_fraction

        for target in spec.target_entities:
            for rxn in perturbed.reactions:
                # Check if target is involved in reaction name or reactants
                if target in rxn.name or target in rxn.reactants or target == rxn.reaction_id:
                    for param in ["k_f", "kcat", "Vmax", "k_act_raf", "k_act_mek", "k_act_erk"]:
                        if param in rxn.parameters:
                            rxn.parameters[param] *= remaining_activity

        return perturbed
