"""State variable exchange and unit conversion across simulation scales."""

import numpy as np


class StateExchangeBridge:
    """Bridges discrete molecular counts, continuous concentrations, and metabolic fluxes."""

    AVOGADRO_CONSTANT = 6.02214076e23  # molecules / mol

    @classmethod
    def concentration_to_counts(
        cls,
        concentration_uM: float,
        cell_volume_liters: float = 1e-15, # 1 fL typical mammalian/bacterial cell
    ) -> int:
        """Convert concentration in uM (micromolar) to discrete copy count."""
        # 1 uM = 1e-6 mol / L
        moles = concentration_uM * 1e-6 * cell_volume_liters
        counts = moles * cls.AVOGADRO_CONSTANT
        return int(max(0, round(counts)))

    @classmethod
    def counts_to_concentration(
        cls,
        molecule_count: int,
        cell_volume_liters: float = 1e-15,
    ) -> float:
        """Convert discrete molecule count to concentration in uM."""
        moles = molecule_count / cls.AVOGADRO_CONSTANT
        conc_M = moles / cell_volume_liters
        return float(conc_M * 1e6)
