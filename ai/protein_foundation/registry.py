import numpy as np
from typing import Dict, Any, Optional
from ai.protein_foundation.model_manager import model_manager, HAS_TORCH

if HAS_TORCH:
    import torch

class BaseProteinModel:
    def embed(self, sequence: str) -> Dict[str, np.ndarray]:
        """Calculates embeddings and returns numpy arrays."""
        raise NotImplementedError()

class ESM2Adapter(BaseProteinModel):
    def embed(self, sequence: str) -> Dict[str, np.ndarray]:
        model, tokenizer = model_manager.get_model_and_tokenizer("esm2")
        
        # If tokenizer is None, we are running in mock fallback mode
        if not tokenizer or not HAS_TORCH:
            # Generate mock embeddings: ESM-2 t30 has 1280 dimensions
            seq_len = len(sequence)
            per_residue = np.random.randn(seq_len, 1280).astype(np.float32)
            pooled = np.mean(per_residue, axis=0)
            return {"per_residue": per_residue, "pooled": pooled}

        inputs = tokenizer(sequence, return_tensors="pt")
        # Place on matching device
        inputs = {k: v.to(model_manager.device) for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = model(**inputs)
            # Remove special start/stop tokens for per-residue embeddings
            # HuggingFace tokenization adds <cls> at start, <eos> at end
            last_hidden = outputs.last_hidden_state[0].cpu().numpy()
            if last_hidden.shape[0] > len(sequence):
                last_hidden = last_hidden[1 : len(sequence) + 1]
                
            pooled = outputs.pooler_output[0].cpu().numpy()
            # If pooler output is missing/empty, take mean
            if pooled is None or len(pooled) == 0:
                pooled = np.mean(last_hidden, axis=0)
                
        return {"per_residue": last_hidden, "pooled": pooled}

class ProtBERTAdapter(BaseProteinModel):
    def embed(self, sequence: str) -> Dict[str, np.ndarray]:
        model, tokenizer = model_manager.get_model_and_tokenizer("protbert")
        
        if not tokenizer or not HAS_TORCH:
            # ProtBERT has 1024 dimensions
            seq_len = len(sequence)
            per_residue = np.random.randn(seq_len, 1024).astype(np.float32)
            pooled = np.mean(per_residue, axis=0)
            return {"per_residue": per_residue, "pooled": pooled}

        # Spaces between residues are required for ProtBERT tokenizer
        spaced_sequence = " ".join(list(sequence))
        inputs = tokenizer(spaced_sequence, return_tensors="pt")
        inputs = {k: v.to(model_manager.device) for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = model(**inputs)
            last_hidden = outputs.last_hidden_state[0].cpu().numpy()
            # Crop padding/special tokens
            if last_hidden.shape[0] > len(sequence):
                last_hidden = last_hidden[1 : len(sequence) + 1]
            pooled = np.mean(last_hidden, axis=0)
            
        return {"per_residue": last_hidden, "pooled": pooled}

class EmbeddingRegistry:
    def __init__(self):
        self._registry: Dict[str, BaseProteinModel] = {
            "esm2": ESM2Adapter(),
            "protbert": ProtBERTAdapter()
        }

    def get(self, name: str) -> BaseProteinModel:
        name = name.lower()
        if name not in self._registry:
            raise KeyError(f"Embedding model '{name}' is not registered in PROTEA.")
        return self._registry[name]

    def register(self, name: str, adapter: BaseProteinModel):
        self._registry[name.lower()] = adapter

registry = EmbeddingRegistry()
