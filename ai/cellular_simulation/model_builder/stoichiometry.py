"""Stoichiometric matrix constructor and conservation law analyzer."""

from __future__ import annotations

from typing import Any, Dict, List, Tuple
import numpy as np
from ai.cellular_simulation.schema import Reaction, Species


class StoichiometryBuilder:
    """Constructs stoichiometric matrices S and verifies reaction mass balances."""

    @staticmethod
    def build_stoichiometric_matrix(
        species_list: List[str],
        reactions: List[Reaction]
    ) -> List[List[float]]:
        """Constructs an m x n stoichiometric matrix where S[i, j] = net change of species i in reaction j."""
        species_idx = {s: i for i, s in enumerate(species_list)}
        m = len(species_list)
        n = len(reactions)

        S = [[0.0 for _ in range(n)] for _ in range(m)]

        for j, rx in enumerate(reactions):
            # Reactants are consumed (negative coefficient)
            for r_id, coeff in rx.reactants.items():
                if r_id in species_idx:
                    i = species_idx[r_id]
                    S[i][j] -= coeff

            # Products are produced (positive coefficient)
            for p_id, coeff in rx.products.items():
                if p_id in species_idx:
                    i = species_idx[p_id]
                    S[i][j] += coeff

        return S

    @staticmethod
    def compute_conservation_laws(S_matrix: List[List[float]]) -> List[List[float]]:
        """Identifies left nullspace vectors L where L * S = 0 (conserved moieties)."""
        S = np.array(S_matrix)
        if S.size == 0:
            return []

        # SVD of S.T: S^T * L^T = 0
        U, s, Vh = np.linalg.svd(S.T)
        tol = 1e-10
        null_indices = np.where(np.abs(s) < tol)[0]

        # Conserved moiety vectors
        conserved_vectors: List[List[float]] = []
        # If rank < m (number of species), there are conservation relationships
        rank = np.linalg.matrix_rank(S)
        m = S.shape[0]
        if rank < m:
            null_space = Vh[rank:, :]
            for row in null_space:
                conserved_vectors.append([round(float(x), 4) for x in row])

        return conserved_vectors

    @classmethod
    def build_matrix(cls, model: Any) -> Tuple[np.ndarray, List[str], List[str]]:
        """Convenience method returning (S_np_matrix, species_ids, reaction_ids)."""
        species_ids = list(model.species.keys())
        reaction_ids = [r.reaction_id for r in model.reactions]
        S_list = cls.build_stoichiometric_matrix(species_ids, model.reactions)
        S_np = np.array(S_list, dtype=float) if S_list else np.zeros((len(species_ids), len(reaction_ids)), dtype=float)
        return S_np, species_ids, reaction_ids

    @classmethod
    def find_conservation_laws(cls, S_matrix: Any) -> np.ndarray:
        """Convenience method returning conservation laws as 2D numpy array."""
        if isinstance(S_matrix, np.ndarray):
            S_list = S_matrix.tolist()
        else:
            S_list = S_matrix
        laws = cls.compute_conservation_laws(S_list)
        return np.array(laws, dtype=float) if laws else np.empty((0, len(S_list) if S_list else 0))

