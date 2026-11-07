"""
PROTEA Phase 10: Interaction Rewiring Predictor
Predicts mutation-conditioned PPI alterations: retained, lost, and novel candidate gain edges.
"""

from __future__ import annotations
from typing import Dict, List, Any, Optional
from ai.mutation_therapeutics.schema import InteractionRewiring, FunctionalClass
from ai.mutation_therapeutics.interaction_rewiring.interface_disruption import PPIInterfaceDisruptionAnalyzer

# Curated reference PPI partners for core signaling nodes
BASELINE_INTERACTOMES: Dict[str, List[Dict[str, Any]]] = {
    "BRAF": [
        {"partner": "MAP2K1", "confidence": 0.98, "type": "phosphorylation_target"},
        {"partner": "MAP2K2", "confidence": 0.97, "type": "phosphorylation_target"},
        {"partner": "KRAS", "confidence": 0.95, "type": "upstream_activator"},
        {"partner": "HRAS", "confidence": 0.94, "type": "upstream_activator"},
        {"partner": "YWHAZ", "confidence": 0.92, "type": "inhibitory_clamp"},
        {"partner": "CRAF", "confidence": 0.88, "type": "heterodimer"}
    ],
    "EGFR": [
        {"partner": "GRB2", "confidence": 0.99, "type": "adaptor"},
        {"partner": "SHC1", "confidence": 0.97, "type": "adaptor"},
        {"partner": "ERBB2", "confidence": 0.96, "type": "heterodimer"},
        {"partner": "STAT3", "confidence": 0.91, "type": "signaling_transducer"},
        {"partner": "CBL", "confidence": 0.90, "type": "ubiquitin_ligase"}
    ],
    "KRAS": [
        {"partner": "BRAF", "confidence": 0.96, "type": "effector"},
        {"partner": "RAF1", "confidence": 0.95, "type": "effector"},
        {"partner": "PIK3CA", "confidence": 0.94, "type": "effector"},
        {"partner": "NF1", "confidence": 0.92, "type": "gap_regulator"},
        {"partner": "SOS1", "confidence": 0.91, "type": "gef_activator"}
    ],
    "TP53": [
        {"partner": "MDM2", "confidence": 0.99, "type": "e3_ligase"},
        {"partner": "MDM4", "confidence": 0.96, "type": "inhibitor"},
        {"partner": "TP53BP1", "confidence": 0.94, "type": "dna_repair"},
        {"partner": "EP300", "confidence": 0.93, "type": "acetyltransferase"}
    ]
}


class RewiringPredictor:
    """Predicts how individual mutations rewire local interactome topologies."""

    @classmethod
    def predict_rewiring(
        cls,
        gene_symbol: str,
        wildtype_aa: str,
        position: int,
        mutant_aa: str,
        functional_class: FunctionalClass = FunctionalClass.UNCHARACTERIZED
    ) -> InteractionRewiring:
        """
        Determines interaction retention, loss, and candidate gains.
        Enforces biological plausibility:
        - LoF causes edge losses
        - GoF retains/hyperactivates downstream effectors while losing inhibitory clamps
        """
        gene = gene_symbol.upper()
        mutation_label = f"{gene}_{wildtype_aa}{position}{mutant_aa}"
        mut_id = f"PROT_{mutation_label}"
        wt_id = f"PROT_{gene}"

        baseline = BASELINE_INTERACTOMES.get(gene, [
            {"partner": "EFFECTOR_1", "confidence": 0.90, "type": "downstream"},
            {"partner": "REGULATOR_1", "confidence": 0.85, "type": "upstream"},
            {"partner": "INHIBITOR_1", "confidence": 0.80, "type": "clamp"}
        ])

        interface_res = PPIInterfaceDisruptionAnalyzer.check_partner_interfaces(gene, position)
        disrupted_set = set(interface_res["disrupted_partners"])

        retained: List[Dict[str, Any]] = []
        lost: List[Dict[str, Any]] = []
        gained: List[Dict[str, Any]] = []

        # Specific biological rewiring for hallmark mutations
        if gene == "BRAF" and position == 600:
            # V600E functions as active monomer independent of RAS and 14-3-3 (YWHAZ)
            for edge in baseline:
                p = edge["partner"]
                if p == "YWHAZ":
                    lost.append({**edge, "reason": "Loss of auto-inhibitory 14-3-3 clamp binding"})
                elif p in ["KRAS", "HRAS"]:
                    lost.append({**edge, "reason": "Uncoupled from upstream RAS-GTP activation requirement"})
                else:
                    retained.append({**edge, "affinity_change": "hyperactivated_constitutive_binding"})

            # Gained interactions
            gained.append({
                "partner": "MAP2K1_MONOMER",
                "confidence": 0.95,
                "type": "constitutive_substrate",
                "reason": "Hyperactive phosphorylation of MEK1 independent of dimerization"
            })
            gained.append({
                "partner": "HSP90AA1",
                "confidence": 0.89,
                "type": "chaperone_dependency",
                "reason": "Addiction to molecular chaperones for mutant stability"
            })

        elif gene == "KRAS" and position in [12, 13, 61]:
            # KRAS G12D/V/C: Impairs GTPase-activating protein (NF1) hydrolysis
            for edge in baseline:
                p = edge["partner"]
                if p == "NF1":
                    lost.append({**edge, "reason": "Inability of GAP to insert arginine finger into catalytic cleft"})
                else:
                    retained.append({**edge, "affinity_change": "persistent_gtp_bound_activation"})

            gained.append({
                "partner": "PIK3CA_HYPERACTIVE",
                "confidence": 0.92,
                "type": "oncogenic_effector",
                "reason": "Persistent non-terminating recruitment of PI3K lipid kinase"
            })

        elif gene == "TP53" and functional_class in [FunctionalClass.LOSS_OF_FUNCTION, FunctionalClass.DOMINANT_NEGATIVE]:
            # TP53 R175H loses sequence-specific DNA repair complexes and gains oncogenic neomorphic interactions
            for edge in baseline:
                lost.append({**edge, "reason": "Structural core collapse prevents interface complex assembly"})
            gained.append({
                "partner": "TP73",
                "confidence": 0.88,
                "type": "neomorphic_gain_dominant_negative",
                "reason": "Mutant p53 binds and sequesters p73 tumor suppressor"
            })
            gained.append({
                "partner": "NFE2L2",
                "confidence": 0.85,
                "type": "neomorphic_activation",
                "reason": "Transcription factor crosstalk promoting antioxidant chemoresistance"
            })

        else:
            # General heuristic rewiring
            for edge in baseline:
                partner = edge["partner"]
                if partner in disrupted_set:
                    lost.append({**edge, "reason": f"Residue {position} directly in {partner} binding interface"})
                elif functional_class == FunctionalClass.LOSS_OF_FUNCTION:
                    lost.append({**edge, "reason": "Loss of function prevents complex stability"})
                else:
                    retained.append({**edge, "affinity_change": "retained_intact"})

        total_ref = len(baseline)
        rewiring_index = round((len(lost) + len(gained)) / max(1, (len(retained) + len(lost))), 2)

        return InteractionRewiring(
            mutation_label=mutation_label,
            mutant_protein_id=mut_id,
            wildtype_protein_id=wt_id,
            retained_interactions=retained,
            lost_interactions=lost,
            gained_interactions=gained,
            total_reference_edges=total_ref,
            rewiring_index=rewiring_index
        )
