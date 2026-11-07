"""
PROTEA API - Biological Reasoning Service Layer
Coordinates BRE orchestration, evidence fusion, mechanism reconstruction, and job tracking.
"""

from typing import List, Dict, Optional, Any
import uuid
import time
import logging

from ai.biological_reasoning.schema import (
    BiologicalQuestion,
    ReasoningReport,
    BiologicalEvidence,
    PerturbationScenario
)
from ai.biological_reasoning.query.parser import BiologicalQuestionParser, BiologicalQueryPlanner
from ai.biological_reasoning.retrieval.hybrid_retriever import HybridEvidenceRetriever
from ai.biological_reasoning.mechanistic.mechanism_reconstructor import MechanisticReasoningEngine
from ai.biological_reasoning.hypothesis.generator import HypothesisGenerationEngine, HypothesisRankingEngine
from ai.biological_reasoning.evidence.fusion import EvidenceFusionEngine
from ai.biological_reasoning.counterfactual.scenario_comparison import CounterfactualReasoningEngine
from ai.biological_reasoning.validation.biological_constraints import BiologicalConstraintValidator
from ai.biological_reasoning.agents.orchestrator import orchestrator

logger = logging.getLogger("services.api.biological_reasoning_service")

class BiologicalReasoningService:
    """Service coordinator for biological reasoning requests and jobs."""

    def __init__(self):
        self.parser = BiologicalQuestionParser()
        self.planner = BiologicalQueryPlanner()
        self.retriever = HybridEvidenceRetriever()
        self.mechanistic = MechanisticReasoningEngine(self.retriever)
        self.hypotheses = HypothesisGenerationEngine(self.mechanistic)
        self.ranker = HypothesisRankingEngine()
        self.fusion = EvidenceFusionEngine()
        self.counterfactual = CounterfactualReasoningEngine()
        self.validator = BiologicalConstraintValidator()
        self.orchestrator = orchestrator

        # In-memory storage for jobs and reports
        self._jobs: Dict[str, Dict[str, Any]] = {}
        self._results: Dict[str, ReasoningReport] = {}

    def execute_reasoning_query(self, raw_query: str) -> ReasoningReport:
        """Parse natural language question and execute full multi-agent reasoning."""
        question = self.parser.parse(raw_query)
        report = self.orchestrator.run_reasoning_pipeline(question)
        self._results[report.report_id] = report
        return report

    def reconstruct_mechanism(self, chain: List[str]) -> Dict[str, Any]:
        mech = self.mechanistic.reconstruct_mechanism(chain)
        return mech.model_dump()

    def identify_regulators(self, target: str, observation: str = "downregulated") -> List[Dict[str, Any]]:
        return self.mechanistic.identify_upstream_regulators(target, observed_change=observation)

    def generate_hypotheses(self, raw_query: str, max_count: int = 3) -> List[Dict[str, Any]]:
        question = self.parser.parse(raw_query)
        hyps = self.hypotheses.generate_competing_hypotheses(question, max_hypotheses=max_count)
        return [h.model_dump() for h in hyps]

    def rank_hypotheses(self, raw_query: str) -> List[Dict[str, Any]]:
        question = self.parser.parse(raw_query)
        hyps = self.hypotheses.generate_competing_hypotheses(question, max_hypotheses=3)
        return self.ranker.rank_hypotheses(hyps)

    def fuse_evidence(self, target: str) -> Dict[str, Any]:
        evs = self.retriever.retrieve_evidence_for_target(target)
        return self.fusion.fuse_evidence(evs)

    def simulate_counterfactual(self, target: str, perturbation_type: str = "knockout", tissue: Optional[str] = None) -> Dict[str, Any]:
        scenario = self.counterfactual.simulate_perturbation(target, perturbation_type=perturbation_type, tissue=tissue)
        return scenario.model_dump()

    def validate_mechanism(self, chain: List[str]) -> Dict[str, Any]:
        mech = self.mechanistic.reconstruct_mechanism(chain)
        return self.validator.validate_mechanism(mech)

    def get_result(self, result_id: str) -> Optional[ReasoningReport]:
        return self._results.get(result_id)

    def get_models(self) -> Dict[str, Any]:
        return {
            "orchestrator": "MultiAgentReasoningOrchestrator v1.0",
            "reasoners": ["MechanisticReasoningEngine", "BiologicalGraphReasoningEngine", "CounterfactualReasoningEngine"],
            "agents": ["RetrievalAgent", "MechanismAgent", "HypothesisAgent", "ValidationAgent", "CriticAgent", "ReportAgent"],
            "evidence_sources": ["IntAct", "BioGRID", "Reactome", "STRING", "PubMed", "GEO", "LINCS"]
        }

biological_reasoning_service = BiologicalReasoningService()
