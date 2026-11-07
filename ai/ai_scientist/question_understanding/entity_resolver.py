"""Biological entity resolution to canonical UniProt, NCBI, and Disease Ontology IDs."""

from typing import Any, Dict, List, Union


class EntityResolver:
    """Resolves natural language biological entities into canonical identifiers."""

    CANONICAL_ENTITIES = {
        "braf": {"id": "UniProtKB:P15056", "canonical_id": "P15056", "name": "BRAF", "type": "Protein", "organism": "NCBI:9606"},
        "mek": {"id": "UniProtKB:Q02750", "canonical_id": "Q02750", "name": "MAP2K1", "type": "Protein", "organism": "NCBI:9606"},
        "mek1": {"id": "UniProtKB:Q02750", "canonical_id": "Q02750", "name": "MAP2K1", "type": "Protein", "organism": "NCBI:9606"},
        "map2k1": {"id": "UniProtKB:Q02750", "canonical_id": "Q02750", "name": "MAP2K1", "type": "Protein", "organism": "NCBI:9606"},
        "erk": {"id": "UniProtKB:P27361", "canonical_id": "P27361", "name": "MAPK3", "type": "Protein", "organism": "NCBI:9606"},
        "erk2": {"id": "UniProtKB:P28482", "canonical_id": "P28482", "name": "MAPK1", "type": "Protein", "organism": "NCBI:9606"},
        "egfr": {"id": "UniProtKB:P00533", "canonical_id": "P00533", "name": "EGFR", "type": "Protein", "organism": "NCBI:9606"},
        "stat3": {"id": "UniProtKB:P40763", "canonical_id": "P40763", "name": "STAT3", "type": "Protein", "organism": "NCBI:9606"},
        "tp53": {"id": "UniProtKB:P04637", "canonical_id": "P04637", "name": "TP53", "type": "Protein", "organism": "NCBI:9606"},
        "ras": {"id": "UniProtKB:P01112", "canonical_id": "P01112", "name": "HRAS", "type": "Protein", "organism": "NCBI:9606"},
        "melanoma": {"id": "DOID:1909", "canonical_id": "DOID:1909", "name": "Melanoma", "type": "Disease", "tissue": "skin"},
        "liver": {"id": "UBERON:0002107", "canonical_id": "UBERON:0002107", "name": "Liver", "type": "Tissue"},
        "hepatocyte": {"id": "CL:0000182", "canonical_id": "CL:0000182", "name": "Hepatocyte", "type": "CellType"},
    }

    @classmethod
    def resolve_entities(cls, text_or_list: Union[str, List[str]]) -> List[Dict[str, Any]]:
        """Extract and resolve recognized biological entities from text or string list."""
        if isinstance(text_or_list, list):
            words = [w.lower() for w in text_or_list]
        else:
            words = text_or_list.lower().replace(",", " ").replace(".", " ").replace("?", " ").split()

        resolved = []
        seen_ids = set()
        for w in words:
            clean_w = w.strip()
            if clean_w in cls.CANONICAL_ENTITIES:
                entry = cls.CANONICAL_ENTITIES[clean_w]
                if entry["id"] not in seen_ids:
                    seen_ids.add(entry["id"])
                    resolved.append(dict(entry))

        return resolved


BiologicalEntityResolver = EntityResolver
