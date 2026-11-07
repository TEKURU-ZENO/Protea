"""Curated biophysical and biochemical model templates for testing and simulation."""

from typing import Dict, List
from ai.cellular_simulation.schema import (
    SimulationModel, Species, Reaction, Parameter, ModelType, RateLawType, ParameterProvenance
)


class ModelFactory:
    """Factory for generating standardized, validated biological models."""

    @staticmethod
    def create_goldbeter_koshland_model() -> SimulationModel:
        """Classic Goldbeter-Koshland (1981) covalent modification cycle.
        
        Substrate W is phosphorylated to W_star by kinase E1,
        and dephosphorylated back to W by phosphatase E2.
        Displays zero-order ultrasensitivity when Km1, Km2 << W_tot.
        """
        species = {
            "W": Species("W", "Unmodified Substrate", compartment="cytosol", initial_amount=10.0, unit="uM"),
            "W_star": Species("W_star", "Phosphorylated Substrate", compartment="cytosol", initial_amount=0.0, unit="uM"),
            "E1": Species("E1", "Kinase", compartment="cytosol", initial_amount=1.0, unit="uM", is_constant=True),
            "E2": Species("E2", "Phosphatase", compartment="cytosol", initial_amount=1.0, unit="uM", is_constant=True),
        }

        parameters = {
            "kcat1": Parameter("kcat1", 1.0, unit="s^-1", provenance=ParameterProvenance.LITERATURE.value),
            "Km1": Parameter("Km1", 0.5, unit="uM", provenance=ParameterProvenance.LITERATURE.value),
            "kcat2": Parameter("kcat2", 0.8, unit="s^-1", provenance=ParameterProvenance.LITERATURE.value),
            "Km2": Parameter("Km2", 0.5, unit="uM", provenance=ParameterProvenance.LITERATURE.value),
        }

        reactions = [
            # Phosphorylation: W -> W_star via E1
            Reaction(
                reaction_id="r_phospho",
                name="W Phosphorylation",
                reactants={"W": 1.0},
                products={"W_star": 1.0},
                rate_law_type=RateLawType.MICHAELIS_MENTEN.value,
                parameters={"kcat": 1.0, "Km": 0.5, "enzyme": 1.0},
            ),
            # Dephosphorylation: W_star -> W via E2
            Reaction(
                reaction_id="r_dephospho",
                name="W_star Dephosphorylation",
                reactants={"W_star": 1.0},
                products={"W": 1.0},
                rate_law_type=RateLawType.MICHAELIS_MENTEN.value,
                parameters={"kcat": 0.8, "Km": 0.5, "enzyme": 1.0},
            ),
        ]

        return SimulationModel(
            model_id="goldbeter_koshland",
            name="Goldbeter-Koshland Ultrasensitive Cycle",
            model_type=ModelType.ODE.value,
            species=species,
            reactions=reactions,
            parameters=parameters,
            metadata={"reference": "Goldbeter & Koshland, PNAS 1981", "type": "kinetics"},
        )

    @staticmethod
    def create_mapk_cascade_model() -> SimulationModel:
        """Huang-Ferrell (1996) 3-tier MAPK/ERK Signaling Cascade.
        
        Tier 1: Raf activation by RasGTP
        Tier 2: MEK activation by Raf*
        Tier 3: ERK activation by MEK*
        """
        species = {
            "RasGTP": Species("RasGTP", "Active Ras GTPase", initial_amount=0.5, unit="uM", is_constant=True),
            "Raf": Species("Raf", "Inactive Raf Kinase", initial_amount=1.0, unit="uM"),
            "Raf_star": Species("Raf_star", "Active Raf Kinase", initial_amount=0.0, unit="uM"),
            "MEK": Species("MEK", "Inactive MEK Kinase", initial_amount=2.0, unit="uM"),
            "MEK_star": Species("MEK_star", "Active MEK Kinase", initial_amount=0.0, unit="uM"),
            "ERK": Species("ERK", "Inactive ERK Kinase", initial_amount=3.0, unit="uM"),
            "ERK_star": Species("ERK_star", "Active ERK Kinase", initial_amount=0.0, unit="uM"),
            "Phosphatase": Species("Phosphatase", "General Phosphatase", initial_amount=0.5, unit="uM", is_constant=True),
        }

        parameters = {
            "k_act_raf": Parameter("k_act_raf", 0.5, unit="uM^-1 s^-1"),
            "k_deact_raf": Parameter("k_deact_raf", 0.1, unit="s^-1"),
            "k_act_mek": Parameter("k_act_mek", 0.8, unit="uM^-1 s^-1"),
            "k_deact_mek": Parameter("k_deact_mek", 0.15, unit="s^-1"),
            "k_act_erk": Parameter("k_act_erk", 1.2, unit="uM^-1 s^-1"),
            "k_deact_erk": Parameter("k_deact_erk", 0.2, unit="s^-1"),
        }

        reactions = [
            # Raf activation by RasGTP
            Reaction("r_raf_act", "Raf Activation", {"Raf": 1.0, "RasGTP": 1.0}, {"Raf_star": 1.0, "RasGTP": 1.0},
                     rate_law_type=RateLawType.MASS_ACTION.value, parameters={"k_f": 0.5}),
            # Raf deactivation
            Reaction("r_raf_inact", "Raf Inactivation", {"Raf_star": 1.0}, {"Raf": 1.0},
                     rate_law_type=RateLawType.MASS_ACTION.value, parameters={"k_f": 0.1}),
            # MEK activation by Raf*
            Reaction("r_mek_act", "MEK Activation", {"MEK": 1.0, "Raf_star": 1.0}, {"MEK_star": 1.0, "Raf_star": 1.0},
                     rate_law_type=RateLawType.MASS_ACTION.value, parameters={"k_f": 0.8}),
            # MEK deactivation
            Reaction("r_mek_inact", "MEK Inactivation", {"MEK_star": 1.0}, {"MEK": 1.0},
                     rate_law_type=RateLawType.MASS_ACTION.value, parameters={"k_f": 0.15}),
            # ERK activation by MEK*
            Reaction("r_erk_act", "ERK Activation", {"ERK": 1.0, "MEK_star": 1.0}, {"ERK_star": 1.0, "MEK_star": 1.0},
                     rate_law_type=RateLawType.MASS_ACTION.value, parameters={"k_f": 1.2}),
            # ERK deactivation
            Reaction("r_erk_inact", "ERK Inactivation", {"ERK_star": 1.0}, {"ERK": 1.0},
                     rate_law_type=RateLawType.MASS_ACTION.value, parameters={"k_f": 0.2}),
        ]

        return SimulationModel(
            model_id="mapk_erk_cascade",
            name="3-Tier MAPK/ERK Cascade (Huang-Ferrell)",
            model_type=ModelType.ODE.value,
            species=species,
            reactions=reactions,
            parameters=parameters,
            metadata={"pathway": "MAPK Signaling", "organism": "Homo sapiens"},
        )

    @staticmethod
    def create_lac_operon_grn_model() -> SimulationModel:
        """Gene regulatory network: Lac Operon with transcription, translation, and repression."""
        species = {
            "IPTG": Species("IPTG", "Inducer (IPTG)", initial_amount=5.0, unit="uM", is_constant=True),
            "LacI": Species("LacI", "Lac Repressor Protein", initial_amount=2.0, unit="uM"),
            "mRNA_lac": Species("mRNA_lac", "Polycistronic lac mRNA", initial_amount=0.1, unit="uM"),
            "BetaGal": Species("BetaGal", "Beta-Galactosidase Protein", initial_amount=0.5, unit="uM"),
        }

        parameters = {
            "Vmax_transcription": Parameter("Vmax_transcription", 0.5, unit="uM s^-1"),
            "Ki_lacI": Parameter("Ki_lacI", 0.4, unit="uM"),
            "hill_coeff": Parameter("hill_coeff", 2.0, unit="dimensionless"),
            "k_transcription_deg": Parameter("k_transcription_deg", 0.05, unit="s^-1"),
            "k_translation": Parameter("k_translation", 0.2, unit="s^-1"),
            "k_protein_deg": Parameter("k_protein_deg", 0.02, unit="s^-1"),
        }

        reactions = [
            # Transcription repressed by LacI (Hill inhibition)
            Reaction(
                "r_transcription", "lac mRNA Transcription",
                reactants={}, products={"mRNA_lac": 1.0},
                rate_law_type=RateLawType.HILL_INHIBITION.value,
                parameters={"Vmax": 0.5, "Ki": 0.4, "n": 2.0},
            ),
            # mRNA degradation
            Reaction("r_mrna_deg", "lac mRNA Degradation", {"mRNA_lac": 1.0}, {},
                     rate_law_type=RateLawType.MASS_ACTION.value, parameters={"k_f": 0.05}),
            # Translation of BetaGal from mRNA
            Reaction("r_translation", "BetaGal Translation", {"mRNA_lac": 1.0}, {"mRNA_lac": 1.0, "BetaGal": 1.0},
                     rate_law_type=RateLawType.MASS_ACTION.value, parameters={"k_f": 0.2}),
            # Protein degradation
            Reaction("r_protein_deg", "BetaGal Degradation", {"BetaGal": 1.0}, {},
                     rate_law_type=RateLawType.MASS_ACTION.value, parameters={"k_f": 0.02}),
        ]

        return SimulationModel(
            model_id="lac_operon_grn",
            name="E. coli Lac Operon Regulatory Model",
            model_type=ModelType.REGULATORY.value,
            species=species,
            reactions=reactions,
            parameters=parameters,
            metadata={"organism": "Escherichia coli", "type": "gene_regulation"},
        )

    @staticmethod
    def create_central_metabolism_fba_model() -> SimulationModel:
        """Stoichiometric metabolic network for Flux Balance Analysis (FBA).
        
        Pathway:
        1. v_uptake: Extracellular Glucose -> Glucose
        2. v_glycolysis: Glucose -> 2 Pyruvate + 2 ATP
        3. v_lactate: Pyruvate -> Lactate (Fermentation)
        4. v_tca: Pyruvate -> 3 CO2 + 15 ATP (Respiration)
        5. v_biomass: 0.5 Pyruvate + 5 ATP -> Biomass (Objective)
        """
        species = {
            "Glucose": Species("Glucose", "Intracellular Glucose", initial_amount=1.0, unit="mmol/gDW"),
            "Pyruvate": Species("Pyruvate", "Pyruvate", initial_amount=0.5, unit="mmol/gDW"),
            "ATP": Species("ATP", "Adenosine Triphosphate", initial_amount=2.0, unit="mmol/gDW"),
            "Lactate": Species("Lactate", "Lactate", initial_amount=0.0, unit="mmol/gDW", is_constant=True),
            "CO2": Species("CO2", "Carbon Dioxide", initial_amount=0.0, unit="mmol/gDW", is_constant=True),
            "Biomass": Species("Biomass", "Cell Biomass", initial_amount=0.1, unit="gDW", is_constant=True),
        }

        parameters = {
            "glucose_uptake_max": Parameter("glucose_uptake_max", 10.0, unit="mmol/gDW/h"),
        }

        # Reactions with stoichiometric coefficients and flux bounds [lb, ub]
        reactions = [
            Reaction("v_uptake", "Glucose Uptake", {}, {"Glucose": 1.0},
                     rate_law_type=RateLawType.ZERO_ORDER.value, parameters={"lb": 0.0, "ub": 10.0}),
            Reaction("v_glycolysis", "Glycolytic Flux", {"Glucose": 1.0}, {"Pyruvate": 2.0, "ATP": 2.0},
                     rate_law_type=RateLawType.ZERO_ORDER.value, parameters={"lb": 0.0, "ub": 1000.0}),
            Reaction("v_lactate", "Lactate Fermentation", {"Pyruvate": 1.0}, {"Lactate": 1.0},
                     rate_law_type=RateLawType.ZERO_ORDER.value, parameters={"lb": 0.0, "ub": 1000.0}),
            Reaction("v_tca", "TCA Cycle Respiration", {"Pyruvate": 1.0}, {"CO2": 3.0, "ATP": 15.0},
                     rate_law_type=RateLawType.ZERO_ORDER.value, parameters={"lb": 0.0, "ub": 1000.0}),
            Reaction("v_biomass", "Biomass Synthesis (Objective)", {"Pyruvate": 0.5, "ATP": 5.0}, {"Biomass": 1.0},
                     rate_law_type=RateLawType.ZERO_ORDER.value, parameters={"lb": 0.0, "ub": 1000.0, "objective_weight": 1.0}),
        ]

        return SimulationModel(
            model_id="central_metabolism_fba",
            name="Central Carbon Metabolism (FBA)",
            model_type=ModelType.METABOLIC.value,
            species=species,
            reactions=reactions,
            parameters=parameters,
            metadata={"objective": "v_biomass", "scale": "metabolic"},
        )

    @staticmethod
    def create_hybrid_signaling_grn_model() -> SimulationModel:
        """Coupled hybrid model: MAPK signaling tier activating transcription factor (Elk1)
        which induces target gene transcription (c-Fos).
        """
        species = {
            "ERK_active": Species("ERK_active", "Active ERK Kinase", initial_amount=0.2, unit="uM"),
            "TF_inactive": Species("TF_inactive", "Inactive Elk-1 TF", initial_amount=1.0, unit="uM"),
            "TF_active": Species("TF_active", "Phosphorylated Elk-1 TF", initial_amount=0.0, unit="uM"),
            "mRNA_target": Species("mRNA_target", "c-Fos mRNA", initial_amount=0.01, unit="uM"),
            "Protein_target": Species("Protein_target", "c-Fos Protein", initial_amount=0.05, unit="uM"),
        }

        parameters = {
            "k_tf_act": Parameter("k_tf_act", 1.5, unit="uM^-1 s^-1"),
            "k_tf_inact": Parameter("k_tf_inact", 0.3, unit="s^-1"),
            "Vmax_transcription": Parameter("Vmax_transcription", 1.0, unit="uM s^-1"),
            "Ka_tf": Parameter("Ka_tf", 0.3, unit="uM"),
            "hill_coeff": Parameter("hill_coeff", 2.0, unit="dimensionless"),
            "k_mrna_deg": Parameter("k_mrna_deg", 0.1, unit="s^-1"),
            "k_translation": Parameter("k_translation", 0.4, unit="s^-1"),
            "k_protein_deg": Parameter("k_protein_deg", 0.05, unit="s^-1"),
        }

        reactions = [
            # TF phosphorylation driven by ERK_active
            Reaction("r_tf_activation", "Elk-1 Phosphorylation", {"TF_inactive": 1.0}, {"TF_active": 1.0},
                     rate_law_type=RateLawType.MASS_ACTION.value, parameters={"k_f": 1.5}),
            # TF dephosphorylation
            Reaction("r_tf_deactivation", "Elk-1 Dephosphorylation", {"TF_active": 1.0}, {"TF_inactive": 1.0},
                     rate_law_type=RateLawType.MASS_ACTION.value, parameters={"k_f": 0.3}),
            # Target mRNA transcription activated cooperatively by TF_active
            Reaction("r_transcription", "c-Fos Transcription", {}, {"mRNA_target": 1.0},
                     rate_law_type=RateLawType.HILL_ACTIVATION.value, parameters={"Vmax": 1.0, "Ka": 0.3, "n": 2.0}),
            # mRNA decay
            Reaction("r_mrna_decay", "c-Fos mRNA Decay", {"mRNA_target": 1.0}, {},
                     rate_law_type=RateLawType.MASS_ACTION.value, parameters={"k_f": 0.1}),
            # Translation to protein
            Reaction("r_translation", "c-Fos Translation", {"mRNA_target": 1.0}, {"mRNA_target": 1.0, "Protein_target": 1.0},
                     rate_law_type=RateLawType.MASS_ACTION.value, parameters={"k_f": 0.4}),
            # Protein degradation
            Reaction("r_protein_decay", "c-Fos Protein Decay", {"Protein_target": 1.0}, {},
                     rate_law_type=RateLawType.MASS_ACTION.value, parameters={"k_f": 0.05}),
        ]

        return SimulationModel(
            model_id="hybrid_signaling_grn",
            name="Coupled MAPK Signaling & c-Fos Gene Expression",
            model_type=ModelType.HYBRID.value,
            species=species,
            reactions=reactions,
            parameters=parameters,
            metadata={"scale": "multiscale", "tiers": ["signaling", "gene_regulation"]},
        )
