"""Core data schemas, typed structures, and interfaces for the Cellular Simulation Engine (CSE)."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional


class ModelType(str, Enum):
    """Categorical mathematical representation of the biological model."""
    ODE = "ODE"                    # Deterministic continuous ordinary differential equations
    STOCHASTIC = "STOCHASTIC"      # Discrete molecule Gillespie SSA / tau-leaping
    REGULATORY = "REGULATORY"      # Gene regulatory network (Boolean / continuous Hill)
    METABOLIC = "METABOLIC"        # Stoichiometric constraint-based Flux Balance Analysis (FBA)
    HYBRID = "HYBRID"              # Coupled multiscale simulation (e.g. signaling + gene regulation)


class RateLawType(str, Enum):
    """Kinetic rate law mechanisms."""
    MASS_ACTION = "MASS_ACTION"                  # Mass-action: v = k * [A]^a * [B]^b
    MICHAELIS_MENTEN = "MICHAELIS_MENTEN"        # Enzyme kinetics: v = (Vmax * [S]) / (Km + [S])
    HILL_ACTIVATION = "HILL_ACTIVATION"          # Cooperative activation: v = (Vmax * [A]^n) / (Ka^n + [A]^n)
    HILL_INHIBITION = "HILL_INHIBITION"          # Cooperative repression: v = Vmax / (1 + ([I]/Ki)^n)
    ZERO_ORDER = "ZERO_ORDER"                    # Constant flux: v = k0
    CUSTOM = "CUSTOM"                            # Arbitrary algebraic expression


class InterventionType(str, Enum):
    """Types of in silico experiments executable on the model."""
    KNOCKOUT = "KNOCKOUT"              # Complete -100% loss-of-function
    KNOCKDOWN = "KNOCKDOWN"            # -50% to -80% expression reduction
    OVEREXPRESSION = "OVEREXPRESSION"  # Increased synthesis / production
    INHIBITION = "INHIBITION"          # Chemical / ligand-induced inhibition
    ACTIVATION = "ACTIVATION"          # Chemical agonist stimulation
    DOSE_RESPONSE = "DOSE_RESPONSE"    # Multi-concentration titrations (EC50/IC50)
    WASHOUT = "WASHOUT"                # Reversible intervention followed by recovery
    MUTATION = "MUTATION"              # Kinetic parameter alteration


class ParameterProvenance(str, Enum):
    """Provenance origin of kinetic parameter values."""
    EXPERIMENTAL = "EXPERIMENTAL"      # Empirically measured in matched wet-lab assay
    CALIBRATED = "CALIBRATED"          # Numerically estimated via parameter optimization
    LITERATURE = "LITERATURE"          # Curated from literature or BioModels repository
    ASSUMED = "ASSUMED"                # Heuristic or biophysically plausible default


@dataclass
class Species:
    """Molecular species or state variable in the simulation."""
    species_id: str
    name: str
    compartment: str = "cytosol"
    initial_amount: float = 0.0        # Concentration (uM) or discrete molecule count
    unit: str = "uM"
    is_constant: bool = False          # Boundary species held constant during simulation

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Reaction:
    """Biochemical reaction or state transition with stoichiometry and kinetics."""
    reaction_id: str
    name: str
    reactants: Dict[str, float] = field(default_factory=dict)  # species_id -> stoichiometric coefficient
    products: Dict[str, float] = field(default_factory=dict)   # species_id -> stoichiometric coefficient
    rate_law_type: str = RateLawType.MASS_ACTION.value
    parameters: Dict[str, float] = field(default_factory=dict) # k_f, k_r, Vmax, Km, n, etc.
    reversible: bool = False
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Parameter:
    """Model kinetic parameter with units, bounds, and provenance."""
    name: str
    value: float
    unit: str = "s^-1"
    lower_bound: Optional[float] = None
    upper_bound: Optional[float] = None
    provenance: str = ParameterProvenance.LITERATURE.value
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SimulationModel:
    """Executable biological simulation model specification."""
    model_id: str
    name: str
    model_version: str = "1.0.0"
    model_type: str = ModelType.ODE.value
    species: Dict[str, Species] = field(default_factory=dict)
    reactions: List[Reaction] = field(default_factory=list)
    parameters: Dict[str, Parameter] = field(default_factory=dict)
    compartments: List[str] = field(default_factory=lambda: ["cytosol"])
    stoichiometric_matrix: Optional[List[List[float]]] = None
    observables: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def get_species_names(self) -> List[str]:
        return list(self.species.keys())

    def get_initial_conditions(self) -> Dict[str, float]:
        return {s_id: sp.initial_amount for s_id, sp in self.species.items()}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "model_id": self.model_id,
            "name": self.name,
            "model_version": self.model_version,
            "model_type": self.model_type,
            "species": {k: v.to_dict() for k, v in self.species.items()},
            "reactions": [r.to_dict() for r in self.reactions],
            "parameters": {k: v.to_dict() for k, v in self.parameters.items()},
            "compartments": self.compartments,
            "stoichiometric_matrix": self.stoichiometric_matrix,
            "observables": self.observables,
            "metadata": self.metadata
        }


@dataclass
class Trajectory:
    """Time-series trajectory containing molecular concentration / abundance histories."""
    times: List[float]
    species_trajectories: Dict[str, List[float]]  # species_id -> concentration history
    time_unit: str = "second"
    concentration_unit: str = "uM"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SimulationResult:
    """Result of an executed simulation experiment."""
    job_id: str
    model_id: str
    model_type: str
    solver: str
    trajectory: Trajectory
    fluxes: Optional[Dict[str, float]] = None              # Metabolic fluxes (for FBA)
    flux_bounds: Optional[Dict[str, tuple[float, float]]] = None # Min/max bounds (for FVA)
    execution_time_seconds: float = 0.0
    is_steady_state: bool = False
    metrics: Dict[str, Any] = field(default_factory=dict)
    uncertainty_intervals: Optional[Dict[str, Dict[str, List[float]]]] = None # species -> {lower, upper}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "job_id": self.job_id,
            "model_id": self.model_id,
            "model_type": self.model_type,
            "solver": self.solver,
            "trajectory": self.trajectory.to_dict(),
            "fluxes": self.fluxes,
            "flux_bounds": self.flux_bounds,
            "execution_time_seconds": self.execution_time_seconds,
            "is_steady_state": self.is_steady_state,
            "metrics": self.metrics,
            "uncertainty_intervals": self.uncertainty_intervals
        }


@dataclass
class InterventionSpec:
    """Specification of an in silico intervention experiment."""
    intervention_id: str
    intervention_type: str
    target_entities: List[str]
    strength: float = 1.0
    duration: Optional[float] = None
    dose_range: Optional[List[float]] = None
    mechanism: Optional[str] = None
    parameters_modified: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ValidationReport:
    """Fidelity and consistency check result for a model or simulation trajectory."""
    model_id: str
    mass_conserved: bool = True
    non_negativity_satisfied: bool = True
    solver_converged: bool = True
    rmse_against_data: Optional[float] = None
    pearson_r: Optional[float] = None
    issues: List[str] = field(default_factory=list)
    is_valid: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
