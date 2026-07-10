import os
from typing import Dict, Any, Optional
from services.api.core.logging import logger
from services.api.core.config import settings

# Attempt PyTorch/Transformers imports; fall back if running in light test environments
try:
    import torch
    import torch.nn as nn
    from transformers import AutoTokenizer, EsmModel, BertModel
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False
    logger.warning("Torch or Transformers library not found. Falling back to mock model serving.")

class MockModel(nn.Module if HAS_TORCH else object):
    """Fallback mock model that simulates embedding outputs."""
    def __init__(self, embed_dim: int = 1024):
        if HAS_TORCH:
            super().__init__()
            self.linear = nn.Linear(10, embed_dim)
        self.embed_dim = embed_dim

    def __call__(self, input_ids, attention_mask=None, **kwargs):
        if HAS_TORCH:
            # Return mock tensors matching standard output shapes: [batch_size, seq_len, embed_dim]
            batch_size = input_ids.shape[0]
            seq_len = input_ids.shape[1]
            last_hidden_state = torch.randn(batch_size, seq_len, self.embed_dim, device=input_ids.device)
            pooler_output = torch.randn(batch_size, self.embed_dim, device=input_ids.device)
            
            # Mimic HuggingFace BatchEncoding output object
            class HFOutput:
                def __init__(self, lhs, po):
                    self.last_hidden_state = lhs
                    self.pooler_output = po
                def __getitem__(self, key):
                    return getattr(self, key)
            return HFOutput(last_hidden_state, pooler_output)
        else:
            return None

class ModelManager:
    _instance: Optional['ModelManager'] = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ModelManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        
        # Determine device
        self.device = "cpu"
        if HAS_TORCH:
            if torch.cuda.is_available():
                self.device = "cuda"
                logger.info(f"CUDA is available. Servicing models on GPU: {torch.cuda.get_device_name(0)}")
            else:
                logger.info("CUDA not available. Servicing models on CPU.")
        
        # Cache dictionaries
        self.models: Dict[str, Any] = {}
        self.tokenizers: Dict[str, Any] = {}
        self._initialized = True

    def get_model_and_tokenizer(self, model_name: str) -> Tuple[Any, Any]:
        """Loads and returns model and tokenizer. Lazy loaded on first request."""
        model_name = model_name.lower()
        if model_name in self.models:
            return self.models[model_name], self.tokenizers[model_name]

        logger.info(f"Loading protein foundation model: {model_name}...")
        
        if not HAS_TORCH:
            # Fallback to mock immediately
            dim = 1280 if "esm2" in model_name else 1024
            self.models[model_name] = MockModel(embed_dim=dim)
            self.tokenizers[model_name] = None
            return self.models[model_name], self.tokenizers[model_name]

        try:
            if "esm2" in model_name:
                # Load ESM-2 150M or 650M
                hf_name = "facebook/esm2_t30_150M_UR50D"
                tokenizer = AutoTokenizer.from_pretrained(hf_name)
                model = EsmModel.from_pretrained(hf_name)
            elif "protbert" in model_name:
                hf_name = "Rostlab/prot_bert"
                tokenizer = AutoTokenizer.from_pretrained(hf_name)
                model = BertModel.from_pretrained(hf_name)
            else:
                raise ValueError(f"Unknown model request: {model_name}")

            model.to(self.device)
            model.eval()
            self.models[model_name] = model
            self.tokenizers[model_name] = tokenizer
            logger.info(f"Successfully loaded and cached {model_name} on device {self.device}")
            
        except Exception as e:
            logger.warning(f"Error loading model {model_name} ({e}). Falling back to Mock model serving.")
            dim = 1280 if "esm2" in model_name else 1024
            self.models[model_name] = MockModel(embed_dim=dim)
            self.tokenizers[model_name] = None

        return self.models[model_name], self.tokenizers[model_name]

# Helper types alias mapping
Tuple = Any
model_manager = ModelManager()
