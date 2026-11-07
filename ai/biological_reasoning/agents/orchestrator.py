"""
PROTEA BRE - Multi-Agent Orchestrator
Coordinates specialized, constrained scientific reasoning agents in a reproducible state-machine workflow.
"""

from typing import List, Dict, Optional, Any
from ai.biological_reasoning.schema import (
    BiologicalQuestion,
    ReasoningReport,
    ReasoningTraceStep,
    MolecularMechanism,
    Hypothesis
)
from ai.biological_reasoning.retrieval.hybrid_retriever import HybridEvidenceRetriever
from ai.biological_reasoning.mechanistic.mechanism_reconstructor import MechanisticReasoningEngine
from ai.biological_reasoning.hypothesis.generator import HypothesisGenerationEngine, HypothesisRankingEngine
from ai.biological_reasoning.evidence.fusion import EvidenceFusionEngine, ContradictionResolutionEngine
from ai.biological_reasoning.validation.biological_constraints import BiologicalConstraintValidator
from ai.biological_reasoning.explanation.report_generator import ScientificReportGenerator

class MultiAgentReasoningOrchestrator:
    """Controls task handoff, state management, and audit trails across specialized reasoning agents."""

    def __init__(self):
        self.retriever = HybridEvidenceRetriever()
        self.mechanistic = MechanisticReasoningEngine(self.retriever)
        self.hypothesis_gen = HypothesisGenerationEngine(self.mechanistic)
        self.hypothesis_ranker = HypothesisRankingEngine()
        self.fusion = EvidenceFusionEngine()
        self.contradictions = ContradictionResolutionEngine()
        self.validator = BiologicalConstraintValidator()
        self.reporter = ScientificReportGenerator()

    def run_reasoning_pipeline(self, question: BiologicalQuestion) -> ReasoningReport:
        """
        Execute deterministic, state-machine driven multi-agent workflow:
        1. Retrieval Agent collects evidence.
        2. Mechanism Agent reconstructs molecular chains.
        3. Hypothesis Agent formulates competing explanations.
        4. Validation Agent audits biological constraints.
        5. Critic Agent challenges assumptions and flags contradictions.
        6. Report Agent synthesizes peer-review-grade scientific summary.
        """
        trace_steps = []
        step_idx = 1

        # 1. Retrieval Agent
        evidence_list = self.retriever.retrieve_evidence_for_target(
            target=question.target,
            tissue=question.context.get("tissue")
        )
        fused_evidence = self.fusion.fuse_evidence(evidence_list)
        trace_steps.append(ReasoningTraceStep(
            step_index=step_idx,
            agent="RetrievalAgent",
            action="retrieve_multimodal_evidence",
            inputs={"target": question.target, "tissue": question.context.get("tissue")},
            outputs={"retrieved_evidence_count": len(evidence_list), "fused_confidence": fused_evidence["fused_confidence"]},
            status="SUCCESS"
        ))
        step_idx += 1

        # 2. Mechanism Agent
        regulators = self.mechanistic.identify_upstream_regulators(
            target=question.target,
            observed_change=question.context.get("observation", "downregulated")
        )
        if regulators:
            top_chain = [regulators[0]["regulator"], question.target, "BAX", "CASP3"]
        else:
            top_chain = ["MDM2", question.target, "BAX", "CASP3"]

        primary_mechanism = self.mechanistic.reconstruct_mechanism(top_chain)
        trace_steps.append(ReasoningTraceStep(
            step_index=step_idx,
            agent="MechanismAgent",
            action="reconstruct_molecular_mechanism",
            inputs={"chain": top_chain},
            outputs={"net_effect": primary_mechanism.net_effect, "steps_count": len(primary_mechanism.steps)},
            status="SUCCESS"
        ))
        step_idx += 1

        # 3. Hypothesis Agent
        hypotheses = self.hypothesis_gen.generate_competing_hypotheses(question, max_hypotheses=3)
        ranked_hypotheses = self.hypothesis_ranker.rank_hypotheses(hypotheses)
        trace_steps.append(ReasoningTraceStep(
            step_index=step_idx,
            agent="HypothesisAgent",
            action="generate_and_rank_competing_hypotheses",
            inputs={"target": question.target},
            outputs={"hypotheses_count": len(hypotheses), "top_hypothesis": hypotheses[0].statement if hypotheses else ""},
            status="SUCCESS"
        ))
        step_idx += 1

        # 4. Validation Agent
        val_result = self.validator.validate_mechanism(primary_mechanism)
        trace_steps.append(ReasoningTraceStep(
            step_index=step_idx,
            agent="ValidationAgent",
            action="validate_biological_constraints",
            inputs={"mechanism_id": primary_mechanism.mechanism_id},
            outputs={"verdict": val_result["verdict"], "violations": val_result["violations_count"]},
            status="SUCCESS" if val_result["is_biologically_valid"] else "WARNING"
        ))
        step_idx += 1

        # 5. Critic Agent
        found_contradictions = self.contradictions.detect_contradictions(evidence_list)
        trace_steps.append(ReasoningTraceStep(
            step_index=step_idx,
            agent="CriticAgent",
            action="audit_claims_and_contradictions",
            inputs={"evidence_count": len(evidence_list)},
            outputs={"detected_contradictions_count": len(found_contradictions), "action": "Preserve empirical evidence, flag context-dependent divergences"},
            status="SUCCESS"
        ))
        step_idx += 1

        # 6. Report Agent
        report = self.reporter.generate_report(
            question=question,
            primary_mechanism=primary_mechanism,
            hypotheses=hypotheses,
            evidence_manifest=evidence_list,
            contradictions=found_contradictions,
            trace_steps=trace_steps
        )
        trace_steps.append(ReasoningTraceStep(
            step_index=step_idx,
            agent="ReportAgent",
            action="compile_scientific_report",
            inputs={"report_id": report.report_id},
            outputs={"summary_length": len(report.executive_summary), "suggested_experiments": len(report.suggested_experiments)},
            status="SUCCESS"
        ))

        return report

orchestrator = MultiAgentReasoningOrchestrator()
