"""
PROTEA PaIE - Cross-Species Ortholog Mapping & Pathway Evolution
Maps orthologous pathway components across model organisms and quantifies evolutionary conservation.
"""

from typing import List, Dict, Set, Optional, Any
import numpy as np

class CrossSpeciesOrthologMapper:
    """Maintains cross-species orthology relationships for model organisms."""

    def __init__(self):
        # {(human_protein, target_species): (ortholog_symbol, sequence_identity)}
        self._orthologs: Dict[tuple, tuple] = {}
        self._init_curated_orthology()

    def _init_curated_orthology(self):
        """Curated orthology dictionary for core signaling cascade proteins."""
        # Human -> Mouse (Mus musculus)
        self.add_ortholog("TP53", "mouse", "Trp53", identity=0.88)
        self.add_ortholog("AKT1", "mouse", "Akt1", identity=0.98)
        self.add_ortholog("EGFR", "mouse", "Egfr", identity=0.92)
        self.add_ortholog("BRCA1", "mouse", "Brca1", identity=0.74)
        self.add_ortholog("CASP3", "mouse", "Casp3", identity=0.89)
        self.add_ortholog("MAPK1", "mouse", "Mapk1", identity=0.99)

        # Human -> Zebrafish (Danio rerio)
        self.add_ortholog("TP53", "zebrafish", "tp53", identity=0.62)
        self.add_ortholog("AKT1", "zebrafish", "akt1", identity=0.87)
        self.add_ortholog("EGFR", "zebrafish", "egfra", identity=0.76)

        # Human -> Drosophila melanogaster
        self.add_ortholog("TP53", "drosophila", "p53", identity=0.38)
        self.add_ortholog("AKT1", "drosophila", "Akt", identity=0.65)
        self.add_ortholog("EGFR", "drosophila", "Egfr", identity=0.55)

        # Human -> Yeast (Saccharomyces cerevisiae)
        self.add_ortholog("MAPK1", "yeast", "FUS3", identity=0.52)
        self.add_ortholog("AKT1", "yeast", "SCH9", identity=0.45)

    def add_ortholog(self, human_protein: str, species: str, ortholog_id: str, identity: float):
        self._orthologs[(human_protein.upper(), species.lower())] = (ortholog_id, float(identity))

    def map_protein(self, human_protein: str, species: str) -> Optional[Dict[str, Any]]:
        key = (human_protein.upper(), species.lower())
        if key in self._orthologs:
            orth_id, ident = self._orthologs[key]
            return {
                "human_protein": human_protein.upper(),
                "target_species": species.lower(),
                "ortholog_symbol": orth_id,
                "sequence_identity": ident
            }
        return None

    def map_pathway(self, pathway_proteins: List[str], species: str) -> Dict[str, Any]:
        """Project a human pathway into a target species."""
        mapped = []
        unmapped = []
        identities = []

        for p in pathway_proteins:
            res = self.map_protein(p, species)
            if res:
                mapped.append(res)
                identities.append(res["sequence_identity"])
            else:
                unmapped.append(p.upper())

        total = len(pathway_proteins)
        conservation_ratio = len(mapped) / total if total > 0 else 0.0
        mean_identity = float(np.mean(identities)) if identities else 0.0

        return {
            "target_species": species.lower(),
            "total_pathway_proteins": total,
            "conserved_orthologs_count": len(mapped),
            "conservation_ratio": round(conservation_ratio, 3),
            "mean_sequence_identity": round(mean_identity, 3),
            "conserved_proteins": mapped,
            "lost_or_diverged_proteins": unmapped
        }


class PathwayEvolutionAnalyzer:
    """Analyzes evolutionary conservation, rewiring, and pathway gain/loss."""

    def __init__(self, mapper: Optional[CrossSpeciesOrthologMapper] = None):
        self.mapper = mapper or CrossSpeciesOrthologMapper()

    def compare_pathway_across_species(
        self,
        pathway_id: str,
        pathway_name: str,
        pathway_proteins: List[str],
        species_list: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        targets = species_list or ["mouse", "zebrafish", "drosophila", "yeast"]
        species_results = {}

        for sp in targets:
            species_results[sp] = self.mapper.map_pathway(pathway_proteins, sp)

        # Evolutionary tree stability score
        avg_conservation = np.mean([sr["conservation_ratio"] for sr in species_results.values()])

        return {
            "pathway_id": pathway_id,
            "pathway_name": pathway_name,
            "human_size": len(pathway_proteins),
            "species_comparison": species_results,
            "evolutionary_stability_score": round(float(avg_conservation), 3),
            "evolutionary_category": "Ancient Core Metazoan" if avg_conservation >= 0.70 else "Vertebrate-Specific / Rewired"
        }
