"""
PROTEA AI Scientist - Criticism and Adversarial Evaluation Module
Adversarial audits, alternative hypotheses, confounder detection, leakage detection, and falsification.
"""

from ai.ai_scientist.criticism.adversarial_review import AdversarialReviewer
from ai.ai_scientist.criticism.alternative_hypotheses import AlternativeHypothesisEvaluator
from ai.ai_scientist.criticism.confounder_detection import ConfounderDetector
from ai.ai_scientist.criticism.leakage_detection import LeakageDetector
from ai.ai_scientist.criticism.falsification_review import FalsificationReviewer

__all__ = [
    "AdversarialReviewer",
    "AlternativeHypothesisEvaluator",
    "ConfounderDetector",
    "LeakageDetector",
    "FalsificationReviewer",
]
