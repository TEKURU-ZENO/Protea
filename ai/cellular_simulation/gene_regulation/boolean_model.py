"""Boolean network dynamics and attractor discovery for Gene Regulatory Networks."""

from typing import Callable, Dict, List, Set, Tuple
import numpy as np


class BooleanNetwork:
    """Boolean Gene Regulatory Network with synchronous and asynchronous state transitions."""

    def __init__(self, node_names: List[str], rules: Dict[str, Callable[[Dict[str, int]], int]]):
        self.node_names = node_names
        self.rules = rules

    def step_synchronous(self, state: Dict[str, int]) -> Dict[str, int]:
        """Update all gene nodes simultaneously."""
        next_state = {}
        for node in self.node_names:
            rule_fn = self.rules.get(node, lambda s: s.get(node, 0))
            next_state[node] = int(rule_fn(state))
        return next_state

    def step_asynchronous(self, state: Dict[str, int], rng: np.random.RandomState) -> Dict[str, int]:
        """Update a single randomly selected gene node."""
        next_state = dict(state)
        chosen_node = rng.choice(self.node_names)
        rule_fn = self.rules.get(chosen_node, lambda s: s.get(chosen_node, 0))
        next_state[chosen_node] = int(rule_fn(state))
        return next_state

    def simulate(
        self,
        initial_state: Dict[str, int],
        steps: int = 50,
        mode: str = "synchronous",
        seed: int = 42,
    ) -> List[Dict[str, int]]:
        """Simulate Boolean trajectory over discrete time steps."""
        trajectory = [dict(initial_state)]
        curr_state = dict(initial_state)
        rng = np.random.RandomState(seed)

        for _ in range(steps):
            if mode == "asynchronous":
                curr_state = self.step_asynchronous(curr_state, rng)
            else:
                curr_state = self.step_synchronous(curr_state)
            trajectory.append(dict(curr_state))

        return trajectory

    def find_attractors(self, max_iterations: int = 100) -> List[Dict[str, int]]:
        """Find point attractors (fixed-point steady states) by sampling states."""
        attractors: List[Dict[str, int]] = []
        seen_states: Set[Tuple[int, ...]] = set()

        n = len(self.node_names)
        # Sample or enumerate states
        total_possible = 2 ** min(n, 10)
        for i in range(total_possible):
            bin_str = bin(i)[2:].zfill(n)
            state = {name: int(b) for name, b in zip(self.node_names, bin_str)}

            curr = state
            for _ in range(max_iterations):
                nxt = self.step_synchronous(curr)
                if nxt == curr:
                    state_tuple = tuple(nxt[k] for k in self.node_names)
                    if state_tuple not in seen_states:
                        seen_states.add(state_tuple)
                        attractors.append(nxt)
                    break
                curr = nxt

        return attractors
