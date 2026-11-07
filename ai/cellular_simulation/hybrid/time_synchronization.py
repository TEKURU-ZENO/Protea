"""Multiscale time synchronization and adaptive interval coordinator."""

from dataclasses import dataclass
from typing import List, Tuple
import numpy as np


@dataclass
class MultiscaleClock:
    """Synchronizes sub-models advancing at different characteristic timescales."""
    t_start: float = 0.0
    t_end: float = 100.0
    sync_interval: float = 1.0     # Time between submodel synchronization exchanges
    fast_dt: float = 0.05          # Fine time step for fast signaling dynamics
    slow_dt: float = 1.0           # Coarse time step for slow transcriptional dynamics

    def get_sync_windows(self) -> List[Tuple[float, float]]:
        """Generate sequence of [t_k, t_{k+1}] synchronization windows."""
        times = np.arange(self.t_start, self.t_end + self.sync_interval, self.sync_interval)
        windows = []
        for i in range(len(times) - 1):
            windows.append((float(times[i]), float(times[i+1])))
        return windows
