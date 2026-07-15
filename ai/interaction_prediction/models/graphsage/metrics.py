from typing import Dict
import numpy as np

class GnnMetrics:
    @staticmethod
    def calculate(y_true: np.ndarray, y_pred_prob: np.ndarray, threshold: float = 0.5) -> Dict[str, float]:
        """Calculates evaluation metrics for GNN binary classifications."""
        y_pred = (y_pred_prob >= threshold).astype(int)
        
        # Guard against zero divisions
        tp = np.sum((y_true == 1) & (y_pred == 1))
        fp = np.sum((y_true == 0) & (y_pred == 1))
        fn = np.sum((y_true == 1) & (y_pred == 0))
        tn = np.sum((y_true == 0) & (y_pred == 0))
        
        precision = float(tp / (tp + fp)) if (tp + fp) > 0 else 0.0
        recall = float(tp / (tp + fn)) if (tp + fn) > 0 else 0.0
        f1 = float(2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0
        
        # Matthews Correlation Coefficient
        mcc_denom = np.sqrt(float(tp + fp) * (tp + fn) * (tn + fp) * (tn + fn))
        mcc = float((tp * tn) - (fp * fn)) / mcc_denom if mcc_denom > 0 else 0.0
        
        # Simple ROC-AUC & PR-AUC estimates for mock evaluation
        # (Using sorted values to construct simple AUC curves)
        desc_score_indices = np.argsort(y_pred_prob)[::-1]
        y_true_sorted = y_true[desc_score_indices]
        
        tps = np.cumsum(y_true_sorted)
        fps = np.cumsum(1 - y_true_sorted)
        
        tpr = tps / max(np.sum(y_true), 1.0)
        fpr = fps / max(np.sum(1 - y_true), 1.0)
        
        roc_auc = float(np.trapz(tpr, fpr)) if len(fpr) > 1 else 0.5
        pr_auc = float(np.trapz(tpr / (tps + fps), tpr)) if len(tpr) > 1 else 0.5
        
        return {
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "mcc": mcc,
            "roc_auc": abs(roc_auc),
            "pr_auc": abs(pr_auc)
        }
