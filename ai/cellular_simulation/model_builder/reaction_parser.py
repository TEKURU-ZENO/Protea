"""Reaction rate law parser and velocity calculator."""

from __future__ import annotations

import math
from typing import Dict, List
from ai.cellular_simulation.schema import RateLawType, Reaction


class ReactionParser:
    """Evaluates reaction fluxes v_j given species concentrations and rate parameters."""

    @staticmethod
    def evaluate_rate(reaction: Reaction, concentrations: Dict[str, float]) -> float:
        """Computes instantaneous reaction velocity v_j."""
        p = reaction.parameters
        rl_type = reaction.rate_law_type

        if rl_type == RateLawType.MASS_ACTION.value:
            # v = k_f * prod([Reactants]^coeff) - (k_r * prod([Products]^coeff) if reversible)
            k_f = p.get("k_f", p.get("k", 1.0))
            forward_rate = k_f
            for r_id, coeff in reaction.reactants.items():
                conc = max(0.0, concentrations.get(r_id, 0.0))
                forward_rate *= (conc ** coeff)

            reverse_rate = 0.0
            if reaction.reversible:
                k_r = p.get("k_r", 0.0)
                reverse_rate = k_r
                for p_id, coeff in reaction.products.items():
                    conc = max(0.0, concentrations.get(p_id, 0.0))
                    reverse_rate *= (conc ** coeff)

            return forward_rate - reverse_rate

        elif rl_type == RateLawType.MICHAELIS_MENTEN.value:
            # v = (Vmax * [S]) / (Km + [S])
            v_max = p.get("Vmax", 1.0)
            km = p.get("Km", 1.0)
            substrate_id = next(iter(reaction.reactants.keys()), "")
            s = max(0.0, concentrations.get(substrate_id, 0.0))
            return (v_max * s) / (km + s) if (km + s) > 0 else 0.0

        elif rl_type == RateLawType.HILL_ACTIVATION.value:
            # v = (Vmax * [A]^n) / (Ka^n + [A]^n)
            v_max = p.get("Vmax", 1.0)
            ka = p.get("Ka", p.get("Km", 1.0))
            n = p.get("n", 2.0)
            activator_id = next(iter(reaction.reactants.keys()), "")
            a = max(0.0, concentrations.get(activator_id, 0.0))
            a_n = a ** n
            ka_n = ka ** n
            return (v_max * a_n) / (ka_n + a_n) if (ka_n + a_n) > 0 else 0.0

        elif rl_type == RateLawType.HILL_INHIBITION.value:
            # v = Vmax / (1 + ([I] / Ki)^n)
            v_max = p.get("Vmax", 1.0)
            ki = p.get("Ki", 1.0)
            n = p.get("n", 2.0)
            inhibitor_id = p.get("inhibitor_id", next(iter(reaction.reactants.keys()), ""))
            inhib = max(0.0, concentrations.get(inhibitor_id, 0.0))
            return v_max / (1.0 + (inhib / ki) ** n) if ki > 0 else 0.0

        elif rl_type == RateLawType.ZERO_ORDER.value:
            return p.get("k0", p.get("v", 1.0))

        # Default fallback: linear mass action
        return p.get("k", 1.0) * sum(concentrations.get(r, 0.0) for r in reaction.reactants)


ReactionRateEvaluator = ReactionParser

