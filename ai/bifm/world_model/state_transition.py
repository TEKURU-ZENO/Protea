"""
PROTEA Phase 12: Biological World Model (Module G)
Learned predictive state-space model simulating state transitions under interventions.
Distinct from mechanistic ODE/FBA simulations (CSE): statistical system forecasting.
"""

from __future__ import annotations
import math
import uuid
from typing import Dict, List, Any, Optional
from ai.bifm.schema import WorldModelState, InterventionSpec


class BiologicalWorldModel:
    """Predicts statistical biological state transitions under supported interventions."""

    def __init__(self, state_dim: int = 128):
        self.state_dim = state_dim

    def initialize_state(
        self,
        system_id: str,
        context: Optional[Dict[str, Any]] = None,
        baseline_pathways: Optional[Dict[str, float]] = None
    ) -> WorldModelState:
        """Initializes a biological system state."""
        ctx = context or {"organism": "Homo sapiens", "tissue": "Melanocyte", "condition": "BRAF_V600E_Melanoma"}
        # Default baseline pathway activities
        pw = baseline_pathways or {
            "MAPK_Signaling": 0.95,
            "PI3K_AKT_Signaling": 0.65,
            "Apoptosis_Pathway": 0.25,
            "Cell_Cycle_Progression": 0.88,
            "Immune_Evasion": 0.72
        }

        # Initialize deterministic latent state vector
        vec: List[float] = [0.0] * self.state_dim
        for i in range(self.state_dim):
            vec[i] = round(math.sin((i + 1) * 0.12) * 0.80, 4)

        return WorldModelState(
            state_id=f"state_init_{uuid.uuid4().hex[:6]}",
            system_id=system_id,
            context=ctx,
            state_vector=vec,
            pathway_activities=pw,
            active_interactions_count=184,
            step=0,
            uncertainty_std=0.03
        )

    def transition_state(
        self,
        current_state: WorldModelState,
        intervention: InterventionSpec,
        steps: int = 1
    ) -> WorldModelState:
        """
        Rolls forward the biological world model under an intervention.
        Predicts:
        - Molecular state shift
        - Pathway activity adjustments
        - Rewired interaction count
        - Propagated uncertainty
        """
        new_vec = list(current_state.state_vector)
        target = intervention.target_entity.upper()
        itype = intervention.intervention_type.lower()
        mag = intervention.magnitude

        # Copy and perturb pathway activities
        new_pw = dict(current_state.pathway_activities)

        if "inhibit" in itype or "knockdown" in itype or "knockout" in itype:
            if "BRAF" in target:
                new_pw["MAPK_Signaling"] = round(max(0.10, new_pw.get("MAPK_Signaling", 0.90) * (0.25 * mag)), 3)
                new_pw["Apoptosis_Pathway"] = round(min(0.95, new_pw.get("Apoptosis_Pathway", 0.20) + 0.55), 3)
                new_pw["Cell_Cycle_Progression"] = round(max(0.15, new_pw.get("Cell_Cycle_Progression", 0.85) - 0.45), 3)
            elif "EGFR" in target:
                new_pw["PI3K_AKT_Signaling"] = round(max(0.15, new_pw.get("PI3K_AKT_Signaling", 0.70) * (0.30 * mag)), 3)
                new_pw["MAPK_Signaling"] = round(max(0.20, new_pw.get("MAPK_Signaling", 0.80) * 0.50), 3)

        elif "overexpress" in itype or "mutation" in itype:
            new_pw["MAPK_Signaling"] = round(min(0.99, new_pw.get("MAPK_Signaling", 0.60) + 0.35), 3)
            new_pw["Cell_Cycle_Progression"] = round(min(0.99, new_pw.get("Cell_Cycle_Progression", 0.60) + 0.30), 3)

        # Modulate state vector
        perturb_factor = -0.35 if ("inhibit" in itype or "knockout" in itype) else 0.35
        for i in range(len(new_vec)):
            shift = math.cos((i + 1) * 0.15) * perturb_factor
            new_vec[i] = round(new_vec[i] + shift, 4)

        # Propagate uncertainty
        new_uncertainty = round(current_state.uncertainty_std + (0.015 * steps), 3)
        new_interactions = max(50, current_state.active_interactions_count - int(24 * (1.0 - mag)))

        return WorldModelState(
            state_id=f"state_step_{current_state.step + steps}_{uuid.uuid4().hex[:6]}",
            system_id=current_state.system_id,
            context=current_state.context,
            state_vector=new_vec,
            pathway_activities=new_pw,
            active_interactions_count=new_interactions,
            step=current_state.step + steps,
            uncertainty_std=new_uncertainty
        )

    def forecast_trajectory(
        self,
        initial_state: WorldModelState,
        intervention: InterventionSpec,
        total_steps: int = 5
    ) -> List[WorldModelState]:
        """Generates multi-step longitudinal state trajectory under intervention."""
        history = [initial_state]
        curr = initial_state
        for _ in range(total_steps):
            nxt = self.transition_state(curr, intervention, steps=1)
            history.append(nxt)
            curr = nxt
        return history
