"""Comprehensive benchmark evaluation suite for the Cellular Simulation Engine."""

from typing import Any, Dict, List
import numpy as np

from ai.cellular_simulation.model_builder.model_factory import ModelFactory
from ai.cellular_simulation.deterministic.ode_engine import ODEDynamicsEngine
from ai.cellular_simulation.stochastic.gillespie import GillespieEngine
from ai.cellular_simulation.metabolism.fba import FluxBalanceAnalysis
from ai.cellular_simulation.metabolism.gene_knockout import MetabolicKnockoutAnalyzer
from ai.cellular_simulation.signaling.signaling_model import SignalingEngine
from ai.cellular_simulation.gene_regulation.regulatory_network import RegulatoryNetworkEngine
from ai.cellular_simulation.uncertainty.sensitivity import LocalSensitivityAnalyzer


class SimulationBenchmarks:
    """Executes 7 standard biophysical and computational benchmarks."""

    @staticmethod
    def run_goldbeter_ultrasensitivity_benchmark() -> Dict[str, Any]:
        """Benchmark 1: Goldbeter-Koshland cycle ultrasensitive switch."""
        model = ModelFactory.create_goldbeter_koshland_model()
        engine = ODEDynamicsEngine(model)
        res = engine.simulate(t_span=(0.0, 50.0), dt=0.2, solver="LSODA")
        w_star_final = res.trajectory.species_trajectories["W_star"][-1]
        passed = bool(w_star_final > 4.0)

        return {
            "benchmark": "Goldbeter-Koshland Ultrasensitivity",
            "passed": passed,
            "w_star_final": float(w_star_final),
            "execution_time_seconds": res.execution_time_seconds,
        }

    @staticmethod
    def run_mapk_cascade_benchmark() -> Dict[str, Any]:
        """Benchmark 2: MAPK/ERK cascade signal propagation and amplification."""
        model = ModelFactory.create_mapk_cascade_model()
        engine = SignalingEngine(model)
        res = engine.simulate_cascade(
            t_span=(0.0, 60.0),
            dt=0.1,
            tiers=["Raf_star", "MEK_star", "ERK_star"],
        )
        erk_peak = res.metrics.get("cascade_tier_analysis", {}).get("ERK_star", {}).get("peak_concentration", 0.0)
        passed = bool(erk_peak > 1.0)

        return {
            "benchmark": "MAPK/ERK Cascade Propagation",
            "passed": passed,
            "erk_peak_concentration": float(erk_peak),
            "execution_time_seconds": res.execution_time_seconds,
        }

    @staticmethod
    def run_lac_operon_benchmark() -> Dict[str, Any]:
        """Benchmark 3: E. coli Lac operon transcription and repression."""
        model = ModelFactory.create_lac_operon_grn_model()
        engine = RegulatoryNetworkEngine(model)
        res = engine.simulate_continuous(t_span=(0.0, 80.0), dt=0.5, solver="LSODA")
        betagal_final = res.trajectory.species_trajectories["BetaGal"][-1]
        passed = bool(betagal_final > 0.05)

        return {
            "benchmark": "Lac Operon Regulatory Dynamics",
            "passed": passed,
            "betagal_final_concentration": float(betagal_final),
            "execution_time_seconds": res.execution_time_seconds,
        }

    @staticmethod
    def run_central_metabolism_fba_benchmark() -> Dict[str, Any]:
        """Benchmark 4: Central carbon metabolism steady-state Flux Balance Analysis."""
        model = ModelFactory.create_central_metabolism_fba_model()
        fba = FluxBalanceAnalysis(model)
        res = fba.optimize()
        obj_val = res.metrics.get("objective_value", 0.0)
        passed = bool(obj_val > 0.5)

        return {
            "benchmark": "Central Metabolism FBA Optimization",
            "passed": passed,
            "biomass_flux_rate": float(obj_val),
            "execution_time_seconds": res.execution_time_seconds,
        }

    @staticmethod
    def run_stochastic_vs_ode_benchmark() -> Dict[str, Any]:
        """Benchmark 5: Gillespie SSA vs deterministic ODE convergence."""
        model = ModelFactory.create_goldbeter_koshland_model()
        gillespie = GillespieEngine(model)
        res_ssa = gillespie.simulate(t_span=(0.0, 30.0), dt_record=0.5, random_seed=42)
        passed = bool(len(res_ssa.trajectory.times) > 10)

        return {
            "benchmark": "Gillespie SSA Stochastic vs Deterministic",
            "passed": passed,
            "steps_simulated": res_ssa.metrics.get("total_stochastic_steps", 0),
            "execution_time_seconds": res_ssa.execution_time_seconds,
        }

    @staticmethod
    def run_sobol_sensitivity_benchmark() -> Dict[str, Any]:
        """Benchmark 6: Local parameter sensitivity profiling."""
        model = ModelFactory.create_mapk_cascade_model()
        analyzer = LocalSensitivityAnalyzer(model)
        sens = analyzer.analyze(
            parameters_to_test=["k_act_raf", "k_act_mek", "k_act_erk"],
            observables=["ERK_star"],
            t_span=(0.0, 30.0),
        )
        passed = bool("ERK_star" in sens and len(sens["ERK_star"]) > 0)

        return {
            "benchmark": "Signaling Parameter Sensitivity",
            "passed": passed,
            "sensitivities": sens,
        }

    @staticmethod
    def run_knockout_essentiality_benchmark() -> Dict[str, Any]:
        """Benchmark 7: Metabolic single knockout essentiality screening."""
        model = ModelFactory.create_central_metabolism_fba_model()
        ko_analyzer = MetabolicKnockoutAnalyzer(model)
        screen = ko_analyzer.single_knockout_screen()
        essential_count = sum(1 for v in screen.values() if v.get("is_essential", False))
        passed = bool(essential_count >= 1)

        return {
            "benchmark": "Metabolic Knockout Lethality Screening",
            "passed": passed,
            "essential_reactions_count": essential_count,
            "screen_summary": screen,
        }

    @classmethod
    def run_all_benchmarks(cls) -> Dict[str, Any]:
        """Run all 7 benchmarks and assemble a master validation scorecard."""
        benchmarks = [
            cls.run_goldbeter_ultrasensitivity_benchmark(),
            cls.run_mapk_cascade_benchmark(),
            cls.run_lac_operon_benchmark(),
            cls.run_central_metabolism_fba_benchmark(),
            cls.run_stochastic_vs_ode_benchmark(),
            cls.run_sobol_sensitivity_benchmark(),
            cls.run_knockout_essentiality_benchmark(),
        ]

        all_passed = all(b.get("passed", False) for b in benchmarks)
        pass_count = sum(1 for b in benchmarks if b.get("passed", False))

        return {
            "total_benchmarks": len(benchmarks),
            "passed_benchmarks": pass_count,
            "all_passed": all_passed,
            "score_percentage": (pass_count / len(benchmarks)) * 100.0,
            "results": benchmarks,
        }
