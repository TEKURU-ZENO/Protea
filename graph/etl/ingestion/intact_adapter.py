import re
from typing import Optional
from graph.etl.ingestion.canonical_schema import CanonicalInteraction
from graph.entity_resolution.protein_mapper import protein_mapper

class IntactAdapter:
    def parse_line(self, line: str) -> Optional[CanonicalInteraction]:
        """Parses a single row from IntAct MITAB 2.5/2.7 format.
        Format: ID Interactor A | ID Interactor B | Alt ID A | Alt ID B | Alias A | Alias B |
        Interaction Detection Method | First Author | Publication Identifier(s) | Taxid A | Taxid B |
        Interaction Type | Source Database | Interaction Identifier | Confidence Value(s)
        """
        parts = line.strip().split("\t")
        if not parts or parts[0].startswith("#"):
            return None

        if len(parts) < 15:
            return None

        # Extract IDs - format is usually: uniprotkb:P12345
        id_a_raw = parts[0]
        id_b_raw = parts[1]
        
        p1_raw = id_a_raw.split(":")[-1] if ":" in id_a_raw else id_a_raw
        p2_raw = id_b_raw.split(":")[-1] if ":" in id_b_raw else id_b_raw
        
        p1 = protein_mapper.resolve(p1_raw)
        p2 = protein_mapper.resolve(p2_raw)

        # Extract detection method and type
        det_method = parts[6]
        pub_id = parts[8]
        int_type = parts[11]
        
        # Extract confidence score (often format: intact-miscore:0.45)
        conf_raw = parts[14]
        combined = 0.50
        match = re.search(r"intact-miscore:(\d\.\d+)", conf_raw)
        if match:
            combined = float(match.group(1))

        # Classify based on interaction type
        is_physical = "physical" in int_type.lower()
        exp_score = combined if is_physical else 0.20
        comp_score = 0.10 if is_physical else combined

        # Extract publication identifier
        pub = "Unknown"
        pub_match = re.search(r"pubmed:(\d+)", pub_id)
        if pub_match:
            pub = pub_match.group(1)

        return CanonicalInteraction(
            protein_a=p1,
            protein_b=p2,
            combined_score=combined,
            experimental_score=exp_score,
            computational_score=comp_score,
            detection_methods=[det_method],
            source_databases=["IntAct"],
            publications=[pub]
        )
