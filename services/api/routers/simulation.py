from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

router = APIRouter(prefix="/simulation", tags=["Cellular Simulation"])

class SimulationRequest(BaseModel):
    initial_abundances: dict
    time_steps: List[float]

@router.post("/solve")
def run_simulation(payload: SimulationRequest):
    # Stub response matching Phase 8 deliverables
    return {
        "status": "success",
        "solver": "Heun ODE Solver",
        "trajectory": [
            {"time": t, "abundances": {k: v * (1.0 - 0.05 * t) for k, v in payload.initial_abundances.items()}}
            for t in payload.time_steps
        ],
        "message": "NeuralODE & CellBox state trajectories will be solved dynamically in Phase 8."
    }
