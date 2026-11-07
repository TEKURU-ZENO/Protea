"""
PROTEA Phase 10: Domain Disruption Analyzer
Maps residue alterations to functional protein domains, active sites, catalytic residues, and post-translational modification sites.
"""

from __future__ import annotations
from typing import Dict, List, Any, Optional

# Curated functional domain architectures for key precision therapeutic targets
DOMAIN_REGISTRIES: Dict[str, List[Dict[str, Any]]] = {
    "BRAF": [
        {"name": "RBD (Ras-binding domain)", "start": 156, "end": 227, "type": "interaction_domain"},
        {"name": "C1 domain (Phorbol ester/DAG-type)", "start": 235, "end": 280, "type": "regulatory"},
        {"name": "Protein Kinase Domain", "start": 457, "end": 717, "type": "catalytic_domain"},
        {"name": "Glycine-rich loop (P-loop)", "start": 464, "end": 471, "type": "atp_binding"},
        {"name": "Catalytic loop", "start": 574, "end": 581, "type": "catalytic_site"},
        {"name": "Activation segment / A-loop", "start": 593, "end": 623, "type": "regulatory_switch"}
    ],
    "EGFR": [
        {"name": "Extracellular Receptor L Domain I", "start": 25, "end": 190, "type": "ligand_binding"},
        {"name": "Furin-like Cysteine-rich Domain II", "start": 191, "end": 334, "type": "dimerization_arm"},
        {"name": "Transmembrane domain", "start": 646, "end": 668, "type": "transmembrane"},
        {"name": "Protein Kinase Domain", "start": 690, "end": 953, "type": "catalytic_domain"},
        {"name": "ATP-binding pocket / Gatekeeper", "start": 788, "end": 796, "type": "gatekeeper"},
        {"name": "Activation loop", "start": 855, "end": 876, "type": "regulatory_switch"}
    ],
    "KRAS": [
        {"name": "P-loop (Phosphate-binding)", "start": 10, "end": 17, "type": "catalytic_site"},
        {"name": "Switch I", "start": 30, "end": 38, "type": "effector_binding"},
        {"name": "Switch II", "start": 59, "end": 67, "type": "catalytic_switch"},
        {"name": "GTPase Core", "start": 1, "end": 166, "type": "catalytic_domain"}
    ],
    "TP53": [
        {"name": "Transactivation domain (TAD)", "start": 1, "end": 61, "type": "regulatory"},
        {"name": "Proline-rich domain", "start": 63, "end": 97, "type": "structural"},
        {"name": "DNA-binding core domain", "start": 102, "end": 292, "type": "catalytic_domain"},
        {"name": "Zinc-coordination site", "start": 175, "end": 242, "type": "catalytic_site"},
        {"name": "Tetramerization domain", "start": 325, "end": 356, "type": "oligomerization"}
    ]
}


class DomainDisruptionAnalyzer:
    """Analyzes the structural and functional domains disrupted by mutations."""

    @classmethod
    def analyze_disruption(cls, gene_symbol: str, position: int) -> Dict[str, Any]:
        """Identifies intersected domains, catalytic roles, and gatekeeper involvement."""
        gene = gene_symbol.upper()
        domains = DOMAIN_REGISTRIES.get(gene, [])

        intersected: List[Dict[str, Any]] = []
        is_catalytic = False
        is_gatekeeper = False
        is_activation_loop = False

        for dom in domains:
            if dom["start"] <= position <= dom["end"]:
                intersected.append(dom)
                if dom["type"] in ["catalytic_site", "catalytic_domain"]:
                    is_catalytic = True
                if dom["type"] == "gatekeeper":
                    is_gatekeeper = True
                if dom["type"] == "regulatory_switch":
                    is_activation_loop = True

        return {
            "gene": gene,
            "position": position,
            "intersected_domains": [d["name"] for d in intersected],
            "domain_details": intersected,
            "is_catalytic_site": is_catalytic,
            "is_gatekeeper": is_gatekeeper,
            "is_activation_loop": is_activation_loop,
            "disruption_severity": "HIGH" if (is_catalytic or is_gatekeeper or is_activation_loop) else ("MODERATE" if intersected else "LOW")
        }
