from typing import List, Dict, Any, Optional

class CanonicalInteraction:
    def __init__(
        self,
        protein_a: str, # UniProt ID
        protein_b: str, # UniProt ID
        combined_score: float,
        experimental_score: float = 0.0,
        computational_score: float = 0.0,
        literature_score: float = 0.0,
        structural_score: float = 0.0,
        detection_methods: Optional[List[str]] = None,
        source_databases: Optional[List[str]] = None,
        publications: Optional[List[str]] = None,
        organism: str = "9606",
        tissues: Optional[List[str]] = None,
        raw_scores: Optional[Dict[str, float]] = None
    ):
        self.protein_a = protein_a
        self.protein_b = protein_b
        self.combined_score = combined_score
        self.experimental_score = experimental_score
        self.computational_score = computational_score
        self.literature_score = literature_score
        self.structural_score = structural_score
        self.detection_methods = detection_methods or []
        self.source_databases = source_databases or []
        self.publications = publications or []
        self.organism = organism
        self.tissues = tissues or []
        self.raw_scores = raw_scores or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "protein_a": self.protein_a,
            "protein_b": self.protein_b,
            "combined_score": self.combined_score,
            "experimental_score": self.experimental_score,
            "computational_score": self.computational_score,
            "literature_score": self.literature_score,
            "structural_score": self.structural_score,
            "detection_methods": self.detection_methods,
            "source_databases": self.source_databases,
            "publications": self.publications,
            "organism": self.organism,
            "tissues": self.tissues,
            "raw_scores": self.raw_scores
        }
