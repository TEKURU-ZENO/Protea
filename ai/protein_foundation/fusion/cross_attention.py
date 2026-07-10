import numpy as np
from typing import Dict, Any
from ai.protein_foundation.fusion.registry import BaseFusionStrategy, fusion_registry
from ai.protein_foundation.model_manager import HAS_TORCH

if HAS_TORCH:
    import torch
    import torch.nn as nn

class CrossAttentionPyTorch(nn.Module if HAS_TORCH else object):
    def __init__(self, seq_dim: int = 1280, struct_dim: int = 128, output_dim: int = 1024):
        if HAS_TORCH:
            super().__init__()
            # Project structural features (1-hot secondary structure, accessibility, flexibility)
            # Secondary structure has 3 classes: H, E, C
            # We map 3 (1-hot) + 1 (accessibility) + 1 (flexibility) = 5 features to struct_dim
            self.struct_proj = nn.Linear(5, struct_dim)
            
            # Cross attention: sequence queries, structure keys/values
            self.attn = nn.MultiheadAttention(embed_dim=output_dim, num_heads=4, batch_first=True)
            
            # Projections to output_dim
            self.seq_proj = nn.Linear(seq_dim, output_dim)
            self.struct_to_output = nn.Linear(struct_dim, output_dim)
            
            self.out_proj = nn.Linear(output_dim, output_dim)

    def forward(self, seq_emb_t: Any, struct_feat_t: Any) -> Any:
        # Project dimensions
        q = self.seq_proj(seq_emb_t) # [1, seq_len, output_dim]
        
        struct_emb = self.struct_proj(struct_feat_t) # [1, seq_len, struct_dim]
        k = self.struct_to_output(struct_emb) # [1, seq_len, output_dim]
        v = k
        
        # Run cross-attention
        attn_out, _ = self.attn(q, k, v)
        # Residual connection and project
        output = self.out_proj(q + attn_out)
        return output

class CrossAttentionFusion(BaseFusionStrategy):
    def __init__(self):
        self.model: Optional[CrossAttentionPyTorch] = None

    def fuse(self, sequence_emb: np.ndarray, structure_features: Dict[str, Any]) -> np.ndarray:
        seq_len, seq_dim = sequence_emb.shape
        
        # Prepare structure features matrix [seq_len, 5]
        # features: 1-hot secondary structure (H, E, C), solvent accessibility, flexibility
        sec_struct = structure_features.get("secondary_structure", ["C"] * seq_len)
        accessibility = structure_features.get("solvent_accessibility", [0.5] * seq_len)
        flexibility = structure_features.get("flexibility", [False] * seq_len)
        
        feat_matrix = []
        for i in range(seq_len):
            ss = sec_struct[i] if i < len(sec_struct) else "C"
            ss_onehot = [1.0, 0.0, 0.0] if ss == "H" else [0.0, 1.0, 0.0] if ss == "E" else [0.0, 0.0, 1.0]
            acc = accessibility[i] if i < len(accessibility) else 0.5
            flex = 1.0 if (i < len(flexibility) and flexibility[i]) else 0.0
            feat_matrix.append(ss_onehot + [acc, flex])
            
        struct_feat_arr = np.array(feat_matrix, dtype=np.float32)

        if HAS_TORCH:
            if self.model is None:
                self.model = CrossAttentionPyTorch(seq_dim=seq_dim, output_dim=1024)
            
            # Run model forward
            self.model.eval()
            with torch.no_grad():
                seq_t = torch.from_numpy(sequence_emb).unsqueeze(0).float()
                struct_t = torch.from_numpy(struct_feat_arr).unsqueeze(0).float()
                out_t = self.model(seq_t, struct_t)
                return out_t.squeeze(0).numpy()
        else:
            # Fallback pure-numpy attention simulation
            # Project sequence directly to 1024
            W_seq = np.random.randn(seq_dim, 1024).astype(np.float32) * 0.01
            q = np.dot(sequence_emb, W_seq) # [seq_len, 1024]
            
            # Project structure to 1024
            W_struct = np.random.randn(5, 1024).astype(np.float32) * 0.01
            k = np.dot(struct_feat_arr, W_struct) # [seq_len, 1024]
            v = k
            
            # Scaled Dot-Product Attention: Softmax(Q K^T / sqrt(d)) V
            scores = np.dot(q, k.T) / np.sqrt(1024)
            # stable softmax
            exp_scores = np.exp(scores - np.max(scores, axis=-1, keepdims=True))
            attn_weights = exp_scores / np.sum(exp_scores, axis=-1, keepdims=True)
            
            context = np.dot(attn_weights, v)
            # Output projection with residual
            fused = q + context
            return fused

# Register the strategy
Optional = Any
fusion_registry.register("cross_attention", CrossAttentionFusion())
