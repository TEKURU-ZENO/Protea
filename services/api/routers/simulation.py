"""Cellular Simulation Engine (CSE) API Router — Phase 8.

Comprehensive endpoints for biological dynamics, deterministic ODEs,
Gillespie SSA, FBA metabolism, hybrid multiscale coupling, and in-silico experiments.
"""

from typing import Any, Dict, List, Optional, Tuple
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from services.api.services.simulation_service import CellularSimulationService

router = APIRouter(prefix="/simulation", tags=["Cellular Simulation Engine"])
simulation_service = CellularSimulationService()


# --- Request & Response Models ---

class DeterministicSimRequest(BaseModel):
    model_id: str = Field(default="mapk_erk_cascade", description="ID of registered simulation model")
    t_start: float = Field(default=0.0, description="Start time in seconds")
    t_end: float = Field(default=60.0, description="End time in seconds")
    dt: float = Field(default=0.1, description="Recording time step")
    solver: str = Field(default="LSODA", description="Solver: LSODA, RK4, RKF45, BDF, RK45")


class StochasticSimRequest(BaseModel):
    model_id: str = Field(default="goldbeter_koshland", description="ID of registered simulation model")
    algorithm: str = Field(default="gillespie", description="Algorithm: gillespie or tau_leaping")
    t_start: float = Field(default=0.0, description="Start time in seconds")
    t_end: float = Field(default=30.0, description="End time in seconds")
    dt_record: float = Field(default=0.5, description="Time step for trajectory recording")
    random_seed: Optional[int] = Field(default=42, description="Random seed for reproducibility")


class FBARequest(BaseModel):
    model_id: str = Field(default="central_metabolism_fba", description="ID of metabolic model")
    objective_reaction: Optional[str] = Field(default=None, description="Target objective reaction (e.g. v_biomass)")


class FVARequest(BaseModel):
    model_id: str = Field(default="central_metabolism_fba", description="ID of metabolic model")
    fraction_of_optimum: float = Field(default=0.95, ge=0.0, le=1.0, description="Minimum fraction of optimal biomass")


class SignalingCascadeRequest(BaseModel):
    model_id: str = Field(default="mapk_erk_cascade", description="Signaling model ID")
    tiers: Optional[List[str]] = Field(default=["Raf_star", "MEK_star", "ERK_star"], description="Signaling tier species")
    t_end: float = Field(default=60.0, description="Duration in seconds")


class DoseResponseRequest(BaseModel):
    model_id: str = Field(default="mapk_erk_cascade", description="Model ID")
    stimulus: str = Field(default="RasGTP", description="Stimulus entity")
    response: str = Field(default="ERK_star", description="Response entity")
    doses: Optional[List[float]] = Field(default=[0.01, 0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0], description="Titration concentrations")


class InterventionRequest(BaseModel):
    model_id: str = Field(default="mapk_erk_cascade", description="Target model ID")
    intervention_type: str = Field(default="INHIBITION", description="KNOCKOUT, KNOCKDOWN, INHIBITION, OVEREXPRESSION")
    target_entities: List[str] = Field(default=["MEK"], description="Target entities to perturb")
    strength: float = Field(default=0.8, ge=0.0, le=10.0, description="Perturbation strength (e.g. 0.8 = 80% inhibition)")
    t_end: float = Field(default=60.0, description="Duration in seconds")


class SensitivityRequest(BaseModel):
    model_id: str = Field(default="mapk_erk_cascade", description="Model ID")
    parameters: List[str] = Field(default=["k_act_raf", "k_act_mek", "k_act_erk"], description="Parameters to perturb")
    observables: List[str] = Field(default=["ERK_star"], description="Observable outputs")


class EnsembleRequest(BaseModel):
    model_id: str = Field(default="goldbeter_koshland", description="Model ID")
    num_runs: int = Field(default=25, ge=5, le=100, description="Number of Monte Carlo simulations")
    cv: float = Field(default=0.2, description="Coefficient of variation for parameter sampling")


# --- Endpoints ---

@router.get("/models", summary="List all registered models")
def list_simulation_models():
    """Retrieve catalog of curated biophysical models and custom user models."""
    return simulation_service.list_models()


@router.get("/models/{model_id}", summary="Get model by ID")
def get_simulation_model(model_id: str):
    """Retrieve complete model definition including species, reactions, and kinetic parameters."""
    m = simulation_service.get_model(model_id)
    if not m:
        raise HTTPException(status_code=404, detail=f"Model '{model_id}' not found.")
    return m


@router.post("/models", summary="Register a custom biological model")
def register_simulation_model(payload: Dict[str, Any]):
    """Register and validate a new SimulationModel."""
    try:
        return simulation_service.register_custom_model(payload)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/run/deterministic", summary="Run deterministic ODE simulation")
