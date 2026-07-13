from typing import Optional
from graph.etl.ingestion.canonical_schema import CanonicalInteraction
from graph.entity_resolution.protein_mapper import protein_mapper

class BiogridAdapter:
    def parse_line(self, line: str) -> Optional[CanonicalInteraction]:
        """Parses a single row from BioGRID tab-delimited format.
        Format (standard TSV): Entrez Gene Interactor A, Entrez Gene Interactor B, 
        System Type, Experimental System, Author, Publication ID (PubMed), etc.
        """
        parts = line.strip().split("\t")
        if not parts or parts[0].startswith("#") or parts[0] == "INTERACTOR_A":
            return None

        if len(parts) < 14:
            return None

        # Extract interactors
        entrez_a = parts[1]
        entrez_b = parts[2]
        system_type = parts[11] # Physical or Genetic
        system_name = parts[12] # e.g. Two-hybrid, Affinity Capture-MS
        pubmed_id = parts[14]

        # Resolve Entrez IDs to UniProt
        p1 = protein_mapper.resolve(entrez_a)
        p2 = protein_mapper.resolve(entrez_b)

        # Base confidence scores on experimental system type
        is_physical = system_type.lower() == "physical"
        exp_score = 0.85 if is_physical else 0.40
        comp_score = 0.10 if is_physical else 0.75
        combined = 0.90 if is_physical else 0.80

        return CanonicalInteraction(
            protein_a=p1,
            protein_b=p2,
            combined_score=combined,
            experimental_score=exp_score,
            computational_score=comp_score,
            detection_methods=[system_name],
            source_databases=["BioGRID"],
            publications=[pubmed_id]
        )
