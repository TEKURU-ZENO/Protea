"""
PROTEA PaIE - KEGG, WikiPathways & Pathway Commons Ingestion Adapters
"""

from typing import Dict, List, Set, Optional, Any
import logging
from ai.pathway_intelligence.registry import paie_registry

logger = logging.getLogger("ai.pathway_intelligence.ingestion.adapters")

@paie_registry.register_ingestion_adapter("kegg")
class KEGGAdapter:
    """Adapter for KEGG biological pathways and KGML network models."""

    def __init__(self, species: str = "hsa"):
        self.species = species
        self._pathways: Dict[str, Dict[str, Any]] = {}
        self._init_curated()

    def _init_curated(self):
        curated = [
            {
                "id": "hsa04110",
                "name": "Cell cycle - Homo sapiens",
                "proteins": ["CDK1", "CDK2", "CDK4", "CCNB1", "CCND1", "RB1", "E2F1", "TP53", "ATM", "ATR", "CHEK1", "CHEK2"],
            },
            {
                "id": "hsa04151",
                "name": "PI3K-Akt signaling pathway",
                "proteins": ["PIK3CA", "AKT1", "MTOR", "PTEN", "FOXO3", "BAD", "BCL2", "GSK3B", "MAPK1", "MAPK3"],
            },
            {
                "id": "hsa05200",
                "name": "Pathways in cancer",
                "proteins": ["TP53", "EGFR", "KRAS", "BRAF", "PIK3CA", "PTEN", "RB1", "MYC", "BCL2", "VEGFA"],
            }
        ]
        for pw in curated:
            self._pathways[pw["id"]] = {
                "id": pw["id"],
                "name": pw["name"],
                "source": "KEGG",
                "proteins": set(p.upper() for p in pw["proteins"]),
                "size": len(pw["proteins"])
            }

    def get_pathway(self, pathway_id: str) -> Optional[Dict[str, Any]]:
        pw = self._pathways.get(pathway_id)
        if not pw:
            return None
        return {
            "id": pw["id"],
            "name": pw["name"],
            "source": pw["source"],
            "proteins": sorted(list(pw["proteins"])),
            "size": pw["size"]
        }

    def list_all_pathways(self) -> List[Dict[str, Any]]:
        return [self.get_pathway(pid) for pid in self._pathways.keys()]


@paie_registry.register_ingestion_adapter("wikipathways")
class WikiPathwaysAdapter:
    """Adapter for community-curated WikiPathways."""

    def __init__(self):
        self._pathways: Dict[str, Dict[str, Any]] = {}
        self._init_curated()

    def _init_curated(self):
        curated = [
            {
                "id": "WP4290",
                "name": "DNA damage response (only ATM dependent)",
                "proteins": ["ATM", "TP53", "MDM2", "CHEK2", "BRCA1", "CDKN1A"],
            },
            {
                "id": "WP179",
                "name": "Cell cycle",
                "proteins": ["CDK1", "CDK2", "CCNB1", "RB1", "E2F1", "TP53"],
            }
        ]
        for pw in curated:
            self._pathways[pw["id"]] = {
                "id": pw["id"],
                "name": pw["name"],
                "source": "WikiPathways",
                "proteins": set(p.upper() for p in pw["proteins"]),
                "size": len(pw["proteins"])
            }

    def get_pathway(self, pathway_id: str) -> Optional[Dict[str, Any]]:
        pw = self._pathways.get(pathway_id)
        if not pw:
            return None
        return {
            "id": pw["id"],
            "name": pw["name"],
            "source": pw["source"],
            "proteins": sorted(list(pw["proteins"])),
            "size": pw["size"]
        }

    def list_all_pathways(self) -> List[Dict[str, Any]]:
        return [self.get_pathway(pid) for pid in self._pathways.keys()]


@paie_registry.register_ingestion_adapter("pathway_commons")
class PathwayCommonsAdapter:
    """Adapter for Pathway Commons unified molecular interaction networks."""

    def __init__(self):
        self._pathways: Dict[str, Dict[str, Any]] = {}

    def get_pathway(self, pathway_id: str) -> Optional[Dict[str, Any]]:
        return self._pathways.get(pathway_id)

    def list_all_pathways(self) -> List[Dict[str, Any]]:
        return list(self._pathways.values())
