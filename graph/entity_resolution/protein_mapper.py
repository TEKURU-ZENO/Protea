from typing import Dict, Optional
from services.api.core.logging import logger

class ProteinMapper:
    def __init__(self):
        # Local lookup table cache for testing/mock mapping
        self._cache: Dict[str, str] = {
            "ENSP00000272298": "P01308", # Insulin Ensembl -> UniProt
            "9606.ENSP00000272298": "P01308",
            "3643": "P01308", # Entrez -> UniProt
            "STRING:9606.ENSP00000272298": "P01308"
        }

    def resolve(self, identifier: str) -> str:
        """Resolves protein identifier to UniProt ID. Falls back to input if unresolved."""
        ident_clean = identifier.strip()
        
        # Check cache
        if ident_clean in self._cache:
            return self._cache[ident_clean]
            
        # Strip prefixes
        if ":" in ident_clean:
            parts = ident_clean.split(":")
            if len(parts) > 1 and parts[1] in self._cache:
                return self._cache[parts[1]]
                
        # Heuristic matching: UniProt IDs are typically 6 or 10 alphanumeric characters
        # e.g., P01308, Q15345
        return ident_clean

    def register_mapping(self, source_id: str, uniprot_id: str):
        self._cache[source_id.strip()] = uniprot_id.strip()

protein_mapper = ProteinMapper()
