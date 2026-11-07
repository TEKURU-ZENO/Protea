"""Mass conservation and stoichiometric invariant validation."""

from typing import Any, Dict, List, Tuple
import numpy as np

from ai.cellular_simulation.schema import SimulationModel, Trajectory
from ai.cellular_simulation.model_builder.stoichiometry import StoichiometryBuilder


class MassConservationValidator:
    """Verifies that stoichiometric conservation relations L * x(t) = const hold across simulation."""

    @staticmethod
    def verify_conservation(
        model: SimulationModel,
        trajectory: Trajectory,
        tolerance: float = 1e-3,
    ) -> Dict[str, Any]:
        """Check all conservation laws across trajectory."""
        matrix, s_names, _ = StoichiometryBuilder.build_matrix(model)
        L = StoichiometryBuilder.find_conservation_laws(matrix)

        if len(L) == 0:
            return {
                "has_conservation_laws": False,
                "is_conserved": True,
                "conservation_laws_count": 0,
                "max_drift": 0.0,
            }

        species_data = np.array([trajectory.species_trajectories[s] for s in s_names]) # (n_species, n_times)
        max_drift = 0.0
        law_results = []

        for i, row in enumerate(L):
            total_amounts = np.dot(row, species_data) # (n_times,)
            init_val = total_amounts[0]
            drift = np.max(np.abs(total_amounts - init_val))
            max_drift = max(max_drift, float(drift))
            law_results.append({
                "law_index": i,
                "coefficients": {s_names[j]: float(row[j]) for j in range(len(s_names)) if abs(row[j]) > 1e-6},
                "initial_total": float(init_val),
                "max_drift": float(drift),
                "is_conserved": bool(drift <= tolerance),
            })

        is_conserved = bool(max_drift <= tolerance)

        return {
            "has_conservation_laws": True,
            "is_conserved": is_conserved,
            "conservation_laws_count": len(L),
            "max_drift": float(max_drift),
            "details": law_results,
        }
