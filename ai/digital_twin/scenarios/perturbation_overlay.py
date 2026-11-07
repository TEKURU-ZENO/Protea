"""Perturbation Overlay Engine computing signed propagation through interactome networks."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional
from ai.digital_twin.schema import (
    InteractomeSnapshot,
    InterventionType,
    MolecularState,
    NetworkEdgeEvidence,
    ScenarioResult,
    StateStatus,
)

logger = logging.getLogger(__name__)


class PerturbationOverlayEngine:
    """Propagates in silico interventions through signed regulatory and physical edges."""

    def __init__(self, decay_factor: float = 0.80, max_depth: int = 3):
        self.decay_factor = decay_factor
        self.max_depth = max_depth

    def simulate_intervention(
        self,
        scenario_id: str,
        parent_version_id: str,
        baseline_states: Dict[str, MolecularState],
        snapshot: InteractomeSnapshot,
        intervention_type: str,
        target_entities: List[str],
        strength: float = 1.0
    ) -> ScenarioResult:
        """Simulates intervention propagation without modifying original baseline states."""
        # Clone states and tag as SIMULATED
        sim_states: Dict[str, MolecularState] = {}
        for k, v in baseline_states.items():
            st_dict = v.to_dict()
            sim_states[k] = MolecularState(**st_dict)

        # Build adjacency with signs
        adj: Dict[str, List[tuple[str, int, float]]] = {n: [] for n in sim_states}
        for e in snapshot.edges:
            sign = e.sign if e.sign is not None else 1
            if e.source in adj and e.target in adj:
                adj[e.source].append((e.target, sign, e.confidence))

        # Initial perturbation vector on targets
        # e.g., KNOCKOUT: -1.0, OVEREXPRESSION: +1.0, KNOCKDOWN: -0.5
        initial_deltas: Dict[str, float] = {}
        for t in target_entities:
            if intervention_type == InterventionType.KNOCKOUT.value:
                initial_deltas[t] = -1.0 * strength
            elif intervention_type == InterventionType.KNOCKDOWN.value:
                initial_deltas[t] = -0.5 * strength
            elif intervention_type == InterventionType.OVEREXPRESSION.value:
                initial_deltas[t] = 1.0 * strength
            elif intervention_type == InterventionType.INHIBITION.value:
                initial_deltas[t] = -0.85 * strength
            elif intervention_type == InterventionType.ACTIVATION.value:
                initial_deltas[t] = 0.85 * strength
            else:
                initial_deltas[t] = -0.5 * strength

        # Breadth-first propagation
        propagated_deltas: Dict[str, float] = dict(initial_deltas)
        current_layer = list(initial_deltas.keys())

        for depth in range(1, self.max_depth + 1):
            next_layer: List[str] = []
            layer_decay = self.decay_factor ** depth

            for node in current_layer:
                parent_delta = propagated_deltas[node]
                for nxt, edge_sign, conf in adj.get(node, []):
                    signal = parent_delta * edge_sign * conf * layer_decay
                    if nxt not in propagated_deltas or abs(signal) > abs(propagated_deltas[nxt]):
                        propagated_deltas[nxt] = round(signal, 3)
                        next_layer.append(nxt)

            current_layer = list(set(next_layer))

        # Apply deltas to simulated states
        for node, delta in propagated_deltas.items():
            if node in sim_states:
                st = sim_states[node]
                st.status = StateStatus.SIMULATED.value
                # Shift expression and protein abundance
                if st.gene_expression is not None:
                    st.gene_expression = round(max(0.0, st.gene_expression + delta * 2.0), 2)
                if st.protein_abundance is not None:
                    st.protein_abundance = round(max(0.0, st.protein_abundance + delta * 2.0), 2)
                if st.protein_activity is not None:
                    st.protein_activity = round(max(-1.0, min(1.0, st.protein_activity + delta)), 2)

        # Estimate pathway shifts
        pathway_shifts = {
            "Apoptosis": round(propagated_deltas.get("BAX", 0.0) * 0.8, 3),
            "Cell Cycle Checkpoints": round(propagated_deltas.get("TP53", 0.0) * 0.7, 3),
            "Insulin / AKT Survival": round(propagated_deltas.get("AKT1", 0.0) * 0.9, 3),
            "Drug Metabolism / Cytochromes": round(propagated_deltas.get("CYP3A4", 0.0) * 0.85, 3)
        }

        return ScenarioResult(
            scenario_id=scenario_id,
            parent_version_id=parent_version_id,
            target_entities=target_entities,
            intervention_type=intervention_type,
            perturbation_strength=strength,
            perturbed_states=sim_states,
            pathway_shifts=pathway_shifts,
            rewired_edges=[],
            assumptions=[
                "Linear signal attenuation with 0.80 decay per interactome hop.",
                "Target nodes subjected to instant steady-state intervention.",
                "Homeostatic baseline assumption: no feedback transcription reconfiguration modeled."
            ],
            uncertainty_score=round(0.05 + 0.02 * len(propagated_deltas), 3)
        )
