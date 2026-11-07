"""
PROTEA Phase 10: Mutant Modeler
Constructs branched mutant protein instances following the Branching Principle.
Never overwrites reference baseline proteins.
"""

from __future__ import annotations
import uuid
from typing import List, Dict, Any, Optional
from ai.mutation_therapeutics.schema import MutantProtein, ProteinMutation, MutationType


class MutantModeler:
    """Builds mutated protein models with isolated, versioned branches."""

    @classmethod
    def generate_mutant_protein(
        cls,
        gene_symbol: str,
        wildtype_sequence: str,
        mutations: List[ProteinMutation],
        base_protein_id: Optional[str] = None
    ) -> MutantProtein:
        """
        Substitutes mutant residues into the wildtype sequence and generates
        a branched, versioned mutant protein object.
        """
        pid = base_protein_id or f"PROT_{gene_symbol.upper()}"
        seq_chars = list(wildtype_sequence)

        labels: List[str] = []
        for mut in mutations:
            pos = mut.position
            # 1-based indexing check
            if 1 <= pos <= len(seq_chars):
                seq_chars[pos - 1] = mut.mutant_aa
            labels.append(f"{mut.wildtype_aa}{mut.position}{mut.mutant_aa}")

        mutation_label = f"{gene_symbol.upper()}_{'_'.join(labels) if labels else 'WT'}"
        mutated_seq = "".join(seq_chars)
        branch_id = f"mut_branch_{uuid.uuid4().hex[:8]}"

        return MutantProtein(
            protein_id=f"{pid}_{mutation_label}",
            wildtype_protein_id=pid,
            mutation_label=mutation_label,
            mutated_sequence=mutated_seq,
            wildtype_sequence=wildtype_sequence,
            mutations=mutations,
            branch_id=branch_id,
            version="1.0-mutant"
        )
