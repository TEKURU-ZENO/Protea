"""
PROTEA AI Scientist - Research Registry
Maintains registry of all active, completed, and archived research investigations.
"""

from typing import Dict, Any, List, Optional
from ai.ai_scientist.schema import ResearchInvestigation


class ResearchRegistry:
    """
    In-memory / persistent registry for scientific investigations.
    """

    def __init__(self):
        self._investigations: Dict[str, ResearchInvestigation] = {}

    def register(self, investigation: ResearchInvestigation) -> None:
        self._investigations[investigation.investigation_id] = investigation

    def get(self, investigation_id: str) -> Optional[ResearchInvestigation]:
        return self._investigations.get(investigation_id)

    def list_all(self) -> List[ResearchInvestigation]:
        return list(self._investigations.values())

    def update_state(self, investigation_id: str, new_state: Any) -> Optional[ResearchInvestigation]:
        inv = self._investigations.get(investigation_id)
        if inv:
            inv.state = new_state
            return inv
        return None
