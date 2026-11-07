"""
PROTEA BRE - Biological Validation & Constraint Engine
Validates cellular compartment co-localization, reaction directionality, and experimental claim citations.
"""

from typing import List, Dict, Set, Optional, Any
from ai.biological_reasoning.schema import MolecularMechanism
from ai.pathway_intelligence.annotation.functional_annotation import localization_mapper

class BiologicalConstraintValidator:
    """Audits proposed mechanisms for biological plausibility and compartment constraints."""

    # Incompatible pairs without known translocation machinery
    INCOMPATIBLE_COMPARTMENTS = [
        ({"nucleus"}, {"extracellular"}),
        ({"mitochondrion"}, {"extracellular"}),
    ]

    def validate_mechanism(self, mechanism: MolecularMechanism) -> Dict[str, Any]:
        """
        Verify that sequential interacting proteins in the mechanism occupy compatible cellular compartments.
        """
        violations = []
        warnings = []

        for step in mechanism.steps:
            u, v = step.source, step.target
            loc_u = set(localization_mapper.get_localization(u))
            loc_v = set(localization_mapper.get_localization(v))

            # Check overlap or intermediate cytosol/membrane bridging
            shared = loc_u & loc_v
            if not shared:
                # Check for strictly incompatible compartmentalization
                for c1, c2 in self.INCOMPATIBLE_COMPARTMENTS:
                    if (loc_u == c1 and loc_v == c2) or (loc_u == c2 and loc_v == c1):
                        violations.append({
                            "type": "COMPARTMENT_INCOMPATIBILITY",
                            "step": f"{u} ➔ {v}",
                            "source_compartments": sorted(list(loc_u)),
                            "target_compartments": sorted(list(loc_v)),
                            "detail": f"{u} is strictly localized to {loc_u} while {v} is in {loc_v} without known direct physical interface."
                        })
                        break
                else:
                    # Non-identical but plausible (e.g. cytosol <-> nucleus via nuclear pore transport)
                    warnings.append({
                        "type": "TRANSLOCATION_REQUIRED",
                        "step": f"{u} ➔ {v}",
                        "detail": f"Interaction requires active nuclear/mitochondrial translocation or membrane-cytosol docking."
                    })

            # Check evidence grounding
            if not step.evidence_ids and step.evidence_status.value == "EXPERIMENTAL":
                warnings.append({
                    "type": "UNSUPPORTED_EXPERIMENTAL_STATUS",
                    "step": f"{u} ➔ {v}",
                    "detail": "Step marked as EXPERIMENTAL but lacks primary experimental citation ID."
                })

        is_valid = len(violations) == 0

        return {
            "is_biologically_valid": is_valid,
            "violations_count": len(violations),
            "warnings_count": len(warnings),
            "violations": violations,
            "warnings": warnings,
            "verdict": "PASSED" if is_valid else "FAILED_CONSTRAINTS"
        }
