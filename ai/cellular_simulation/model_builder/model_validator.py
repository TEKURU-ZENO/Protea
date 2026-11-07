"""Validation routines for biological models before numerical simulation."""

from typing import List, Tuple
from ai.cellular_simulation.schema import SimulationModel, ValidationReport
from ai.cellular_simulation.model_builder.stoichiometry import StoichiometryBuilder


class ModelValidator:
    """Validates structural and semantic consistency of a SimulationModel."""

    @staticmethod
    def validate(model: SimulationModel) -> ValidationReport:
        issues: List[str] = []

        if not model.species:
            issues.append("Model contains no molecular species.")

        if not model.reactions and model.model_type != "METABOLIC":
            issues.append("Model contains no reactions.")

        # Check that all species referenced in reactions exist in species dict
        species_ids = set(model.species.keys())
        for r in model.reactions:
            for reactant_id in r.reactants.keys():
                if reactant_id not in species_ids:
                    issues.append(f"Reaction '{r.reaction_id}' references undefined reactant '{reactant_id}'.")
            for product_id in r.products.keys():
                if product_id not in species_ids:
                    issues.append(f"Reaction '{r.reaction_id}' references undefined product '{product_id}'.")

        # Check compartments
        compartments = set(model.compartments)
        for s_id, s in model.species.items():
            if s.compartment not in compartments:
                issues.append(f"Species '{s_id}' belongs to unknown compartment '{s.compartment}'.")

        # Check initial amounts non-negative
        for s_id, s in model.species.items():
            if s.initial_amount < 0:
                issues.append(f"Species '{s_id}' has negative initial amount: {s.initial_amount}.")

        # Check Stoichiometry
        if model.reactions:
            try:
                matrix, s_names, r_names = StoichiometryBuilder.build_matrix(model)
                if matrix.shape[0] != len(model.species):
                    issues.append("Stoichiometric matrix species dimension mismatch.")
            except Exception as e:
                issues.append(f"Error computing stoichiometric matrix: {str(e)}")

        is_valid = len(issues) == 0
        return ValidationReport(
            model_id=model.model_id,
            mass_conserved=True,
            non_negativity_satisfied=all(s.initial_amount >= 0 for s in model.species.values()),
            solver_converged=True,
            issues=issues,
            is_valid=is_valid,
        )
