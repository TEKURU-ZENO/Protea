import re
from typing import List, Dict, Union, Tuple

class ProteinTokenizer:
    # Standard 20 amino acids
    AMINO_ACIDS = "ACDEFGHIKLMNPQRSTVWY"
    
    def __init__(self, max_length: int = 1024, padding_value: int = 0):
        self.max_length = max_length
        self.padding_value = padding_value
        
        # Build token mapping: pad=0, unk=1, start=2, stop=3, standard residues starting from 4
        self.char_to_id: Dict[str, int] = {"<pad>": 0, "<unk>": 1, "<cls>": 2, "<eos>": 3}
        for idx, aa in enumerate(self.AMINO_ACIDS):
            self.char_to_id[aa] = idx + 4
            
        self.id_to_char: Dict[int, str] = {v: k for k, v in self.char_to_id.items()}

    def clean_sequence(self, sequence: str) -> str:
        """Strips whitespaces, converts to uppercase, and removes non-standard chars."""
        cleaned = re.sub(r"\s+", "", sequence).upper()
        # Filter out anything not in standard 20 residues
        cleaned = "".join([c for c in cleaned if c in self.AMINO_ACIDS])
        return cleaned

    def validate_sequence(self, sequence: str) -> Tuple[bool, str]:
        """Validates if sequence contains only standard amino acids."""
        cleaned = re.sub(r"\s+", "", sequence).upper()
        invalid_chars = [c for c in cleaned if c not in self.AMINO_ACIDS]
        if invalid_chars:
            return False, f"Contains non-standard characters: {set(invalid_chars)}"
        if len(cleaned) == 0:
            return False, "Sequence is empty."
        return True, ""

    def tokenize(self, sequence: str, add_special_tokens: bool = True) -> List[int]:
        """Encodes clean sequence into integer token list."""
        cleaned = self.clean_sequence(sequence)
        # Truncate
        if len(cleaned) > self.max_length:
            cleaned = cleaned[:self.max_length]
            
        tokens = [self.char_to_id.get(aa, 1) for aa in cleaned]
        if add_special_tokens:
            tokens = [self.char_to_id["<cls>"]] + tokens + [self.char_to_id["<eos>"]]
        return tokens

    def pad_sequence(self, tokens: List[int], target_len: int) -> List[int]:
        """Pads token list to target length."""
        if len(tokens) >= target_len:
            return tokens[:target_len]
        return tokens + [self.padding_value] * (target_len - len(tokens))

    def create_batch(self, sequences: List[str], add_special_tokens: bool = True) -> Tuple[List[List[int]], List[List[int]]]:
        """Tokenizes, pads, and returns batch of token ids and attention masks."""
        tokenized_batch = []
        max_batch_len = 0
        
        for seq in sequences:
            tokens = self.tokenize(seq, add_special_tokens)
            tokenized_batch.append(tokens)
            max_batch_len = max(max_batch_len, len(tokens))
            
        padded_batch = []
        attention_masks = []
        
        for tokens in tokenized_batch:
            mask = [1] * len(tokens) + [0] * (max_batch_len - len(tokens))
            padded = self.pad_sequence(tokens, max_batch_len)
            padded_batch.append(padded)
            attention_masks.append(mask)
            
        return padded_batch, attention_masks
