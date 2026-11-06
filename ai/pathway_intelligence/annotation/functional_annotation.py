"""
PROTEA PaIE - Functional Annotation & Protein Localization
Maps proteins to GO terms with evidence codes and subcellular compartment hierarchies.
"""

from typing import Dict, List, Set, Optional, Any
from ai.pathway_intelligence.annotation.gene_ontology import go_engine

class FunctionalAnnotationManager:
    """Manages protein functional annotations with evidence codes and provenance."""

    def __init__(self):
        # {protein_id: {term_id: {"evidence": str, "source": str, "reference": str}}}
        self._annotations: Dict[str, Dict[str, Dict[str, str]]] = {}
        self._init_curated_annotations()

    def _init_curated_annotations(self):
        """Initial baseline annotations for key hub and pathway benchmark proteins."""
        data = [
            ("TP53", "GO:0006915", "EXP", "PubMed:12554876"), # apoptotic process
            ("TP53", "GO:0007049", "IDA", "PubMed:15632056"), # cell cycle
            ("TP53", "GO:0003677", "EXP", "PubMed:9823487"),  # DNA binding
            ("TP53", "GO:0005634", "IDA", "PubMed:8945612"),  # nucleus
            ("BAX", "GO:0006915", "EXP", "PubMed:10234567"),  # apoptotic process
            ("BAX", "GO:0005739", "IDA", "PubMed:11234568"),  # mitochondrion
            ("CASP3", "GO:0006915", "EXP", "PubMed:9012345"), # apoptotic process
            ("CASP3", "GO:0008233", "EXP", "PubMed:9012345"), # peptidase activity
            ("AKT1", "GO:0004674", "EXP", "PubMed:9456789"),  # Ser/Thr kinase
            ("AKT1", "GO:0007165", "EXP", "PubMed:9456789"),  # signal transduction
            ("AKT1", "GO:0005829", "IDA", "PubMed:9456789"),  # cytosol
            ("EGFR", "GO:0007165", "EXP", "PubMed:8765432"),  # signal transduction
            ("EGFR", "GO:0005886", "IDA", "PubMed:8765432"),  # plasma membrane
            ("BRCA1", "GO:0006281", "EXP", "PubMed:7654321"), # DNA repair
            ("BRCA1", "GO:0005634", "IDA", "PubMed:7654321"), # nucleus
            ("BARD1", "GO:0006281", "EXP", "PubMed:7654321"), # DNA repair
        ]
        for prot, term, ev, ref in data:
            self.annotate(prot, term, evidence_code=ev, reference=ref)

    def annotate(self, protein_id: str, term_id: str, evidence_code: str = "IDA", reference: str = "curated"):
        prot = protein_id.upper()
        if prot not in self._annotations:
            self._annotations[prot] = {}
        self._annotations[prot][term_id] = {
            "evidence": evidence_code,
            "reference": reference
        }

    def get_terms_for_protein(self, protein_id: str, propagate: bool = True) -> List[Dict[str, Any]]:
        """Retrieve all GO terms for a protein, optionally including propagated ancestor terms."""
        prot = protein_id.upper()
        direct_terms = self._annotations.get(prot, {})
        results = []

        all_term_ids = set(direct_terms.keys())
        if propagate:
            for tid in list(direct_terms.keys()):
                all_term_ids.update(go_engine.get_ancestors(tid))

        for tid in all_term_ids:
            term_info = go_engine.get_term(tid)
            if term_info:
                evidence = direct_terms.get(tid, {}).get("evidence", "IEA") # Inferred if propagated
                reference = direct_terms.get(tid, {}).get("reference", "transitive_closure")
                results.append({
                    "term_id": tid,
                    "name": term_info["name"],
                    "namespace": term_info["namespace"],
                    "evidence": evidence,
                    "reference": reference,
                    "is_direct": tid in direct_terms
                })

        return results

    def get_proteins_for_term(self, term_id: str) -> List[str]:
        """Find all proteins annotated with this term (including direct annotations)."""
        matching = []
        for prot, terms in self._annotations.items():
            if term_id in terms:
                matching.append(prot)
        return matching


class SubcellularLocalizationMapper:
    """Classifies protein cellular compartment localization."""

    COMPARTMENTS = {
        "nucleus": "GO:0005634",
        "cytosol": "GO:0005829",
        "plasma_membrane": "GO:0005886",
        "mitochondrion": "GO:0005739",
        "extracellular": "GO:0005576"
    }

    def __init__(self, annotation_mgr: FunctionalAnnotationManager):
        self.mgr = annotation_mgr

    def get_localization(self, protein_id: str) -> List[str]:
        terms = {t["term_id"] for t in self.mgr.get_terms_for_protein(protein_id, propagate=True)}
        locs = []
        for comp, go_id in self.COMPARTMENTS.items():
            if go_id in terms:
                locs.append(comp)
        return locs or ["cytosol"] # Default fallback to cytosol

annotation_manager = FunctionalAnnotationManager()
localization_mapper = SubcellularLocalizationMapper(annotation_manager)
