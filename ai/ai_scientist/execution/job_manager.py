"""Asynchronous research job tracker and queue manager."""

import time
import uuid
from typing import Any, Dict, Optional


class ResearchJobManager:
    """Manages asynchronous discovery runs, execution states, and pollable job tokens."""

    def __init__(self):
        self._jobs: Dict[str, Dict[str, Any]] = {}

    def create_job(self, research_id: str, job_type: str) -> str:
        job_id = f"RSJOB-{uuid.uuid4().hex[:8].upper()}"
        self._jobs[job_id] = {
            "job_id": job_id,
            "research_id": research_id,
            "job_type": job_type,
            "status": "RUNNING",
            "progress_percent": 10.0,
            "created_at": time.time(),
            "completed_at": None,
            "result": None,
            "error": None,
        }
        return job_id

    def update_job_progress(self, job_id: str, progress: float, status: str = "RUNNING") -> None:
        if job_id in self._jobs:
            self._jobs[job_id]["progress_percent"] = min(100.0, max(0.0, progress))
            self._jobs[job_id]["status"] = status

    def complete_job(self, job_id: str, result: Any) -> None:
        if job_id in self._jobs:
            self._jobs[job_id]["status"] = "COMPLETED"
            self._jobs[job_id]["progress_percent"] = 100.0
            self._jobs[job_id]["completed_at"] = time.time()
            self._jobs[job_id]["result"] = result

    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        return self._jobs.get(job_id)
