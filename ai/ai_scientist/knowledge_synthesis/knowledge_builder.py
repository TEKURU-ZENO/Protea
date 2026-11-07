"""Scientific knowledge synthesizer and evidence graph builder."""

from typing import Any, Dict, List
from ai.ai_scientist.schema import ScientificClaim, PublicationRecord
from ai.ai_scientist.knowledge_synthesis.claim_extractor import ScientificClaimExtractor
from ai.ai_scientist.knowledge_synthesis.evidence_linker import EvidenceLinker
from ai.ai_scientist.knowledge_synthesis.mechanism_extractor import MechanismExtractor
from ai.ai_scientist.knowledge_synthesis.contradiction_resolver import ContradictionResolver


class ScientificKnowledgeBuilder:
    """Assembles structured scientific knowledge from literature publications and claims."""

    @classmethod
    def synthesize_knowledge(
        cls,
        publications: List[PublicationRecord],
        context: Dict[str, str],
    ) -> Dict[str, Any]:
        """Perform end-to-end knowledge synthesis across literature records."""
        claims = ScientificClaimExtractor.extract_claims_from_publications(publications, context)
        linked_evidence = EvidenceLinker.link_claims_to_publications(claims, publications)
        mechanisms = MechanismExtractor.extract_mechanisms(claims)
        contradictions = ContradictionResolver.identify_contradictions(claims)

        return {
            "claims": claims,
            "linked_evidence": linked_evidence,
            "mechanisms": mechanisms,
            "contradictions": contradictions,
            "total_claims": len(claims),
            "publications_analyzed": len(publications),
        }

    @classmethod
    def build_graph(cls, claims: List[Any]) -> Dict[str, Any]:
        """Constructs an evidence graph dictionary from claims."""
        nodes = []
        edges = []
        node_ids = set()

        for c in claims:
            s = getattr(c, "subject", c.get("subject", "ProteinA") if isinstance(c, dict) else "ProteinA")
            o = getattr(c, "object", c.get("object", "ProteinB") if isinstance(c, dict) else "ProteinB")
            p = getattr(c, "predicate", c.get("predicate", "regulates") if isinstance(c, dict) else "regulates")
            cid = getattr(c, "claim_id", c.get("claim_id", "clm_1") if isinstance(c, dict) else "clm_1")

            if s not in node_ids:
                nodes.append({"id": s, "label": s, "type": "Protein"})
                node_ids.add(s)
            if o not in node_ids:
                nodes.append({"id": o, "label": o, "type": "Protein"})
                node_ids.add(o)

            edges.append({
                "source": s,
                "target": o,
                "interaction": p,
                "claim_id": cid,
            })

        return {"nodes": nodes, "edges": edges, "node_count": len(nodes), "edge_count": len(edges)}


EvidenceKnowledgeGraphBuilder = ScientificKnowledgeBuilder

