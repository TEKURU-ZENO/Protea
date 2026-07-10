import re
from typing import List, Dict, Any, Tuple
from ai.protein_foundation.protein_tokenizer import ProteinTokenizer

class FastaParser:
    def __init__(self, max_length: int = 1024):
        self.tokenizer = ProteinTokenizer(max_length=max_length)

    def parse_string(self, fasta_content: str) -> List[Dict[str, Any]]:
        """Parses FASTA format string content and returns structured sequence objects."""
        lines = fasta_content.strip().split("\n")
        parsed_entries = []
        current_header = None
        current_seq_parts = []
        
        # Helper to push parsed entry
        def push_current():
            if current_header and current_seq_parts:
                seq = "".join(current_seq_parts)
                # Parse header
                header_info = self._parse_header(current_header)
                
                # Validate
                is_valid, err_msg = self.tokenizer.validate_sequence(seq)
                cleaned_seq = self.tokenizer.clean_sequence(seq)
                
                parsed_entries.append({
                    "id": header_info["uniprot_id"],
                    "name": header_info["name"],
                    "description": header_info["description"],
                    "organism": header_info["organism"],
                    "gene": header_info["gene"],
                    "sequence": cleaned_seq,
                    "length": len(cleaned_seq),
                    "is_valid": is_valid,
                    "validation_error": err_msg
                })

        for line in lines:
            line = line.strip()
            if not line:
                continue
            if line.startswith(">"):
                push_current()
                current_header = line[1:]
                current_seq_parts = []
            else:
                current_seq_parts.append(line)
        
        # Push last entry
        push_current()
        
        # Deduplicate by sequence
        seen_seqs = set()
        deduplicated = []
        for entry in parsed_entries:
            if entry["sequence"] not in seen_seqs:
                seen_seqs.add(entry["sequence"])
                deduplicated.append(entry)
                
        return deduplicated

    def _parse_header(self, header: str) -> Dict[str, str]:
        """Extracts fields from standard UniProt headers or fallback headers.
        Example: db|UniprotID|EntryName Description OS=Organism GN=GeneName
        """
        parts = header.split(maxsplit=1)
        db_id = parts[0]
        desc_part = parts[1] if len(parts) > 1 else ""
        
        # Parse db_id: sp|Q15345|BARD1_HUMAN
        uniprot_id = db_id
        name = db_id
        if "|" in db_id:
            subparts = db_id.split("|")
            if len(subparts) >= 3:
                uniprot_id = subparts[1]
                name = subparts[2]
            elif len(subparts) == 2:
                uniprot_id = subparts[0]
                name = subparts[1]
                
        # Parse organism and gene
        organism = "Unknown"
        gene = "Unknown"
        
        os_match = re.search(r"OS=([^=]+)(?: GN=|$)", desc_part)
        if os_match:
            organism = os_match.group(1).split("GN=")[0].strip()
            
        gn_match = re.search(r"GN=([^= ]+)", desc_part)
        if gn_match:
            gene = gn_match.group(1).strip()
            
        # Clean description
        description = desc_part
        for tag in ["OS=", "GN=", "PE=", "SV="]:
            if tag in description:
                description = description.split(tag)[0].strip()
                
        return {
            "uniprot_id": uniprot_id,
            "name": name,
            "description": description or name,
            "organism": organism,
            "gene": gene
        }
