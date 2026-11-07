"""
PROTEA BRE - Evidence Fusion, Reliability & Contradiction Detection
Integrates heterogeneous biological observations, accounts for co-dependent citations, and flags conflicting findings.
"""

from typing import List, Dict, Set, Optional, Any, Tuple
from collections import defaultdict
from ai.biological_reasoning.schema import BiologicalEvidence, EvidenceStatus

SOURCE_RELIABILITY_WEIGHTS = {
    "X-ray": 1.00,
    "Cryo-EM": 1.00,
    "NMR": 0.95,
    "EXP": 0.90,
    "IDA": 0.90,
    "AP-MS": 0.85,
    "Y2H": 0.75,
    "Reactome": 0.88,
    "BioGRID": 0.85,
    "IntAct": 0.88,
    "STRING": 0.65,
    "COMP": 0.50,
    "TEXT": 0.45,
    "IEA": 0.40
}

class EvidenceFusionEngine:
    """Fuses multi-source evidence using source reliability profiles and citation independence."""

    def fuse_evidence(self, evidence_list: List[BiologicalEvidence]) -> Dict[str, Any]:
        """
        Aggregate evidence across sources without blindly multiplying scores.
        Distinguishes:
        1. evidence_strength (independent observations & method rigor)
        2. model_confidence (statistical calibrated score)
        3. biological_certainty (consensus across literature)
        """
        if not evidence_list:
            return {
                "fused_confidence": 0.10,
                "evidence_strength": 0.10,
                "model_confidence": 0.10,
                "biological_certainty": "HYPOTHETICAL",
                "unique_publications": 0,
                "independent_evidence_count": 0
            }

        # Deduplicate shared PubMed IDs to prevent counting recycled data as multiple independent observations
        unique_pmids = set(e.publication_id for e in evidence_list if e.publication_id and "PubMed" in e.publication_id)
        experimental_count = sum(1 for e in evidence_list if e.evidence_status == EvidenceStatus.EXPERIMENTAL)
        computational_count = sum(1 for e in evidence_list if e.evidence_status == EvidenceStatus.COMPUTATIONAL)

        # Weighted score incorporating method hierarchy
        weights = [SOURCE_RELIABILITY_WEIGHTS.get(e.evidence_code or e.source, 0.60) for e in evidence_list]
        max_weight = max(weights) if weights else 0.50
        diminishing_bonus = min(0.20, len(unique_pmids) * 0.05)
        evidence_strength = round(min(1.0, max_weight + diminishing_bonus), 3)

        model_confidence = round(float(sum(e.confidence or 0.70 for e in evidence_list) / len(evidence_list)), 3)

        # Determine biological certainty
        if experimental_count >= 2 and len(unique_pmids) >= 2:
            certainty = "ESTABLISHED"
        elif experimental_count >= 1 or computational_count >= 3:
            certainty = "PROBABLE"
        else:
            certainty = "HYPOTHETICAL"

        return {
            "fused_confidence": round(0.55 * evidence_strength + 0.45 * model_confidence, 3),
            "evidence_strength": evidence_strength,
            "model_confidence": model_confidence,
            "biological_certainty": certainty,
            "unique_publications": len(unique_pmids),
            "independent_evidence_count": len(evidence_list),
            "experimental_evidence_count": experimental_count,
            "computational_evidence_count": computational_count
        }


class ContradictionResolutionEngine:
    """Detects opposing biological statements and context-dependent contradictions."""

    OPPOSING_PREDICATES = {
        "activates": ["inhibits", "downregulates", "represses", "cleaves_inactivates"],
        "inhibits": ["activates", "upregulates", "stimulates", "stabilizes"],
        "phosphorylates": ["dephosphorylates"],
        "dephosphorylates": ["phosphorylates"],
        "ubiquitinates": ["deubiquitinates"],
        "deubiquitinates": ["ubiquitinates"]
    }

    def detect_contradictions(self, evidence_list: List[BiologicalEvidence]) -> List[Dict[str, Any]]:
        """
        Scan evidence pairs between the same subject and object for conflicting regulatory directions.
        """
        pair_map = defaultdict(list)
        for ev in evidence_list:
            key = (ev.subject_id.upper(), ev.object_id.upper())
            pair_map[key].append(ev)

        contradictions = []

        for (u, v), evs in pair_map.items():
            if len(evs) < 2:
                continue

            for i in range(len(evs)):
                for j in range(i + 1, len(evs)):
                    e1, e2 = evs[i], evs[j]
                    p1 = e1.predicate.lower()
                    p2 = e2.predicate.lower()

                    if p1 in self.OPPOSING_PREDICATES and p2 in self.OPPOSING_PREDICATES[p1]:
                        contradictions.append({
                            "subject": u,
                            "object": v,
                            "claim_1": f"{u} {p1} {v} [{e1.source}, {e1.publication_id}]",
                            "claim_2": f"{u} {p2} {v} [{e2.source}, {e2.publication_id}]",
                            "severity": "HIGH",
                            "resolution_strategy": "Evaluate tissue context, cell-type specificity, or phosphorylation site dependence."
                        })

        return contradictions
