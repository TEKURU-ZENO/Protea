"""Coupled transcription and translation two-stage gene expression dynamics."""

from dataclasses import dataclass
from typing import Dict, Tuple
import numpy as np


@dataclass
class GeneExpressionParameters:
    """Biophysical rates governing gene expression."""
    alpha_m: float = 0.5       # mRNA synthesis rate (uM / s)
    delta_m: float = 0.05      # mRNA degradation rate (s^-1), t1/2 ~ 14s
    alpha_p: float = 0.2       # Protein translation rate per mRNA (s^-1)
    delta_p: float = 0.01      # Protein degradation rate (s^-1), t1/2 ~ 70s
    basal_transcription: float = 0.01


class TwoStageGeneExpression:
    """Simulates coupled mRNA transcription and protein translation."""

    def __init__(self, params: GeneExpressionParameters):
        self.params = params

    def derivatives(self, mrna: float, protein: float, promoter_activity: float) -> Tuple[float, float]:
        """Compute d[mRNA]/dt and d[Protein]/dt given current promoter activity."""
        # dmRNA/dt = alpha_m * promoter - delta_m * mRNA
        dmrna_dt = self.params.alpha_m * promoter_activity - self.params.delta_m * mrna
        # dProtein/dt = alpha_p * mRNA - delta_p * Protein
        dprotein_dt = self.params.alpha_p * mrna - self.params.delta_p * protein
        return dmrna_dt, dprotein_dt

    def steady_state(self, promoter_activity: float) -> Tuple[float, float]:
        """Analytical steady-state concentrations for mRNA and Protein."""
        mrna_ss = (self.params.alpha_m * promoter_activity) / max(1e-9, self.params.delta_m)
        protein_ss = (self.params.alpha_p * mrna_ss) / max(1e-9, self.params.delta_p)
        return mrna_ss, protein_ss
