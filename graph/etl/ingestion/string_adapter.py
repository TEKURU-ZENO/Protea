from typing import List, Optional
from graph.etl.ingestion.canonical_schema import CanonicalInteraction
from graph.entity_resolution.protein_mapper import protein_mapper

class StringAdapter:
    def parse_line(self, line: str) -> Optional[CanonicalInteraction]:
        """Parses a single row from STRING link file.
        Format: protein1 protein2 neighborhood fusion cooccurence coexpression experimental database textmining combined_score
        """
        parts = line.strip().split()
        if not parts or parts[0] == "protein1":
            return None # Header line or empty

        # Ensure correct column count (STRING links usually have 10 or 15 columns)
        if len(parts) < 3:
            return None

        p1_raw = parts[0]
        p2_raw = parts[1]
        
        # Resolve STRING ENSP IDs to UniProt
        p1 = protein_mapper.resolve(p1_raw)
        p2 = protein_mapper.resolve(p2_raw)

        # Normalize score from 0-1000 range to 0.0-1.0 range
        try:
            combined = float(parts[-1]) / 1000.0
            
            # Extract subscores if present (assume standard 10-column links file format)
            # neighborhood, fusion, cooccurence, coexpression, experimental, database, textmining, combined
            exp_score = float(parts[6]) / 1000.0 if len(parts) > 6 else 0.0
            comp_score = float(parts[2]) / 1000.0 if len(parts) > 2 else 0.0 # neighborhood
            lit_score = float(parts[8]) / 1000.0 if len(parts) > 8 else 0.0 # textmining
            
            # Map database source
            db_score = float(parts[7]) / 1000.0 if len(parts) > 7 else 0.0
            
            raw_vals = {
                "neighborhood": float(parts[2]) if len(parts) > 2 else 0.0,
                "fusion": float(parts[3]) if len(parts) > 3 else 0.0,
                "cooccurence": float(parts[4]) if len(parts) > 4 else 0.0,
                "coexpression": float(parts[5]) if len(parts) > 5 else 0.0,
                "experimental": float(parts[6]) if len(parts) > 6 else 0.0,
                "database": float(parts[7]) if len(parts) > 7 else 0.0,
                "textmining": float(parts[8]) if len(parts) > 8 else 0.0
            }
        except ValueError:
            return None

        return CanonicalInteraction(
            protein_a=p1,
            protein_b=p2,
            combined_score=combined,
            experimental_score=exp_score,
            computational_score=comp_score,
            literature_score=lit_score,
            source_databases=["STRING"],
            raw_scores=raw_vals
        )
