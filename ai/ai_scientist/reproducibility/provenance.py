"""
PROTEA AI Scientist - Scientific Provenance Tracker
Maintains end-to-end immutable lineage from scientific question to published conclusions.
"""

from typing import Dict, Any, List
import time
import uuid


class ScientificProvenanceTracker:
    """
    Maintains a directed acyclic lineage graph of all transformations and artifacts.
    """

    def __init__(self):
        self.lineage_events: List[Dict[str, Any]] = []

    def record_step(
        self,
        investigation_id: str,
        step_name: str,
        inputs: List[str],
        outputs: List[str],
        agent_role: str,
        metadata: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Records a discrete provenance transformation step.
        """
        event = {
            "event_id": f"prov_{uuid.uuid4().hex[:8]}",
            "investigation_id": investigation_id,
            "step_name": step_name,
            "agent_role": agent_role,
            "inputs": inputs,
            "outputs": outputs,
            "metadata": metadata,
            "timestamp": time.time(),
        }
        self.lineage_events.append(event)
        return event

    def get_lineage(self, investigation_id: str) -> List[Dict[str, Any]]:
        """
        Returns all provenance events for a given investigation in chronological order.
        """
        return [e for e in self.lineage_events if e["investigation_id"] == investigation_id]
