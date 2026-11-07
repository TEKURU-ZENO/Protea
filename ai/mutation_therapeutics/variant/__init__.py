"""
PROTEA Variant Intelligence Module
"""

from ai.mutation_therapeutics.variant.parser import VariantParser, AA_3_TO_1, AA_1_TO_3
from ai.mutation_therapeutics.variant.normalizer import VariantNormalizer, CANONICAL_TRANSCRIPTS
from ai.mutation_therapeutics.variant.annotator import VariantAnnotator, CURATED_VARIANT_DB

__all__ = [
    "VariantParser",
    "AA_3_TO_1",
    "AA_1_TO_3",
    "VariantNormalizer",
    "CANONICAL_TRANSCRIPTS",
    "VariantAnnotator",
    "CURATED_VARIANT_DB"
]
