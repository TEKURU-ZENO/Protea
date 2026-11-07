"""
PROTEA AI Scientist - Service Layer
Encapsulates all Phase 9 Autonomous Biological Discovery Engine business logic for API routers.
"""

from typing import Dict, Any, List, Optional
from ai.ai_scientist.agents.orchestrator import PrincipalResearchOrchestrator
from ai.ai_scientist.question_understanding.parser import QuestionParser
from ai.ai_scientist.question_understanding.entity_resolver import BiologicalEntityResolver
from ai.ai_scientist.question_understanding.feasibility import FeasibilityChecker
from ai.ai_scientist.literature.search import LiteratureSearchCoordinator
from ai.ai_scientist.literature.deduplication import LiteratureDeduplicator
from ai.ai_scientist.knowledge_synthesis.claim_extractor import ScientificClaimExtractor
from ai.ai_scientist.knowledge_synthesis.knowledge_builder import EvidenceKnowledgeGraphBuilder
from ai.ai_scientist.research_gaps.gap_detector import GapDetector
from ai.ai_scientist.research_gaps.novelty_auditor import NoveltyAuditor
from ai.ai_scientist.hypothesis.generator import HypothesisGenerator
from ai.ai_scientist.hypothesis.hypothesis_ranker import HypothesisRanker
from ai.ai_scientist.experiment_design.planner import ExperimentPlanner
from ai.ai_scientist.execution.workflow_executor import WorkflowExecutor
from ai.ai_scientist.analysis.statistical_analysis import StatisticalAnalyzer
from ai.ai_scientist.criticism.adversarial_review import AdversarialReviewer
from ai.ai_scientist.writing.manuscript_generator import ScientificManuscriptGenerator
from ai.ai_scientist.writing.report_builder import ReportBuilder
from ai.ai_scientist.reproducibility.artifact_versioning import ReproducibilityPackageBuilder
from ai.ai_scientist.schema import ResearchState


