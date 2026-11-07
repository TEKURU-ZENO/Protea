"""
PROTEA BRE - Biological Entity Resolution
Resolves proteins, genes, diseases, tissues, and organisms with synonym mapping and ambiguity preservation.
"""

from typing import Dict, List, Optional, Any, Tuple
import re

class BiologicalEntityResolver:
    """Normalizes biological terms, extracts contextual entities, and flags ambiguities."""

    def __init__(self):
        # Curated synonym dictionary: {normalized_symbol: [synonyms]}
        self._protein_synonyms: Dict[str, List[str]] = {
            "TP53": ["p53", "tumor protein p53", "LFS1", "TRP53"],
            "AKT1": ["akt", "protein kinase b", "pkb", "pkb-alpha", "rac-alpha"],
            "EGFR": ["erbb1", "her1", "epidermal growth factor receptor"],
            "MDM2": ["hdm2", "double minute 2 protein"],
            "BRCA1": ["breast cancer type 1 susceptibility protein", "rnf53"],
            "PTEN": ["phosphatase and tensin homolog", "mmac1", "tep1"],
            "KRAS": ["k-ras", "c-k-ras", "kras2", "rask2"],
            "MAPK1": ["erk2", "p42mapk", "erk-2", "mitogen-activated protein kinase 1"],
            "CASP3": ["caspase-3", "cpp32", "apopain"],
            "BAX": ["bcl-2-associated x protein", "bcl2l4"]
        }

        self._tissues: List[str] = [
            "liver", "brain", "lung", "kidney", "heart", "breast", "colon", "pancreas",
            "prostate", "ovary", "blood", "spleen", "bone marrow", "muscle"
        ]

        self._diseases: Dict[str, str] = {
            "cancer": "Hepatocellular carcinoma / General malignancy",
            "carcinoma": "Carcinoma",
            "alzheimer": "Alzheimer's Disease",
            "parkinson": "Parkinson's Disease",
            "diabetes": "Type 2 Diabetes",
            "hypoxia": "Ischemic Hypoxia",
            "fibrosis": "Organ Fibrosis"
        }

    def resolve_protein(self, term: str) -> Tuple[Optional[str], List[str]]:
        """Resolve protein name/synonym to canonical HGNC symbol, reporting ambiguities if multiple exist."""
        clean = term.strip().upper()
        if clean in self._protein_synonyms:
            return clean, []

        matches = []
        term_lower = term.strip().lower()
        for canonical, syns in self._protein_synonyms.items():
            if term_lower == canonical.lower() or any(term_lower == s.lower() for s in syns):
                matches.append(canonical)

        if len(matches) == 1:
            return matches[0], []
        elif len(matches) > 1:
            return matches[0], matches # Ambiguity preserved
        return None, []

    def extract_context(self, text: str) -> Dict[str, Any]:
        """Extract tissue, condition, observation state, and organism from question text."""
        text_lower = text.lower()
        context = {
            "tissue": None,
            "condition": "disease",
            "observation": None,
            "organism": "Homo sapiens"
        }

        # Tissue extraction
        for t in self._tissues:
            if re.search(r'\b' + re.escape(t) + r'\b', text_lower):
                context["tissue"] = t
                break

        # Observation state
        if any(w in text_lower for w in ["downregulated", "decreased", "suppressed", "reduced", "lowered", "loss"]):
            context["observation"] = "downregulated"
        elif any(w in text_lower for w in ["upregulated", "increased", "elevated", "activated", "overexpressed"]):
            context["observation"] = "upregulated"
        elif any(w in text_lower for w in ["mutated", "mutation", "variant"]):
            context["observation"] = "mutated"
        else:
            context["observation"] = "altered"

        # Disease / Condition extraction
        for d_key, d_name in self._diseases.items():
            if d_key in text_lower:
                context["condition"] = d_name
                break

        return context
