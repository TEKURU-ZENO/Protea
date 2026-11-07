"""
PROTEA AI Scientist - Unresolved Research Questions Tracker
Curates open research questions and gaps uncovered during investigations.
"""

from typing import Dict, Any, List
import time
import uuid


class UnresolvedQuestionsTracker:
    """
    Curates a backlog of open biological questions for subsequent iterative discovery cycles.
    """

    def __init__(self):
        self._questions: List[Dict[str, Any]] = []

    def log_question(
        self,
        investigation_id: str,
        question_text: str,
        origin_gap_id: str,
        priority: str = "MEDIUM",
    ) -> Dict[str, Any]:
        record = {
            "question_id": f"q_{uuid.uuid4().hex[:8]}",
            "investigation_id": investigation_id,
            "question_text": question_text,
            "origin_gap_id": origin_gap_id,
            "priority": priority,
            "resolved": False,
            "timestamp": time.time(),
        }
        self._questions.append(record)
        return record

    def list_unresolved(self) -> List[Dict[str, Any]]:
        return [q for q in self._questions if not q["resolved"]]
