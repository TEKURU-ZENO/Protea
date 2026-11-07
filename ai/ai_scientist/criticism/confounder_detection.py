"""
PROTEA AI Scientist - Confounder & Artifact Detection
Identifies potential experimental confounders, off-target effects, and assay artifacts.
"""

from typing import Dict, Any, List


class ConfounderDetector:
    """
    Audits computational and simulated experimental designs for known confounders,
    cross-talk, solvent/vehicle artifacts, and non-specific interactions.
    """

    CONFOUNDER_RULES = [
        {
            "id": "CONF_001",
            "name": "Vehicle / Solvent Shift",
            "condition": lambda exp: exp.get("controls", {}).get("vehicle") is None,
            "severity": "HIGH",
            "description": "Missing vehicle/solvent control allows carrier effects to masquerade as molecular intervention effects.",
        },
        {
            "id": "CONF_002",
            "name": "Off-Target Target Saturation",
            "condition": lambda exp: exp.get("concentration_uM", 1.0) > 20.0,
            "severity": "HIGH",
            "description": "Excessive intervention concentration (>20 uM) induces promiscuous off-target binding.",
        },
        {
            "id": "CONF_003",
            "name": "Orthogonal Control Absence",
            "condition": lambda exp: not exp.get("controls", {}).get("orthogonal_controls"),
            "severity": "MEDIUM",
            "description": "Lack of orthogonal readout or independent target validation increases risk of assay-specific artifact.",
        },
        {
            "id": "CONF_004",
            "name": "Dynamic Range Floor/Ceiling Effect",
            "condition": lambda exp: "baseline_expression" in exp and (exp["baseline_expression"] < 0.05 or exp["baseline_expression"] > 0.95),
            "severity": "MEDIUM",
            "description": "Baseline readout is near dynamic range boundary, creating artificial compression or non-linear distortion.",
        },
        {
            "id": "CONF_005",
            "name": "Simulation Convergence Instability",
            "condition": lambda exp: exp.get("solver_residuals_max", 0.0) > 1e-3,
            "severity": "HIGH",
            "description": "Numerical solver residuals exceed tolerance threshold, risking numerical instability interpreted as biological oscillations.",
        },
    ]

    def audit_confounders(self, experiment_design: Dict[str, Any]) -> Dict[str, Any]:
        """
        Runs automated confounder rules against experiment specification.
        """
        flagged_confounders = []
        for rule in self.CONFOUNDER_RULES:
            try:
                if rule["condition"](experiment_design):
                    flagged_confounders.append({
                        "rule_id": rule["id"],
                        "name": rule["name"],
                        "severity": rule["severity"],
                        "description": rule["description"],
                    })
            except Exception:
                continue

        has_high_severity = any(c["severity"] == "HIGH" for c in flagged_confounders)
        confounder_risk_score = round(
            sum(0.3 if c["severity"] == "HIGH" else 0.15 for c in flagged_confounders), 2
        )
        confounder_risk_score = min(1.0, confounder_risk_score)

        return {
            "confounders_detected_count": len(flagged_confounders),
            "confounders": flagged_confounders,
            "confounder_risk_score": confounder_risk_score,
            "is_valid": not has_high_severity,
            "mitigation_recommendations": [
                f"Address {c['name']}: {c['description']}" for c in flagged_confounders
            ],
        }
