import numpy as np
from typing import Dict, Any
from ai.protein_foundation.fusion.registry import BaseFusionStrategy, fusion_registry

class WeightedSumFusion(BaseFusionStrategy):
    def __init__(self, sequence_weight: float = 0.7, structure_weight: float = 0.3):
        self.w_seq_param = sequence_weight
        self.w_struct_param = structure_weight

    def fuse(self, sequence_emb: np.ndarray, structure_features: Dict[str, Any]) -> np.ndarray:
        seq_len, seq_dim = sequence_emb.shape
        
        # Project sequence embedding to 1024
        W_seq = np.random.randn(seq_dim, 1024).astype(np.float32) * 0.01
        projected_seq = np.dot(sequence_emb, W_seq)
        
        # Prepare structure features matrix [seq_len, 5]
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
        
        # Project structure features to 1024
        W_struct = np.random.randn(5, 1024).astype(np.float32) * 0.01
        projected_struct = np.dot(struct_feat_arr, W_struct)
        
        # Dynamic weighted sum
        denom = self.w_seq_param + self.w_struct_param
        w_seq = self.w_seq_param / denom
        w_struct = self.w_struct_param / denom
        
        return w_seq * projected_seq + w_struct * projected_struct

fusion_registry.register("weighted_sum", WeightedSumFusion())
