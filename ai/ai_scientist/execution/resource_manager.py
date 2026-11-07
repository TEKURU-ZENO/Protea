"""Compute budget and concurrent resource limits manager."""

from typing import Any, Dict


class ResourceManager:
    """Enforces computational quotas, wall-clock timeouts, and resource caps."""

    def __init__(self, max_concurrent: int = 4, max_budget_seconds: float = 120.0, max_runtime_minutes: float = None):
        self.max_concurrent = max_concurrent
        self.max_budget_seconds = (max_runtime_minutes * 60.0) if max_runtime_minutes is not None else max_budget_seconds
        self.active_jobs = 0
        self.total_compute_seconds_used = 0.0

    def can_allocate(self, estimated_seconds: float) -> bool:
        """Check if budget and concurrency limits permit new execution."""
        if self.active_jobs >= self.max_concurrent:
            return False
        if self.total_compute_seconds_used + estimated_seconds > self.max_budget_seconds:
            return False
        return True

    def record_usage(self, seconds_used: float) -> None:
        self.total_compute_seconds_used += seconds_used
