"""Continuous Hill-type transcriptional response models."""

from typing import Dict, List, Optional
import numpy as np


class HillTranscriptionalKinetics:
    """Computes transcriptional promoter activities based on cooperative transcription factor binding."""

    @staticmethod
    def activation(tf_conc: float, Ka: float = 1.0, n: float = 2.0) -> float:
        """Cooperative transcriptional activation: A^n / (Ka^n + A^n)."""
        if tf_conc <= 0:
            return 0.0
        val = (tf_conc / Ka) ** n
        return float(val / (1.0 + val))

    @staticmethod
    def repression(tf_conc: float, Kr: float = 1.0, n: float = 2.0) -> float:
        """Cooperative transcriptional repression: 1 / (1 + (R/Kr)^n)."""
        if tf_conc <= 0:
            return 1.0
        val = (tf_conc / Kr) ** n
        return float(1.0 / (1.0 + val))

    @staticmethod
    def combinatorial(
        activators: List[tuple[float, float, float]], # list of (conc, Ka, n)
        repressors: List[tuple[float, float, float]], # list of (conc, Kr, n)
        logic: str = "AND",
        basal_rate: float = 0.01,
        max_rate: float = 1.0,
    ) -> float:
        """Evaluate combinatorial promoter activity combining multiple regulators."""
        act_term = 1.0
        if activators:
            if logic == "AND":
                act_term = 1.0
                for conc, ka, n in activators:
                    act_term *= HillTranscriptionalKinetics.activation(conc, ka, n)
            else: # OR
                prob_none = 1.0
                for conc, ka, n in activators:
                    prob_none *= (1.0 - HillTranscriptionalKinetics.activation(conc, ka, n))
                act_term = 1.0 - prob_none

        rep_term = 1.0
        for conc, kr, n in repressors:
            rep_term *= HillTranscriptionalKinetics.repression(conc, kr, n)

        promoter_activity = basal_rate + (max_rate - basal_rate) * act_term * rep_term
        return float(promoter_activity)