def run_deterministic_simulation(payload: DeterministicSimRequest):
    """Simulate reaction kinetics using adaptive or fixed-step ODE solvers (LSODA, RK4, RKF45, BDF)."""
    try:
        return simulation_service.run_deterministic(
            model_id=payload.model_id,
            t_span=(payload.t_start, payload.t_end),
            dt=payload.dt,
            solver=payload.solver,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/run/stochastic", summary="Run discrete stochastic simulation")
def run_stochastic_simulation(payload: StochasticSimRequest):
    """Simulate stochastic chemical reactions via Gillespie SSA or Tau-Leaping."""
    try:
        return simulation_service.run_stochastic(
            model_id=payload.model_id,
            algorithm=payload.algorithm,
            t_span=(payload.t_start, payload.t_end),
            dt_record=payload.dt_record,
            random_seed=payload.random_seed,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/run/fba", summary="Run Flux Balance Analysis (FBA)")
def run_fba_simulation(payload: FBARequest):
    """Calculate steady-state metabolic flux distribution using Linear Programming."""
    try:
        return simulation_service.run_fba(
            model_id=payload.model_id,
            objective_reaction=payload.objective_reaction,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/run/fva", summary="Run Flux Variability Analysis (FVA)")
def run_fva_simulation(payload: FVARequest):
    """Determine permissible min/max flux ranges supporting near-optimal objective yield."""
    try:
        return simulation_service.run_fva(
            model_id=payload.model_id,
            fraction_of_optimum=payload.fraction_of_optimum,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/metabolism/knockout-screen", summary="Metabolic reaction knockout screen")
def run_metabolic_knockout_screen(model_id: str = Query(default="central_metabolism_fba")):
    """Screen for essential metabolic reactions by systematically knocking out each flux."""
    try:
        return simulation_service.run_metabolic_knockout_screen(model_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/signaling/cascade", summary="Simulate multi-tier signaling cascade")
def run_signaling_cascade_endpoint(payload: SignalingCascadeRequest):
    """Simulate signaling cascade and analyze signal amplification, peak delays, and AUC."""
    try:
        return simulation_service.run_signaling_cascade(
            model_id=payload.model_id,
            tiers=payload.tiers,
            t_span=(0.0, payload.t_end),
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/signaling/dose-response", summary="Compute dose-response titration curve")
def run_dose_response_endpoint(payload: DoseResponseRequest):
    """Titrate stimulus concentration across orders of magnitude to estimate EC50/IC50."""
    try:
        return simulation_service.run_dose_response(
            model_id=payload.model_id,
            stimulus=payload.stimulus,
            response=payload.response,
            doses=payload.doses,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/gene-regulation", summary="Simulate gene regulatory dynamics")
def run_gene_regulation_endpoint(model_id: str = Query(default="lac_operon_grn"), t_end: float = Query(default=100.0)):
    """Simulate coupled mRNA transcription, translation, and repression."""
    try:
        return simulation_service.run_gene_regulation(model_id=model_id, t_span=(0.0, t_end))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/hybrid", summary="Run multiscale hybrid simulation")
def run_hybrid_endpoint(model_id: str = Query(default="hybrid_signaling_grn")):
    """Simulate synchronized multiscale coupling between signaling and gene regulation."""
    try:
        return simulation_service.run_hybrid_multiscale(model_id=model_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/interventions", summary="Execute in-silico intervention experiment")
def run_intervention_endpoint(payload: InterventionRequest):
    """Execute gene knockout, chemical inhibition, or overexpression and compare with wild-type."""
    try:
        spec_dict = {
            "intervention_id": f"pert_{payload.target_entities[0]}",
            "intervention_type": payload.intervention_type,
            "target_entities": payload.target_entities,
            "strength": payload.strength,
        }
        return simulation_service.run_intervention_experiment(
            model_id=payload.model_id,
            spec_data=spec_dict,
            t_span=(0.0, payload.t_end),
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sensitivity", summary="Calculate local parameter sensitivities")
def run_sensitivity_endpoint(payload: SensitivityRequest):
    """Compute normalized sensitivity coefficients dy_i/dtheta_j."""
    try:
        return simulation_service.run_sensitivity_analysis(
            model_id=payload.model_id,
            parameters=payload.parameters,
            observables=payload.observables,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ensemble", summary="Run Monte Carlo ensemble uncertainty simulation")
def run_ensemble_endpoint(payload: EnsembleRequest):
    """Simulate ensemble of perturbed parameters and return mean trajectories with 95% confidence intervals."""
    try:
        return simulation_service.run_ensemble_uncertainty(
            model_id=payload.model_id,
            num_runs=payload.num_runs,
            cv=payload.cv,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/benchmarks", summary="Run all 7 Phase 8 verification benchmarks")
def run_benchmarks_endpoint():
    """Execute master biophysical benchmark suite and return validation scorecard."""
    return simulation_service.run_all_benchmarks()


@router.get("/reproducibility", summary="Verify deterministic seed reproducibility")
def run_reproducibility_endpoint(seed: int = Query(default=12345)):
    """Confirm exact trajectory repeatability under deterministic pseudo-random seeds."""
    return simulation_service.verify_reproducibility(seed)


@router.get("/export/{model_id}", summary="Export model as JSON or SBML stub")
def export_model_endpoint(model_id: str, format: str = Query(default="json", pattern="^(json|sbml)$")):
    """Export model specification for external computational biology systems."""
    try:
        if format == "sbml":
            return {"format": "sbml", "content": simulation_service.export_model_sbml(model_id)}
        return {"format": "json", "content": simulation_service.export_model_json(model_id)}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
