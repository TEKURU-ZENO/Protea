"""Fourth-Order Runge-Kutta (RK4) numerical integrator."""

from typing import Callable, List, Tuple
import numpy as np


class RK4Integrator:
    """Fixed-step 4th-order Runge-Kutta solver for differential equations."""

    @staticmethod
    def solve(
        fun: Callable[[float, np.ndarray], np.ndarray],
        t_span: Tuple[float, float],
        y0: np.ndarray,
        dt: float = 0.05,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Integrate system of ODEs from t_span[0] to t_span[1] with step dt.
        
        Returns:
            times: 1D array of time points
            states: 2D array of states (len(times), len(y0))
        """
        t0, tf = t_span
        if tf <= t0:
            return np.array([t0]), np.array([y0])

        num_steps = int(np.ceil((tf - t0) / dt))
        dt = (tf - t0) / num_steps

        times = np.linspace(t0, tf, num_steps + 1)
        states = np.zeros((num_steps + 1, len(y0)), dtype=float)
        states[0] = y0

        curr_y = np.copy(y0)
        for i in range(num_steps):
            t = times[i]
            k1 = fun(t, curr_y)
            k2 = fun(t + 0.5 * dt, curr_y + 0.5 * dt * k1)
            k3 = fun(t + 0.5 * dt, curr_y + 0.5 * dt * k2)
            k4 = fun(t + dt, curr_y + dt * k3)

            next_y = curr_y + (dt / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)
            # Clip negative numerical noise while respecting non-negativity constraint
            next_y = np.maximum(next_y, 0.0)

            states[i + 1] = next_y
            curr_y = next_y

        return times, states
