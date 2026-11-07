"""
PROTEA AI Scientist - Evaluation Benchmarks Suite
Implements the 7 core scientific research benchmarks for evaluating AI scientist capability.
"""

from typing import Dict, Any, List


class ScientificDiscoveryBenchmarkSuite:
    """
    Standardized benchmark suite measuring performance across all 7 research dimensions.
    """

    def evaluate_literature_synthesis(
        self,
        extracted_claims: List[Dict[str, Any]],
        ground_truth_claims: List[str],
    ) -> Dict[str, Any]:
        """
        Benchmark 1: Literature Synthesis Accuracy & Grounding.
        """
        matched = 0
        for c in extracted_claims:
            stmt = c.get("statement", "").lower()
            if any(gt.lower() in stmt or stmt in gt.lower() for gt in ground_truth_claims):
                matched += 1

        precision = matched / len(extracted_claims) if extracted_claims else 1.0
        recall = matched / len(ground_truth_claims) if ground_truth_claims else 1.0
        f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0

        return {
            "benchmark": "BM1_LITERATURE_SYNTHESIS",
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1_score": round(f1, 4),
            "status": "PASS" if f1 >= 0.70 else "NEEDS_IMPROVEMENT",
        }

    def evaluate_research_gap_detection(
        self,
        detected_gaps: List[Dict[str, Any]],
        known_expert_gaps: List[str],
    ) -> Dict[str, Any]:
        """
        Benchmark 2: Research Gap Identification Quality.
        """
        identified = 0
        for eg in known_expert_gaps:
            if any(eg.lower() in g.get("description", "").lower() for g in detected_gaps):
                identified += 1

        coverage = identified / len(known_expert_gaps) if known_expert_gaps else 1.0

        return {
            "benchmark": "BM2_RESEARCH_GAP_QUALITY",
            "coverage_rate": round(coverage, 4),
            "status": "PASS" if coverage >= 0.60 else "NEEDS_IMPROVEMENT",
        }

    def evaluate_hypothesis_falsifiability(
        self,
        hypotheses: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Benchmark 3: Hypothesis Novelty & Falsifiability.
        """
        falsifiable_count = 0
        quantitative_pred_count = 0

        for h in hypotheses:
            has_crit = len(h.get("falsification_criteria", [])) > 0
            has_preds = len(h.get("predictions", [])) > 0
            if has_crit:
                falsifiable_count += 1
            if has_preds:
                quantitative_pred_count += 1

        n = len(hypotheses) if hypotheses else 1
        rate = falsifiable_count / n

        return {
            "benchmark": "BM3_HYPOTHESIS_FALSIFIABILITY",
            "falsifiable_rate": round(rate, 4),
            "has_quantitative_predictions_rate": round(quantitative_pred_count / n, 4),
            "status": "PASS" if rate >= 0.80 else "NEEDS_IMPROVEMENT",
        }

    def evaluate_experiment_design_soundness(
        self,
        experiment_plan: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Benchmark 4: Experiment Design Soundness.
        """
        controls = experiment_plan.get("controls", {})
        has_pos = bool(controls.get("positive_controls"))
        has_neg = bool(controls.get("negative_controls"))
        has_veh = bool(controls.get("vehicle"))
        reps = experiment_plan.get("replicate_count", 0) >= 3

        passed = has_pos and has_neg and has_veh and reps

        return {
            "benchmark": "BM4_EXPERIMENT_DESIGN_SOUNDNESS",
            "has_positive_control": has_pos,
            "has_negative_control": has_neg,
            "has_vehicle_control": has_veh,
            "adequate_replicates": reps,
            "soundness_score": sum([has_pos, has_neg, has_veh, reps]) / 4.0,
            "status": "PASS" if passed else "FAIL",
        }

    def evaluate_execution_reliability(
        self,
        execution_records: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Benchmark 5: Execution Reliability.
        """
        success_count = sum(1 for e in execution_records if e.get("success", False))
        rate = success_count / len(execution_records) if execution_records else 1.0

        return {
            "benchmark": "BM5_EXECUTION_RELIABILITY",
            "completion_rate": round(rate, 4),
            "status": "PASS" if rate >= 0.90 else "NEEDS_IMPROVEMENT",
        }

    def evaluate_adversarial_rigor(
        self,
        adversarial_audits: List[Dict[str, Any]],
        flaws_present: bool,
    ) -> Dict[str, Any]:
        """
        Benchmark 6: Adversarial Review Rigor.
        """
        caught_flaws = any(not a.get("passed_audit", True) for a in adversarial_audits)
        correct_verdict = (caught_flaws == flaws_present)

        return {
            "benchmark": "BM6_ADVERSARIAL_RIGOR",
            "correct_verdict": correct_verdict,
            "status": "PASS" if correct_verdict else "FAIL",
        }

    def evaluate_rediscovery_benchmark(
        self,
        discovered_mechanisms: List[str],
        historical_discovery_target: str,
    ) -> Dict[str, Any]:
        """
        Benchmark 7: End-to-End Historical Rediscovery Benchmark.
        (e.g., historical target: 'T790M gatekeeper mutation restores kinase activity' or 'MET amplification bypasses EGFR').
        """
        target_lower = historical_discovery_target.lower()
        rediscovered = any(target_lower in m.lower() or m.lower() in target_lower for m in discovered_mechanisms)

        return {
            "benchmark": "BM7_REDISCOVERY",
            "target": historical_discovery_target,
            "rediscovered": rediscovered,
            "status": "PASS" if rediscovered else "FAIL",
        }
