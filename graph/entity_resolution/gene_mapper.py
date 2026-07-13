from typing import Dict, Optional

class GeneMapper:
    def __init__(self):
        self._cache: Dict[str, str] = {
            "HGNC:6081": "INS", # Insulin HGNC -> Symbol
            "ENSG00000254647": "INS",
            "NCBI:3643": "INS"
        }

    def resolve(self, identifier: str) -> str:
        """Resolves gene identifier to canonical symbol."""
        ident_clean = identifier.strip()
        if ident_clean in self._cache:
            return self._cache[ident_clean]
        return ident_clean

    def register_mapping(self, source_id: str, symbol: str):
        self._cache[source_id.strip()] = symbol.strip()

gene_mapper = GeneMapper()
