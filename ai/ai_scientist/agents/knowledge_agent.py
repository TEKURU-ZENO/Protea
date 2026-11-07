"""
PROTEA AI Scientist - Knowledge Synthesis Agent
Extracts scientific claims, resolves contradictions, and constructs unified evidence graphs.
"""

from typing import Dict, Any, List
from ai.ai_scientist.knowledge_synthesis.claim_extractor import ScientificClaimExtractor
from ai.ai_scientist.knowledge_synthesis.evidence_linker import EvidenceLinker
from ai.ai_scientist.knowledge_synthesis.contradiction_resolver import ContradictionResolver
from ai.ai_scientist.knowledge_synthesis.knowledge_builder import EvidenceKnowledgeGraphBuilder


class KnowledgeAgent:
    """
    Synthesizes discrete literature into structured, claim-level evidence networks.
    """

    def __init__(self):
        self.claim_extractor = ScientificClaimExtractor()
        self.evidence_linker = EvidenceLinker()
        self.contradiction_resolver = ContradictionResolver()
        self.kg_builder = EvidenceKnowledgeGraphBuilder()

    def run(self, publication_records: List[Any]) -> Dict[str, Any]:
        """
        Executes knowledge extraction and synthesis.
        """
        claims = self.claim_extractor.extract_claims(publication_records)
        grounded_map = self.evidence_linker.link_evidence(claims, publication_records)
        contradiction_report = self.contradiction_resolver.detect_contradictions(claims)
        graph = self.kg_builder.build_graph(claims)

        return {
            "claims": [c.dict() if hasattr(c, "dict") else c for c in claims],
            "total_claims": len(claims),
            "grounded_evidence": grounded_map,
            "contradiction_report": contradiction_report,
            "evidence_graph": graph,
        }
