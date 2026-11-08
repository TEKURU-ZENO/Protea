"""
PROTEA Phase 11: Scientific Leakage Prevention Guard
Enforces strict train/test partitioning by donor, protein family, and species to prevent data leakage.
"""

from __future__ import annotations
from typing import Dict, List, Any, Set


class ScientificLeakageGuard:
    """Enforces non-negotiable data partitioning standards across evolutionary and multi-omics splits."""

    @classmethod
    def audit_partitions(
        cls,
        train_samples: List[Dict[str, Any]],
        test_samples: List[Dict[str, Any]],
        partition_key: str = "donor_id"
    ) -> Dict[str, Any]:
        """
        Audits train and test splits to ensure zero leakage across:
        1. Donors (prevents single-cell cell-level splitting artifacts)
        2. Protein families / Homologs (prevents evolutionary memorization)
        3. Species clades (evaluates genuine generalization)
        """
        train_keys = {s.get(partition_key) for s in train_samples if partition_key in s}
        test_keys = {s.get(partition_key) for s in test_samples if partition_key in s}

        overlap = train_keys.intersection(test_keys)
        has_leakage = len(overlap) > 0

        return {
            "partition_key": partition_key,
            "train_unique_count": len(train_keys),
            "test_unique_count": len(test_keys),
            "overlap_count": len(overlap),
            "overlapping_keys": list(overlap),
            "is_leakage_free": not has_leakage,
            "audit_verdict": "PASSED (Zero Leakage)" if not has_leakage else f"FAILED: Overlap detected on {partition_key}"
        }

    @classmethod
    def audit_family_disjoint_split(
        cls,
        train_genes: List[str],
        test_genes: List[str],
        family_map: Dict[str, str]
    ) -> Dict[str, Any]:
        """Ensures that entire protein families are held out together during evolutionary transfer evaluation."""
        train_fams = {family_map.get(g, f"FAM_{g}") for g in train_genes}
        test_fams = {family_map.get(g, f"FAM_{g}") for g in test_genes}

        shared_fams = train_fams.intersection(test_fams)
        has_leakage = len(shared_fams) > 0

        return {
            "shared_families_count": len(shared_fams),
            "is_family_disjoint": not has_leakage,
            "audit_verdict": "PASSED (Family Disjoint)" if not has_leakage else "FAILED: Homologous family leakage"
        }
