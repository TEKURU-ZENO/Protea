"""
PROTEA AI Scientist - Confirmed Finding Store
Indexes validated biological findings, effect sizes, and mechanistic links across investigations.
"""

from typing import Dict, Any, List, Optional
import time
import uuid


class FindingStore:
    """
    Stores and retrieves confirmed biological findings with evidence links and uncertainty scores.
    """

    def __init__(self):
        self._findings: Dict[str, Dict[str, Any]] = {}

    def store_finding(
        self,
        investigation_id: str,
        hypothesis_id: str,
        statement: str,
        target_entities: List[str],
        effect_size: float,
        p_value: float,
        confidence: float,
        evidence_sources: List[str],
    ) -> Dict[str, Any]:
        finding_id = f"fnd_{uuid.uuid4().hex[:8]}"
        record = {
            "finding_id": finding_id,
            "investigation_id": investigation_id,
            "hypothesis_id": hypothesis_id,
            "statement": statement,
            "target_entities": target_entities,
            "effect_size": effect_size,
            "p_value": p_value,
            "confidence": confidence,
            "evidence_sources": evidence_sources,
            "timestamp": time.time(),
        }
        self._findings[finding_id] = record
        return record

    def get_findings_for_entity(self, entity_id: str) -> List[Dict[str, Any]]:
        entity_upper = entity_id.upper()
        return [
            f for f in self._findings.values()
            if any(entity_upper in e.upper() for e in f["target_entities"])
        ]

    def list_all(self) -> List[Dict[str, Any]]:
        return list(self._findings.values())
