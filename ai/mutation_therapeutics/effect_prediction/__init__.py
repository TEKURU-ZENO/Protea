"""
PROTEA Effect Prediction Module
"""

from ai.mutation_therapeutics.effect_prediction.missense_scorer import MissenseScorer, BLOSUM62, GRANTHAM_DISTANCES
from ai.mutation_therapeutics.effect_prediction.domain_disruption import DomainDisruptionAnalyzer, DOMAIN_REGISTRIES
from ai.mutation_therapeutics.effect_prediction.functional_classifier import FunctionalClassifier, KNOWN_GOF_SIGNATURES
from ai.mutation_therapeutics.effect_prediction.ensemble import EnsembleEffectPredictor

__all__ = [
    "MissenseScorer",
    "BLOSUM62",
    "GRANTHAM_DISTANCES",
    "DomainDisruptionAnalyzer",
    "DOMAIN_REGISTRIES",
    "FunctionalClassifier",
    "KNOWN_GOF_SIGNATURES",
    "EnsembleEffectPredictor"
]
