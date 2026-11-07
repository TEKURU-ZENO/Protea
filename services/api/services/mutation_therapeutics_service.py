"""
PROTEA Mutation & Therapeutic Intelligence Engine (MTIE) - Service Layer
Encapsulates all Phase 10 precision oncology and computational therapeutic discovery logic.
"""

from typing import Dict, Any, List, Optional
from ai.mutation_therapeutics.variant.parser import VariantParser
from ai.mutation_therapeutics.variant.normalizer import VariantNormalizer
from ai.mutation_therapeutics.variant.annotator import VariantAnnotator
from ai.mutation_therapeutics.effect_prediction.ensemble import EnsembleEffectPredictor
from ai.mutation_therapeutics.effect_prediction.missense_scorer import MissenseScorer
from ai.mutation_therapeutics.structure.structure_fetcher import StructureFetcher
from ai.mutation_therapeutics.structure.mutant_modeler import MutantModeler
from ai.mutation_therapeutics.structure.interface_analyzer import InterfaceAnalyzer
from ai.mutation_therapeutics.structure.structural_confidence import StructuralConfidenceEvaluator
from ai.mutation_therapeutics.stability.folding_stability import FoldingStabilityPredictor
from ai.mutation_therapeutics.stability.aggregation_analyzer import AggregationAnalyzer
from ai.mutation_therapeutics.stability.allosteric_perturbation import AllostericPerturbationEngine
from ai.mutation_therapeutics.interaction_rewiring.rewiring_predictor import RewiringPredictor
from ai.mutation_therapeutics.interaction_rewiring.mutant_interactome import MutantInteractomeGraphBuilder
from ai.mutation_therapeutics.disease_mechanisms.pathway_disruption import PathwayDisruptionAnalyzer
from ai.mutation_therapeutics.disease_mechanisms.causal_tracer import CausalDiseaseTracer
from ai.mutation_therapeutics.disease_mechanisms.compensatory_detector import CompensatoryBypassDetector
from ai.mutation_therapeutics.target_discovery.target_prioritizer import TargetPrioritizer
from ai.mutation_therapeutics.target_discovery.druggability_analyzer import DruggabilityAnalyzer
from ai.mutation_therapeutics.drug_intelligence.drug_retriever import DrugRetriever
from ai.mutation_therapeutics.drug_intelligence.docking_engine import DockingEngine
from ai.mutation_therapeutics.drug_intelligence.selectivity_analyzer import SelectivityAnalyzer
from ai.mutation_therapeutics.resistance.resistance_predictor import ResistancePredictor
from ai.mutation_therapeutics.resistance.dose_response_model import DoseResponseModel
from ai.mutation_therapeutics.combination_therapy.synergy_calculator import SynergyCalculator
from ai.mutation_therapeutics.combination_therapy.combination_ranker import CombinationRanker
from ai.mutation_therapeutics.simulation.therapeutic_simulator import TherapeuticSimulator
from ai.mutation_therapeutics.simulation.multi_objective_optimizer import MultiObjectiveTherapeuticOptimizer
from ai.mutation_therapeutics.validation.acmg_classifier import ACMGClassifier
from ai.mutation_therapeutics.validation.uncertainty_reporter import UncertaintyReporter
from ai.mutation_therapeutics.evaluation.benchmarks import MTIEBenchmarkSuite
from ai.mutation_therapeutics.schema import (
    GenomicVariant,
    ProteinMutation,
    MutationType,
    FunctionalClass,
    TherapeuticScenario
)


