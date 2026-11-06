"""
PROTEA PaIE - Reactome Pathway Ingestion Adapter
Parses Reactome hierarchical pathway structures, events, and GMT gene sets.
"""

from typing import Dict, List, Set, Optional, Any
import logging
from ai.pathway_intelligence.registry import paie_registry

logger = logging.getLogger("ai.pathway_intelligence.ingestion.reactome")

@paie_registry.register_ingestion_adapter("reactome")
class ReactomeAdapter:
    """Ingestion and query interface for Reactome Pathway Knowledge."""

    def __init__(self, species: str = "Homo sapiens"):
        self.species = species
        # In-memory index of pathways: {pathway_id: {"name": str, "proteins": Set[str], "parent": str, "children": List[str]}}
        self._pathways: Dict[str, Dict[str, Any]] = {}
        self._protein_to_pathways: Dict[str, Set[str]] = {}
        self._initialize_curated_baselines()

    def _initialize_curated_baselines(self):
        """Pre-populate core physiological human signaling pathways for immediate availability."""
        curated_pathways = [
            {
                "id": "R-HSA-109581",
                "name": "Apoptosis",
                "category": "Cellular Responses",
                "proteins": ["TP53", "BAX", "BCL2", "CASP3", "CASP8", "CASP9", "CYCS", "FAS", "APAF1", "BID", "BAD", "XIAP"],
                "parent": "R-HSA-109582",
                "reactions": [
                    {"source": "FAS", "target": "CASP8", "type": "activates"},
                    {"source": "CASP8", "target": "BID", "type": "cleaves"},
                    {"source": "BID", "target": "BAX", "type": "activates"},
                    {"source": "BAX", "target": "CYCS", "type": "translocates"},
                    {"source": "CYCS", "target": "APAF1", "type": "complex_formation"},
                    {"source": "APAF1", "target": "CASP9", "type": "activates"},
                    {"source": "CASP9", "target": "CASP3", "type": "cleaves"},
                    {"source": "BCL2", "target": "BAX", "type": "inhibits"},
                ]
            },
            {
                "id": "R-HSA-1257604",
                "name": "PIP3 activates AKT signaling",
                "category": "Signal Transduction",
                "proteins": ["PIK3CA", "PIK3R1", "PTEN", "AKT1", "AKT2", "PDPK1", "MTOR", "FOXO3", "GSK3B", "BAD"],
                "parent": "R-HSA-1980145",
                "reactions": [
                    {"source": "PIK3CA", "target": "PDPK1", "type": "activates"},
                    {"source": "PDPK1", "target": "AKT1", "type": "phosphorylates"},
                    {"source": "PTEN", "target": "PIK3CA", "type": "inhibits"},
                    {"source": "AKT1", "target": "MTOR", "type": "activates"},
                    {"source": "AKT1", "target": "FOXO3", "type": "inhibits"},
                    {"source": "AKT1", "target": "GSK3B", "type": "inhibits"},
                    {"source": "AKT1", "target": "BAD", "type": "inhibits"},
                ]
            },
            {
                "id": "R-HSA-5683057",
                "name": "MAPK family signaling cascades",
                "category": "Signal Transduction",
                "proteins": ["EGFR", "GRB2", "SOS1", "HRAS", "KRAS", "RAF1", "BRAF", "MAP2K1", "MAP2K2", "MAPK1", "MAPK3", "MYC"],
                "parent": "R-HSA-1980145",
                "reactions": [
                    {"source": "EGFR", "target": "GRB2", "type": "activates"},
                    {"source": "GRB2", "target": "SOS1", "type": "complex_formation"},
                    {"source": "SOS1", "target": "KRAS", "type": "activates"},
                    {"source": "KRAS", "target": "BRAF", "type": "activates"},
                    {"source": "BRAF", "target": "MAP2K1", "type": "phosphorylates"},
                    {"source": "MAP2K1", "target": "MAPK1", "type": "phosphorylates"},
                    {"source": "MAPK1", "target": "MYC", "type": "phosphorylates"},
                ]
            },
            {
                "id": "R-HSA-69278",
                "name": "Cell Cycle Checkpoints",
                "category": "Cell Cycle",
                "proteins": ["CDK1", "CDK2", "CDK4", "CDK6", "CCNA2", "CCNB1", "CCND1", "CCNE1", "RB1", "E2F1", "CDKN1A", "CDKN2A", "ATM", "ATR", "CHEK1", "CHEK2"],
                "parent": "R-HSA-1640170",
                "reactions": [
                    {"source": "ATM", "target": "CHEK2", "type": "phosphorylates"},
                    {"source": "CHEK2", "target": "CDKN1A", "type": "activates"},
                    {"source": "CDKN1A", "target": "CDK2", "type": "inhibits"},
                    {"source": "CDK4", "target": "RB1", "type": "phosphorylates"},
                    {"source": "RB1", "target": "E2F1", "type": "inhibits"},
                ]
            },
            {
                "id": "R-HSA-73894",
                "name": "DNA Repair Pathways",
                "category": "DNA Repair",
                "proteins": ["BRCA1", "BRCA2", "BARD1", "RAD51", "ATM", "CHEK2", "PALB2", "TP53BP1", "PARP1"],
                "parent": "R-HSA-73886",
                "reactions": [
                    {"source": "ATM", "target": "BRCA1", "type": "phosphorylates"},
                    {"source": "BRCA1", "target": "BARD1", "type": "complex_formation"},
                    {"source": "BRCA1", "target": "RAD51", "type": "activates"},
                    {"source": "BRCA2", "target": "RAD51", "type": "activates"},
                ]
            }
        ]

        for pw in curated_pathways:
            self.add_pathway(
                pathway_id=pw["id"],
                name=pw["name"],
                category=pw.get("category", "General"),
                proteins=pw["proteins"],
                reactions=pw.get("reactions", []),
                parent=pw.get("parent")
            )

    def add_pathway(self, pathway_id: str, name: str, category: str, proteins: List[str], reactions: Optional[List[Dict[str, str]]] = None, parent: Optional[str] = None):
        """Add or update a pathway definition."""
        prot_set = set(p.upper() for p in proteins)
        self._pathways[pathway_id] = {
            "id": pathway_id,
            "name": name,
            "category": category,
            "proteins": prot_set,
            "reactions": reactions or [],
            "parent": parent,
            "size": len(prot_set)
        }
        for p in prot_set:
            if p not in self._protein_to_pathways:
                self._protein_to_pathways[p] = set()
            self._protein_to_pathways[p].add(pathway_id)

    def load_gmt(self, gmt_content: str):
        """Parse standard Gene Matrix Transposed (.gmt) pathway file content."""
        count = 0
        for line in gmt_content.strip().split("\n"):
            parts = line.strip().split("\t")
            if len(parts) >= 3:
                name = parts[0]
                pw_id = parts[1] if parts[1] else f"REACTOME_{name.replace(' ', '_').upper()}"
                genes = [g.strip().upper() for g in parts[2:] if g.strip()]
                self.add_pathway(pathway_id=pw_id, name=name, category="Imported GMT", proteins=genes)
                count += 1
        logger.info(f"Loaded {count} pathways from GMT format.")
        return count

    def get_pathway(self, pathway_id: str) -> Optional[Dict[str, Any]]:
        pw = self._pathways.get(pathway_id)
        if not pw:
            return None
        return {
            "id": pw["id"],
            "name": pw["name"],
            "category": pw["category"],
            "proteins": sorted(list(pw["proteins"])),
            "reactions": pw["reactions"],
            "parent": pw["parent"],
            "size": pw["size"]
        }

    def get_pathways_for_protein(self, protein_id: str) -> List[Dict[str, Any]]:
        pw_ids = self._protein_to_pathways.get(protein_id.upper(), set())
        return [self.get_pathway(pid) for pid in pw_ids if self.get_pathway(pid) is not None]

    def list_all_pathways(self) -> List[Dict[str, Any]]:
        return [self.get_pathway(pid) for pid in self._pathways.keys()]
