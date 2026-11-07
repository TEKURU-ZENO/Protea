"""Adaptive step size embedded Runge-Kutta (RKF45) integrator."""

from typing import Callable, List, Tuple
import numpy as np


class AdaptiveRKSolver:
    """Adaptive step-size Runge-Kutta-Fehlberg (RKF45) solver."""

    # Butcher tableau for RKF45
    c = np.array([0, 1/4, 3/8, 12/13, 1, 1/2])
    a = [
        [],
        [1/4],
        [3/32, 9/32],
        [1932/2197, -7200/2197, 7296/2197],
        [439/216, -8, 3680/513, -845/4104],
        [-8/27, 2, -3544/2565, 1859/4104, -11/40]
    ]
    b4 = np.array([25/216, 0, 1408/2565, 2197/4104, -1/5, 0])
    b5 = np.array([16/135, 0, 6656/12825, 28561/56430, -9/50, 2/55])

    @classmethod
    def solve(
        cls,
        fun: Callable[[float, np.ndarray], np.ndarray],
        t_span: Tuple[float, float],
        y0: np.ndarray,
        tol: float = 1e-5,
        h_init: float = 0.01,
        h_min: float = 1e-6,
        h_max: float = 1.0,
    ) -> Tuple[np.ndarray, np.ndarray]:
        t0, tf = t_span
        t = t0
        y = np.copy(y0)

        times = [t]
        states = [np.copy(y)]

        h = h_init

        while t < tf:
            if t + h > tf:
                h = tf - t

            k1 = fun(t, y)
            k2 = fun(t + cls.c[1]*h, y + h*(cls.a[1][0]*k1))
            k3 = fun(t + cls.c[2]*h, y + h*(cls.a[2][0]*k1 + cls.a[2][1]*k2))
            k4 = fun(t + cls.c[3]*h, y + h*(cls.a[3][0]*k1 + cls.a[3][1]*k2 + cls.a[3][2]*k3))
            k5 = fun(t + cls.c[4]*h, y + h*(cls.a[4][0]*k1 + cls.a[4][1]*k2 + cls.a[4][2]*k3 + cls.a[4][3]*k4))
            k6 = fun(t + cls.c[5]*h, y + h*(cls.a[5][0]*k1 + cls.a[5][1]*k2 + cls.a[5][2]*k3 + cls.a[5][3]*k4 + cls.a[5][4]*k5))

            k_mat = np.array([k1, k2, k3, k4, k5, k6])
            y4 = y + h * np.dot(cls.b4, k_mat)
            y5 = y + h * np.dot(cls.b5, k_mat)

            # Local truncation error
            err = np.max(np.abs(y5 - y4))

            if err <= tol or h <= h_min:
                # Accept step
                t = t + h
                y = np.maximum(y5, 0.0)
                times.append(t)
                states.append(np.copy(y))

                # Step size adjustment for next iteration
                factor = 0.84 * (tol / (err + 1e-12))**0.2
                h = np.clip(h * factor, h_min, h_max)
            else:
                # Reject step and decrease h
                factor = 0.84 * (tol / (err + 1e-12))**0.25
                h = max(h_min, h * factor)

        return np.array(times), np.array(states)