class MutationTherapeuticsService:
    """Singleton service orchestrating the Mutation & Therapeutic Intelligence Engine."""

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(MutationTherapeuticsService, cls).__new__(cls, *args, **kwargs)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return

        self.variant_parser = VariantParser()
        self.variant_normalizer = VariantNormalizer()
        self.variant_annotator = VariantAnnotator()
        self.ensemble_predictor = EnsembleEffectPredictor()
        self.missense_scorer = MissenseScorer()
        self.structure_fetcher = StructureFetcher()
        self.mutant_modeler = MutantModeler()
        self.interface_analyzer = InterfaceAnalyzer()
        self.structural_confidence = StructuralConfidenceEvaluator()
        self.folding_stability = FoldingStabilityPredictor()
        self.aggregation_analyzer = AggregationAnalyzer()
        self.allosteric_engine = AllostericPerturbationEngine()
        self.rewiring_predictor = RewiringPredictor()
        self.interactome_builder = MutantInteractomeGraphBuilder()
        self.pathway_analyzer = PathwayDisruptionAnalyzer()
        self.causal_tracer = CausalDiseaseTracer()
        self.compensatory_detector = CompensatoryBypassDetector()
        self.target_prioritizer = TargetPrioritizer()
        self.druggability_analyzer = DruggabilityAnalyzer()
        self.drug_retriever = DrugRetriever()
        self.docking_engine = DockingEngine()
        self.selectivity_analyzer = SelectivityAnalyzer()
        self.resistance_predictor = ResistancePredictor()
        self.dose_response_model = DoseResponseModel()
        self.synergy_calculator = SynergyCalculator()
        self.combination_ranker = CombinationRanker()
        self.simulator = TherapeuticSimulator()
        self.optimizer = MultiObjectiveTherapeuticOptimizer()
        self.acmg_classifier = ACMGClassifier()
        self.uncertainty_reporter = UncertaintyReporter()
        self.benchmark_suite = MTIEBenchmarkSuite()

        self._initialized = True

    # 1. Variant Ingestion & Normalization
    def ingest_vcf(self, vcf_text: str) -> List[Dict[str, Any]]:
        variants = self.variant_parser.parse_vcf_content(vcf_text)
        return [v.to_dict() for v in variants]

    def normalize_variant(self, variant_data: Dict[str, Any]) -> Dict[str, Any]:
        variant = GenomicVariant.from_dict(variant_data)
        normalized = self.variant_normalizer.normalize_variant(variant)
        transcripts = self.variant_normalizer.map_to_transcript(normalized)
        return {
            "variant": normalized.to_dict(),
            "transcripts": [t.to_dict() for t in transcripts]
        }

    def annotate_variant(self, variant_data: Dict[str, Any]) -> Dict[str, Any]:
        variant = GenomicVariant.from_dict(variant_data)
        return self.variant_annotator.annotate(variant=variant)

    # 2. Mutation Effect Prediction
    def predict_mutation_effect(
        self,
        gene_symbol: str,
        wildtype_aa: str,
        position: int,
        mutant_aa: str
    ) -> Dict[str, Any]:
        effect = self.ensemble_predictor.predict_effect(
            gene_symbol=gene_symbol,
            wildtype_aa=wildtype_aa,
            position=position,
            mutant_aa=mutant_aa
        )
        return effect.to_dict()

    # 3. Structure & Stability
    def analyze_structure(
        self,
        gene_symbol: str,
        wildtype_aa: str,
        position: int,
        mutant_aa: str
    ) -> Dict[str, Any]:
        struct_meta = self.structure_fetcher.fetch_structure_metadata(gene_symbol)
        effect = self.interface_analyzer.analyze_structural_perturbation(
            gene_symbol=gene_symbol,
            wildtype_aa=wildtype_aa,
            position=position,
            mutant_aa=mutant_aa,
            reference_pdb=struct_meta.get("representative_pdb")
        )
        conf = self.structural_confidence.evaluate_confidence(
            plddt_score=effect.plddt_mutant,
            backbone_rmsd=effect.backbone_rmsd
        )
        return {
            "structural_metadata": struct_meta,
            "structural_effect": effect.to_dict(),
            "confidence_evaluation": conf
        }

    def analyze_stability(
        self,
        gene_symbol: str,
        wildtype_aa: str,
        position: int,
        mutant_aa: str
    ) -> Dict[str, Any]:
        folding = self.folding_stability.predict_ddg(wildtype_aa, mutant_aa)
        agg = self.aggregation_analyzer.analyze_aggregation(wildtype_aa, mutant_aa)
        allosteric = self.allosteric_engine.trace_allosteric_coupling(
            gene_symbol=gene_symbol,
            position=position,
            backbone_rmsd=0.65
        )
        return {
            "folding_stability": folding,
            "aggregation": agg,
            "allosteric_perturbation": allosteric
        }

    # 4. Interactome Rewiring
    def predict_rewiring(
        self,
        gene_symbol: str,
        wildtype_aa: str,
        position: int,
        mutant_aa: str,
        functional_class: str = "gain_of_function"
    ) -> Dict[str, Any]:
        try:
            fc = FunctionalClass(functional_class)
        except ValueError:
            fc = FunctionalClass.UNCHARACTERIZED

        rewiring = self.rewiring_predictor.predict_rewiring(
            gene_symbol=gene_symbol,
            wildtype_aa=wildtype_aa,
            position=position,
            mutant_aa=mutant_aa,
            functional_class=fc
        )
        branch_graph = self.interactome_builder.build_branched_interactome(rewiring)
        return {
            "rewiring": rewiring.to_dict(),
            "interactome_branch_graph": branch_graph
        }

    # 5. Disease Mechanisms
    def analyze_disease_mechanism(
        self,
        gene_symbol: str,
        mutation_label: str
    ) -> Dict[str, Any]:
        pathways = self.pathway_analyzer.evaluate_pathway_impact(gene_symbol)
        bypass = self.compensatory_detector.detect_bypass_mechanisms(gene_symbol)
        mechanism = self.causal_tracer.trace_mechanism(
            gene_symbol=gene_symbol,
            mutation_label=mutation_label,
            disrupted_pathways=pathways["disrupted_pathways"],
            hyperactivated_pathways=pathways["hyperactivated_pathways"],
            bypass_mechanisms=[b["mechanism"] for b in bypass]
        )
        return {
            "disease_mechanism": mechanism.to_dict(),
            "bypass_signaling": bypass
        }

    def get_bypass_mechanisms(self, gene_symbol: str) -> List[Dict[str, Any]]:
        return self.compensatory_detector.detect_bypass_mechanisms(gene_symbol)

    # 6. Target Discovery & Druggability
    def discover_targets(
        self,
        mutant_gene: str,
        candidate_genes: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        cands = candidate_genes or ["MAP2K1", "MAP2K2", "EGFR", "MET", "POLR2A"]
        targets = self.target_prioritizer.prioritize_targets(cands, mutant_gene=mutant_gene)
        return [t.to_dict() for t in targets]

    def get_druggability(self, gene_symbol: str) -> Dict[str, Any]:
        return self.druggability_analyzer.evaluate_target(gene_symbol)

    # 7. Drug Intelligence & Docking
    def search_drugs(self, targets: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        if targets:
            drugs = self.drug_retriever.get_drugs_for_targets(targets)
        else:
            drugs = self.drug_retriever.get_all_drugs()
        return [d.to_dict() for d in drugs]

    def evaluate_docking(
        self,
        drug_id: str,
        target_id: str,
        mutation_context: Optional[str] = None
    ) -> Dict[str, Any]:
        binding = self.docking_engine.evaluate_binding(drug_id, target_id, mutation_context)
        selectivity = self.selectivity_analyzer.analyze_selectivity(drug_id)
        return {
            "binding_evidence": binding.to_dict(),
            "selectivity_profile": selectivity
        }

    # 8. Resistance & Combinations
    def predict_resistance(
        self,
        mutation_label: str,
        drug_id: str,
        target_id: str
    ) -> Dict[str, Any]:
        resistance = self.resistance_predictor.predict_resistance(mutation_label, drug_id, target_id)
        # Default dose curve points
        dose_curve = self.dose_response_model.generate_dose_curve_points(ic50_nm=12.0 * resistance.ic50_fold_change)
        return {
            "resistance_mechanism": resistance.to_dict(),
            "simulated_dose_curve": dose_curve
        }

    def analyze_combinations(
        self,
        gene_symbol: str,
        mutation_label: str
    ) -> List[Dict[str, Any]]:
        combos = self.combination_ranker.rank_combinations_for_context(gene_symbol, mutation_label)
        return [c.to_dict() for c in combos]

    # 9. In-Silico Therapeutic Simulation
    def run_simulation(
        self,
        mutant_context: str,
        interventions: List[Dict[str, Any]],
        duration_hours: float = 48.0
    ) -> Dict[str, Any]:
        scen = self.simulator.simulate_intervention(mutant_context, interventions, duration_hours)
        # Evaluate Pareto optimality
        ranked = self.optimizer.evaluate_pareto_frontier([scen])
        return {
            "scenario": ranked[0].to_dict(),
            "pareto_optimal": ranked[0].pareto_optimal
        }

    # 10. Clinical Research Validation Report
    def validate_variant(
        self,
        gene_symbol: str,
        wildtype_aa: str,
        position: int,
        mutant_aa: str
    ) -> Dict[str, Any]:
        variant_id = f"VAR_{gene_symbol}_{wildtype_aa}{position}{mutant_aa}"
        func_res = self.predict_mutation_effect(gene_symbol, wildtype_aa, position, mutant_aa)
        annot_res = self.variant_annotator.annotate(key_hint=f"{gene_symbol}_{wildtype_aa}{position}{mutant_aa}")
        struct_res = self.analyze_structure(gene_symbol, wildtype_aa, position, mutant_aa)["structural_effect"]

        report = self.uncertainty_reporter.generate_validation_report(
            variant_id=variant_id,
            gene_symbol=gene_symbol,
            wildtype_aa=wildtype_aa,
            position=position,
            mutant_aa=mutant_aa,
            functional_effect=func_res,
            annotation_info=annot_res,
            structural_data=struct_res
        )
        return report.to_dict()

    # 11. Scientific Benchmarks
    def run_benchmarks(self) -> Dict[str, Any]:
        return self.benchmark_suite.run_all_benchmarks()
