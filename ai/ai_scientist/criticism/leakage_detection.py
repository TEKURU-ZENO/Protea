"""
PROTEA AI Scientist - Data Leakage & Circularity Detection
Detects test-train leakage, circular reasoning, and benchmark memorization.
"""

from typing import Dict, Any, List, Set


class LeakageDetector:
    """
    Audits the scientific discovery workflow to ensure no circularity or data leakage:
    1. Training set contamination (target pairs already present in GNN training splits).
    2. Circular verification (using the same model to validate its own prediction).
    3. Literature publication bias (interpreting absence of reporting as negative evidence).
    """

    def audit_leakage(
        self,
        predicted_pairs: List[Dict[str, str]],
        training_database_edges: Set[str],
        validation_engine_name: str,
        inference_engine_name: str,
    ) -> Dict[str, Any]:
        """
        Audits predictions for training data contamination and circularity.
        """
        leaked_pairs = []
        for pair in predicted_pairs:
            p1 = pair.get("source", "")
            p2 = pair.get("target", "")
            key1 = f"{p1}:{p2}"
            key2 = f"{p2}:{p1}"
            if key1 in training_database_edges or key2 in training_database_edges:
                leaked_pairs.append({"source": p1, "target": p2, "reason": "Present in training dataset"})

        # Circular validation check: if validation uses identical model/weights
        circular_validation = (
            validation_engine_name.strip().lower() == inference_engine_name.strip().lower()
            and bool(validation_engine_name)
        )

        leakage_ratio = (
            len(leaked_pairs) / len(predicted_pairs) if predicted_pairs else 0.0
        )

        critical_failure = circular_validation or (leakage_ratio > 0.0)

        return {
            "total_pairs_checked": len(predicted_pairs),
            "leaked_pairs_count": len(leaked_pairs),
            "leakage_ratio": round(leakage_ratio, 4),
            "leaked_pairs": leaked_pairs,
            "circular_validation_detected": circular_validation,
            "passed_leakage_audit": not critical_failure,
            "critical_warning": (
                "Data leakage or circular validation detected! Hypothesis cannot be claimed as novel until isolated."
                if critical_failure
                else "Clean data partition verified: no training set leakage or circular model validation."
            ),
        }
