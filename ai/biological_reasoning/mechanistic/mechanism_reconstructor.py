"""
PROTEA BRE - Mechanistic Reasoning Engine
Reconstructs multi-hop molecular mechanisms, signed regulatory cascades, and upstream/downstream causal chains.
"""

from typing import List, Dict, Set, Optional, Any
from ai.biological_reasoning.schema import (
    MolecularMechanism,
    MolecularMechanismStep,
    RelationshipType,
    EvidenceStatus
)
from ai.biological_reasoning.retrieval.hybrid_retriever import HybridEvidenceRetriever
from ai.biological_reasoning.registry import bre_registry

SIGN_MAP = {
    "activates": 1,
    "phosphorylates": 1,
    "upregulates": 1,
    "transcriptional_activation": 1,
    "cleaves": 1,
    "stabilization": 1,
    "deubiquitinates": 1,
    "inhibits": -1,
    "dephosphorylates": -1,
    "downregulates": -1,
    "ubiquitination": -1,
    "deacetylates": -1,
    "phosphatase_inhibition": -1,
    "complex_formation": 1,
    "direct_binding": 0
}

@bre_registry.register_reasoner("mechanistic")
class MechanisticReasoningEngine:
    """Reconstructs multi-hop molecular chains with signed causal propagation."""

    def __init__(self, retriever: Optional[HybridEvidenceRetriever] = None):
        self.retriever = retriever or HybridEvidenceRetriever()

    def identify_upstream_regulators(
        self,
        target: str,
        observed_change: str = "downregulated",
        max_hops: int = 2
    ) -> List[Dict[str, Any]]:
        """
        Identify upstream candidate regulators that mechanistically explain the observed target state.
        If target is 'downregulated', look for:
        1. Regulators that INHIBIT target and are upregulated/active.
        2. Regulators that ACTIVATE target and are inhibited/inactive.
        """
        target_up = target.upper()
        evidence_list = self.retriever.retrieve_evidence_for_target(target_up)

        candidate_regulators = []

        for ev in evidence_list:
            if ev.object_id == target_up:
                upstream = ev.subject_id
                mech = ev.predicate
                sign = SIGN_MAP.get(mech.lower(), 0)

                # Explanatory logic:
                # Downregulated target explained by:
                # - Inactivator (sign = -1, e.g. MDM2 ubiquitination of TP53)
                # - Loss of activator (sign = +1, e.g. loss of ATM/CHEK2 phosphorylation)
                if observed_change == "downregulated":
                    if sign == -1:
                        explanation = f"Hyperactivation of {upstream} ({mech}) directly suppresses {target_up}."
                        concordance = "Consistent with direct negative regulation"
                    elif sign == 1:
                        explanation = f"Impaired/attenuated {upstream} activity impairs normal {target_up} activation."
                        concordance = "Consistent with loss of positive upstream drive"
                    else:
                        explanation = f"Physical interaction between {upstream} and {target_up}."
                        concordance = "Neutral binding"
                else:
                    if sign == 1:
                        explanation = f"Upregulation of {upstream} directly drives {target_up} activation."
                        concordance = "Consistent with direct activation"
                    else:
                        explanation = f"Loss of {upstream} relieves basal repression on {target_up}."
                        concordance = "Consistent with derepression"

                candidate_regulators.append({
                    "regulator": upstream,
                    "target": target_up,
                    "mechanism": mech,
                    "sign": sign,
                    "evidence_strength": ev.confidence,
                    "evidence_status": ev.evidence_status.value,
                    "source": ev.source,
                    "publication_id": ev.publication_id,
                    "biological_explanation": explanation,
                    "concordance": concordance
                })

        # Rank by evidence strength
        candidate_regulators.sort(key=lambda r: -r["evidence_strength"])
        return candidate_regulators

    def reconstruct_mechanism(self, path: List[str]) -> MolecularMechanism:
        """Evaluate a specific multi-hop sequence of proteins and compute cumulative causality."""
        steps = []
        net_sign = 1
        confidences = []
        compartments = []

        for i in range(len(path) - 1):
            u, v = path[i].upper(), path[i + 1].upper()
            evs = self.retriever.retrieve_evidence_for_target(u)
            matching_ev = next((e for e in evs if (e.subject_id == u and e.object_id == v) or (e.subject_id == v and e.object_id == u)), None)

            if matching_ev:
                mech = matching_ev.predicate
                sign = SIGN_MAP.get(mech.lower(), 1)
                conf = matching_ev.confidence
                ev_status = matching_ev.evidence_status
                ev_ids = [matching_ev.evidence_id]
            else:
                mech = "associates_with"
                sign = 1
                conf = 0.60
                ev_status = EvidenceStatus.COMPUTATIONAL
                ev_ids = []

            net_sign *= sign if sign != 0 else 1
            confidences.append(conf)

            # Check compartments
            u_ctx = self.retriever.get_protein_context(u)
            if u_ctx.get("compartments"):
                compartments.extend(u_ctx["compartments"])

            steps.append(MolecularMechanismStep(
                source=u,
                target=v,
                mechanism=mech,
                relationship_type=RelationshipType.DIRECT_REGULATION if sign != 0 else RelationshipType.PHYSICAL_BINDING,
                sign=sign,
                confidence=conf,
                evidence_status=ev_status,
                evidence_ids=ev_ids
            ))

        effect = "Activation" if net_sign > 0 else ("Inhibition" if net_sign < 0 else "Modulation")
        cum_conf = round(float(min(confidences)) if confidences else 0.70, 3)

        return MolecularMechanism(
            chain=path,
            steps=steps,
            net_effect=effect,
            net_sign=net_sign,
            cumulative_confidence=cum_conf,
            compartments=sorted(list(set(compartments)))
        )