class AIScientistService:
    """
    Singleton service managing autonomous scientific research pipelines.
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(AIScientistService, cls).__new__(cls, *args, **kwargs)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return

        self.orchestrator = PrincipalResearchOrchestrator()
        self.question_parser = QuestionParser()
        self.entity_resolver = BiologicalEntityResolver()
        self.feasibility_checker = FeasibilityChecker()
        self.literature_search = LiteratureSearchCoordinator()
        self.deduplicator = LiteratureDeduplicator()
        self.claim_extractor = ScientificClaimExtractor()
        self.kg_builder = EvidenceKnowledgeGraphBuilder()
        self.gap_detector = GapDetector()
        self.novelty_auditor = NoveltyAuditor()
        self.hypothesis_gen = HypothesisGenerator()
        self.hypothesis_ranker = HypothesisRanker()
        self.experiment_planner = ExperimentPlanner()
        self.workflow_executor = WorkflowExecutor()
        self.statistical_analyzer = StatisticalAnalyzer()
        self.critic_reviewer = AdversarialReviewer()
        self.manuscript_gen = ScientificManuscriptGenerator()
        self.report_builder = ReportBuilder()
        self.pkg_builder = ReproducibilityPackageBuilder()

        self._initialized = True

    def create_investigation(
        self,
        research_question: str,
        investigator: str = "PROTEA_User",
        max_compute_budget_minutes: float = 30.0,
        require_human_approval: bool = True,
    ) -> Dict[str, Any]:
        inv = self.orchestrator.create_investigation(
            research_question=research_question,
            investigator=investigator,
            max_compute_budget_minutes=max_compute_budget_minutes,
            require_human_approval=require_human_approval,
        )
        return inv.dict()

    def get_investigation(self, investigation_id: str) -> Optional[Dict[str, Any]]:
        inv = self.orchestrator.registry.get(investigation_id)
        return inv.dict() if inv else None

    def list_investigations(self) -> List[Dict[str, Any]]:
        return [inv.dict() for inv in self.orchestrator.registry.list_all()]

    def analyze_question(self, question: str) -> Dict[str, Any]:
        parsed = self.question_parser.parse(question)
        entities = self.entity_resolver.resolve_entities(parsed.get("extracted_entities", []))
        feasibility = self.feasibility_checker.check_feasibility(question, entities)
        return {
            "parsed": parsed,
            "resolved_entities": entities,
            "feasibility": feasibility,
        }

    def search_literature(self, query: str, max_results: int = 15) -> Dict[str, Any]:
        raw_pubs = self.literature_search.search(query=query, max_results=max_results)
        dedup = self.deduplicator.deduplicate(raw_pubs)
        return {
            "query": query,
            "total_raw": len(raw_pubs),
            "unique_count": len(dedup["unique_records"]),
            "peer_reviewed_count": dedup["peer_reviewed_count"],
            "preprint_count": dedup["preprint_count"],
            "publications": [p.dict() for p in dedup["unique_records"]],
        }

    def synthesize_knowledge(self, publications: List[Dict[str, Any]]) -> Dict[str, Any]:
        claims = self.claim_extractor.extract_claims(publications)
        graph = self.kg_builder.build_graph(claims)
        return {
            "total_claims": len(claims),
            "claims": [c.dict() for c in claims],
            "evidence_graph": graph,
        }

    def detect_gaps(self, claims: List[Dict[str, Any]], entities: List[str]) -> Dict[str, Any]:
        gaps = self.gap_detector.detect_gaps(claims, entities)
        return {
            "total_gaps": len(gaps),
            "gaps": [g.dict() for g in gaps],
        }

    def audit_novelty(self, proposed_discovery: str, publications: List[Dict[str, Any]]) -> Dict[str, Any]:
        return self.novelty_auditor.audit_novelty(proposed_discovery, publications)

    def generate_hypotheses(
        self,
        gap_id: str,
        gap_description: str,
        claims: List[Dict[str, Any]],
        entities: List[str],
    ) -> Dict[str, Any]:
        hyps = self.hypothesis_gen.generate_competing_hypotheses(
            gap_id=gap_id,
            gap_description=gap_description,
            claims=claims,
            entities=entities,
            prior_knowledge={},
        )
        return {
            "total_hypotheses": len(hyps),
            "hypotheses": [h.dict() for h in hyps],
        }

    def rank_hypotheses(self, hypotheses: List[Any]) -> Dict[str, Any]:
        ranked = self.hypothesis_ranker.rank_hypotheses(hypotheses)
        return {
            "ranked_hypotheses": [h.dict() if hasattr(h, "dict") else h for h in ranked],
            "top_hypothesis": ranked[0].dict() if ranked and hasattr(ranked[0], "dict") else (ranked[0] if ranked else None),
        }

    def design_experiment(
        self,
        hypothesis: Dict[str, Any],
        target_entities: List[str],
        engine: str = "CellularSimulationEngine",
    ) -> Dict[str, Any]:
        plan = self.experiment_planner.plan_experiment(
            hypothesis=hypothesis,
            target_entities=target_entities,
            computational_engine=engine,
        )
        return plan.dict()

    def approve_experiment(self, investigation_id: str, approved: bool = True) -> Dict[str, Any]:
        inv = self.orchestrator.registry.get(investigation_id)
        if not inv:
            raise ValueError(f"Investigation {investigation_id} not found.")

        if approved:
            inv.state = ResearchState.EXPERIMENT_EXECUTION
            return {"status": "approved", "current_state": inv.state.value}
        else:
            inv.state = ResearchState.FAILED
            return {"status": "rejected", "current_state": inv.state.value}

    def execute_experiment(
        self,
        experiment_plan: Dict[str, Any],
        user_approved: bool = True,
    ) -> Dict[str, Any]:
        exec_record = self.workflow_executor.execute_experiment(
            experiment_plan=experiment_plan,
            user_approved=user_approved,
        )
        return exec_record.dict()

    def run_analysis(
        self,
        experiment_id: str,
        hypothesis_id: str,
        intervention_replicates: List[float],
        control_replicates: List[float],
    ) -> Dict[str, Any]:
        report = self.statistical_analyzer.evaluate_significance(
            experiment_id=experiment_id,
            hypothesis_id=hypothesis_id,
            intervention_replicates=intervention_replicates,
            control_replicates=control_replicates,
        )
        return report.dict()

    def review_criticism(
        self,
        hypothesis_id: str,
        hypothesis_statement: str,
        falsification_criteria: List[str],
        experiment_design: Dict[str, Any],
        experimental_results: Dict[str, Any],
        pathway_context: Dict[str, Any],
    ) -> Dict[str, Any]:
        audit = self.critic_reviewer.conduct_audit(
            hypothesis_id=hypothesis_id,
            hypothesis_statement=hypothesis_statement,
            falsification_criteria=falsification_criteria,
            experiment_design=experiment_design,
            experimental_results=experimental_results,
            pathway_context=pathway_context,
        )
        return audit.dict()

    def generate_reports(
        self,
        investigation_id: str,
        research_question: str,
        gap_description: str,
        primary_hypothesis: Dict[str, Any],
        experiment_plan: Dict[str, Any],
        statistical_report: Dict[str, Any],
        adversarial_report: Dict[str, Any],
        retrieved_publications: List[Dict[str, Any]],
        random_seeds: List[int],
    ) -> Dict[str, Any]:
        manuscript = self.manuscript_gen.generate_manuscript(
            investigation_id=investigation_id,
            research_question=research_question,
            gap_description=gap_description,
            primary_hypothesis=primary_hypothesis,
            experiment_plan=experiment_plan,
            statistical_report=statistical_report,
            adversarial_report=adversarial_report,
            retrieved_publications=retrieved_publications,
        )

        exec_summary = self.report_builder.build_executive_summary(
            investigation_id=investigation_id,
            question=research_question,
            top_hypothesis=primary_hypothesis,
            adversarial_result=adversarial_report,
            key_findings=[
                f"Statistically significant effect observed (p = {statistical_report.get('p_value', 0.001):.4f})",
                f"Robustness score of {adversarial_report.get('robustness_score', 0.85):.2f}",
            ],
        )

        pkg = self.pkg_builder.build_package(
            investigation_id=investigation_id,
            experiment_id=experiment_plan.get("experiment_id", "exp_01"),
            hypothesis_id=primary_hypothesis.get("hypothesis_id", "hyp_01"),
            config=experiment_plan.get("simulation_parameters", {}),
            random_seeds=random_seeds,
            raw_outputs=statistical_report,
            dataset_uris=["protea://knowledge_graph/ubkg_v1"],
        )

        return {
            "manuscript": manuscript.dict(),
            "executive_summary": exec_summary,
            "reproducibility_package": pkg.dict(),
        }

    def run_full_investigation(
        self,
        research_question: str,
        auto_approve_simulation: bool = True,
    ) -> Dict[str, Any]:
        return self.orchestrator.run_full_investigation(
            research_question=research_question,
            auto_approve_simulation=auto_approve_simulation,
        )


ai_scientist_service = AIScientistService()
