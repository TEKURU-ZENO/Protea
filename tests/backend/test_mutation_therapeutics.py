"""
Unit & Integration Test Suite for PROTEA Phase 10:
Mutation & Therapeutic Intelligence Engine (MTIE)
"""

import pytest
from ai.mutation_therapeutics.variant.parser import VariantParser
from ai.mutation_therapeutics.variant.normalizer import VariantNormalizer
from ai.mutation_therapeutics.variant.annotator import VariantAnnotator
from ai.mutation_therapeutics.effect_prediction.missense_scorer import MissenseScorer
from ai.mutation_therapeutics.effect_prediction.domain_disruption import DomainDisruptionAnalyzer
from ai.mutation_therapeutics.effect_prediction.functional_classifier import FunctionalClassifier
from ai.mutation_therapeutics.effect_prediction.ensemble import EnsembleEffectPredictor
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
from ai.mutation_therapeutics.validation.evidence_aggregator import EvidenceAggregator
from ai.mutation_therapeutics.validation.uncertainty_reporter import UncertaintyReporter
from ai.mutation_therapeutics.evaluation.benchmarks import MTIEBenchmarkSuite
from ai.mutation_therapeutics.schema import (
    GenomicVariant,
    ProteinMutation,
    MutationType,
    FunctionalClass,
    StabilityClass,
    ACMGClass,
    TractabilityTier
)


def test_variant_parsing_and_normalization():
    """Module 1: Test VCF parsing, multi-allelic splitting, HGVS parser, and GRCh38 normalization."""
    vcf_content = """##fileformat=VCFv4.2
#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO
chr7\t140753336\trs113488022\tT\tA,C\t100\tPASS\tGENE=BRAF;HGVS_P=p.Val600Glu
chr17\t7674220\trs28934578\tC\tT\t99\tPASS\tGENE=TP53;HGVS_P=p.Arg175His
"""
    variants = VariantParser.parse_vcf_content(vcf_content, split_multiallelic=True)
    # The first line has two ALT alleles ('A,C'), so it splits into 2 + 1 = 3 variants
    assert len(variants) == 3
    assert variants[0].chrom == "chr7"
    assert variants[0].pos == 140753336
    assert variants[0].alt == "A"
    assert variants[1].alt == "C"

    # HGVS Protein parser
    hgvs_res = VariantParser.parse_hgvs_p("p.Val600Glu")
    assert hgvs_res["wildtype_1"] == "V"
    assert hgvs_res["position"] == 600
    assert hgvs_res["mutant_1"] == "E"
    assert hgvs_res["mutation_type"] == "missense"

    # 1-letter format
    hgvs_1 = VariantParser.parse_hgvs_p("T790M")
    assert hgvs_1["wildtype_1"] == "T"
    assert hgvs_1["position"] == 790
    assert hgvs_1["mutant_1"] == "M"

    # Normalization
    norm_var = VariantNormalizer.normalize_variant(variants[0])
    assert norm_var.chrom == "chr7"
    transcripts = VariantNormalizer.map_to_transcript(norm_var, gene_symbol="BRAF")
    assert len(transcripts) >= 1
    assert transcripts[0].gene_symbol == "BRAF"
    assert "ENST00000288602" in transcripts[0].transcript_id


def test_variant_annotation():
    """Module 1: Test ClinVar, VEP, dbSNP, gnomAD, and COSMIC knowledge integration."""
    annot = VariantAnnotator.annotate(key_hint="BRAF_V600E")
    assert annot["clinvar"]["significance"] == "Pathogenic"
    assert annot["vep"]["consequence"] == "missense_variant"
    assert annot["dbsnp"]["rsid"] == "rs113488022"
    assert annot["cosmic"]["cosmic_id"] == "COSM476"
    assert annot["is_oncogenic_hotspot"] is True

    # Novel variant fallback
    novel_annot = VariantAnnotator.annotate(key_hint="GENE_X99Y")
    assert novel_annot["clinvar"]["significance"] == "Uncertain Significance"
    assert novel_annot["is_oncogenic_hotspot"] is False


def test_missense_scoring_and_conservation():
    """Module 2: Test ESM-2 surrogate scoring, BLOSUM62, and Grantham distance."""
    # V600E: non-conservative change (V hydrophobic -> E negatively charged)
    score_v600e = MissenseScorer.score_mutation("V", "E", 600)
    assert score_v600e["esm_log_odds_delta"] < -5.0
    assert score_v600e["grantham_distance"] > 100
    assert score_v600e["predicted_deleterious"] is True

    # Synonymous change
    score_syn = MissenseScorer.score_mutation("V", "V", 600)
    assert score_syn["esm_log_odds_delta"] == 0.0
    assert score_syn["predicted_deleterious"] is False


def test_domain_disruption_and_functional_classification():
    """Module 2: Test domain disruption mapping and GoF vs LoF classification (Pathogenicity != Mechanism)."""
    # BRAF residue 600 in activation loop
    domain_braf = DomainDisruptionAnalyzer.analyze_disruption("BRAF", 600)
    assert domain_braf["is_activation_loop"] is True
    assert domain_braf["disruption_severity"] == "HIGH"

    # BRAF V600E is deleterious by sequence metrics but is a GAIN OF FUNCTION oncogenic activator
    func_braf = FunctionalClassifier.classify_mechanism("BRAF", "V", 600, "E", domain_braf)
    assert func_braf["functional_class"] == FunctionalClass.GAIN_OF_FUNCTION

    # TP53 R175H in DNA-binding core is a dominant-negative / loss-of-function in tumor suppressor
    domain_p53 = DomainDisruptionAnalyzer.analyze_disruption("TP53", 175)
    assert domain_p53["is_catalytic_site"] is True
    func_p53 = FunctionalClassifier.classify_mechanism("TP53", "R", 175, "H", domain_p53)
    assert func_p53["functional_class"] in [FunctionalClass.LOSS_OF_FUNCTION, FunctionalClass.DOMINANT_NEGATIVE]


def test_structural_modeling_and_confidence():
    """Module 3: Test MutantModeler Branching Principle, interface perturbation, and pLDDT confidence."""
    mut = ProteinMutation(
        gene_symbol="BRAF",
        protein_id="PROT_BRAF",
        wildtype_aa="V",
        position=600,
        mutant_aa="E",
        hgvs_p="p.Val600Glu"
    )
    wt_seq = "M" * 599 + "V" + "M" * 166
    mutant_protein = MutantModeler.generate_mutant_protein("BRAF", wt_seq, [mut])

    # Enforce Branching Principle:
    assert mutant_protein.protein_id != "PROT_BRAF"
    assert mutant_protein.wildtype_protein_id == "PROT_BRAF"
    assert mutant_protein.mutated_sequence[599] == "E"
    assert mutant_protein.wildtype_sequence[599] == "V"
    assert mutant_protein.branch_id.startswith("mut_branch_")

    # Interface analyzer
    struct_res = InterfaceAnalyzer.analyze_structural_perturbation("BRAF", "V", 600, "E")
    assert struct_res.backbone_rmsd > 0.5
    assert struct_res.sasa_change_angstrom2 > 20.0
    assert len(struct_res.interface_residues_perturbed) > 0

    # Structural confidence
    conf = StructuralConfidenceEvaluator.evaluate_confidence(struct_res.plddt_mutant, struct_res.backbone_rmsd)
    assert conf["confidence_tier"] in ["HIGH", "VERY_HIGH"]
    assert conf["is_structurally_reliable"] is True


def test_folding_stability_and_allosteric():
    """Module 4: Test thermodynamic DeltaDeltaG, aggregation propensity, and allosteric coupling."""
    ddg_res = FoldingStabilityPredictor.predict_ddg("V", "E", burial_fraction=0.7)
    assert ddg_res["ddg_kcal_mol"] > 1.2
    assert ddg_res["stability_class"] in [StabilityClass.DESTABILIZING, StabilityClass.SEVERELY_DESTABILIZING]

    # Aggregation
    agg_res = AggregationAnalyzer.analyze_aggregation("A", "F")
    assert agg_res["aggregation_propensity_delta"] > 0.2
    assert agg_res["increased_aggregation_risk"] is True

    # Allosteric coupling
    allosteric = AllostericPerturbationEngine.trace_allosteric_coupling("BRAF", 600, backbone_rmsd=0.85)
    assert allosteric["is_catalytically_perturbed"] is True
    assert "ATP-binding cleft" in allosteric["affected_regulatory_pockets"]


def test_interactome_rewiring_and_branching():
    """Module 5: Test interactome rewiring and branched graph builder with immutable baseline interactome."""
    rewiring = RewiringPredictor.predict_rewiring("BRAF", "V", 600, "E", FunctionalClass.GAIN_OF_FUNCTION)
    assert rewiring.rewiring_index > 0.2
    assert any("YWHAZ" in e["partner"] for e in rewiring.lost_interactions)
    assert any("MAP2K1" in e["partner"] for e in rewiring.gained_interactions or rewiring.retained_interactions)

    # Branch Graph Builder
    branch_graph = MutantInteractomeGraphBuilder.build_branched_interactome(rewiring)
    assert branch_graph["branching_principle_verified"] is True
    assert branch_graph["parent_interactome_id"] == "interactome_human_reference_v3"
    assert branch_graph["nodes_count"] > 2
    assert branch_graph["edges_count"] > 2


def test_disease_mechanism_and_pathways():
    """Module 6: Test pathway disruption, causal mechanistic tracing, and compensatory bypass."""
    pathways = PathwayDisruptionAnalyzer.evaluate_pathway_impact("BRAF", FunctionalClass.GAIN_OF_FUNCTION)
    assert len(pathways["hyperactivated_pathways"]) >= 2
    assert any("MAPK" in p["name"] for p in pathways["hyperactivated_pathways"])

    # Causal tracer
    causal = CausalDiseaseTracer.trace_mechanism(
        gene_symbol="BRAF",
        mutation_label="BRAF_V600E",
        disrupted_pathways=pathways["disrupted_pathways"],
        hyperactivated_pathways=pathways["hyperactivated_pathways"]
    )
    assert "Melanoma" in causal.disease_name
    assert len(causal.causal_chain) >= 5

    # Compensatory bypass
    bypass = CompensatoryBypassDetector.detect_bypass_mechanisms("BRAF")
    assert len(bypass) >= 2
    assert any("CRAF" in b["mechanism"] for b in bypass)


def test_target_discovery_and_druggability():
    """Module 7: Test target prioritization with DepMap dependency and safety penalization."""
    targets = TargetPrioritizer.prioritize_targets(["MAP2K1", "EGFR", "POLR2A"], mutant_gene="BRAF")
    # Top targets
    assert len(targets) >= 3
    top_gene = targets[0].gene_symbol
    assert top_gene in ["BRAF", "MAP2K1", "EGFR"]

    # Pan-essential gene POLR2A must be penalized in safety
    polr2a = next(t for t in targets if t.gene_symbol == "POLR2A")
    assert polr2a.safety_score < 0.15

    # Druggability analyzer
    drug_eval = DruggabilityAnalyzer.evaluate_target("BRAF")
    assert drug_eval["is_druggable"] is True
    assert drug_eval["pocket_volume_angstrom3"] > 600.0


def test_drug_intelligence_and_docking():
    """Module 8: Test drug candidate queries, molecular docking scores, and selectivity."""
    drugs = DrugRetriever.get_drugs_for_targets(["BRAF"])
    assert len(drugs) >= 2
    drug_names = [d.name for d in drugs]
    assert "Vemurafenib" in drug_names or "Dabrafenib" in drug_names

    # Docking evaluation with caution guardrail
    dock_res = DockingEngine.evaluate_binding("DRUG_VEMURAFENIB", "TGT_BRAF", "BRAF_V600E")
    assert dock_res.docking_score_kcal_mol <= -10.0
    assert "computational ranking estimate" in dock_res.caution_note

    # Selectivity
    sel_res = SelectivityAnalyzer.analyze_selectivity("DRUG_VEMURAFENIB")
    assert sel_res["selectivity_ratio"] > 10.0


def test_resistance_and_dose_response():
    """Module 9: Test secondary resistance prediction and Hill equation dose-response modeling."""
    res = ResistancePredictor.predict_resistance("EGFR_T790M", "DRUG_GEFITINIB", "TGT_EGFR")
    assert res.mechanism_type == "gatekeeper_mutation"
    assert res.ic50_fold_change > 50.0

    # Dose response model
    dose_resp = DoseResponseModel.compute_response_shift(
        drug_id="DRUG_GEFITINIB",
        target_id="TGT_EGFR",
        wt_ic50_nm=33.0,
        mut_ic50_nm=2100.0
    )
    assert dose_resp.response_phenotype == "resistant"
    assert dose_resp.resistance_fold_change > 50.0

    # Curve points
    curve = DoseResponseModel.generate_dose_curve_points(ic50_nm=50.0, num_points=5)
    assert len(curve) == 5
    assert curve[0]["inhibition_percent"] < curve[-1]["inhibition_percent"]


def test_combination_therapy_synergy():
    """Module 10: Test multi-metric combination synergy with explicit assumption reporting."""
    combo = SynergyCalculator.calculate_synergy(
        drug_a_id="DRUG_DABRAFENIB",
        drug_b_id="DRUG_TRAMETINIB",
        target_a="BRAF",
        target_b="MAP2K1",
        effect_a=0.55,
        effect_b=0.50,
        combination_effect=0.95,
        conc_a=50.0,
        ic50_a=120.0,
        conc_b=5.0,
        ic50_b=15.0
    )
    assert combo.synergistic is True
    assert combo.bliss_excess > 15.0
    assert combo.loewe_combination_index < 1.0
    assert "bliss" in combo.metric_assumptions
    assert "loewe" in combo.metric_assumptions

    # Ranker
    ranked_combos = CombinationRanker.rank_combinations_for_context("BRAF", "BRAF_V600E")
    assert len(ranked_combos) >= 1
    assert ranked_combos[0].synergistic is True


def test_therapeutic_simulation_and_pareto():
    """Module 11: Test in-silico intervention simulation and multi-objective Pareto optimization."""
    scen = TherapeuticSimulator.simulate_intervention(
        mutant_context="BRAF_V600E",
        drug_interventions=[{"name": "Dabrafenib"}, {"name": "Trametinib"}]
    )
    assert scen.disease_pathway_inhibition > 0.90
    assert len(scen.trajectory_points) == 7
    # Trajectory demonstrates increasing pathway inhibition over time
    assert scen.trajectory_points[0]["pathway_activity_percent"] > scen.trajectory_points[-1]["pathway_activity_percent"]

    # Pareto optimizer
    bad_scen = TherapeuticSimulator.simulate_intervention(
        mutant_context="BRAF_V600E",
        drug_interventions=[]
    )
    bad_scen.disease_pathway_inhibition = 0.40
    bad_scen.essential_gene_retention = 0.60
    bad_scen.toxicity_estimate = 0.50

    ranked = MultiObjectiveTherapeuticOptimizer.evaluate_pareto_frontier([scen, bad_scen])
    assert ranked[0].scenario_id == scen.scenario_id
    assert scen.pareto_optimal is True
    assert bad_scen.pareto_optimal is False


def test_acmg_classification_and_uncertainty_report():
    """Module 12: Test ACMG/AMP rules, evidence aggregation, and uncertainty quantification."""
    annot = VariantAnnotator.annotate(key_hint="BRAF_V600E")
    func_eff = EnsembleEffectPredictor.predict_effect("BRAF", "V", 600, "E").to_dict()

    acmg_class, criteria = ACMGClassifier.evaluate_criteria(
        gene_symbol="BRAF",
        wildtype_aa="V",
        position=600,
        mutant_aa="E",
        functional_effect=func_eff,
        annotation_info=annot,
        is_known_hotspot=True
    )
    assert acmg_class in [ACMGClass.PATHOGENIC, ACMGClass.LIKELY_PATHOGENIC]
    assert any(c in criteria for c in ["PS3", "PM1", "PP3", "PP5"])

    # Uncertainty & Evidence report
    report = UncertaintyReporter.generate_validation_report(
        variant_id="VAR_BRAF_V600E",
        gene_symbol="BRAF",
        wildtype_aa="V",
        position=600,
        mutant_aa="E",
        functional_effect=func_eff,
        annotation_info=annot
    )
    assert report.acmg_class == acmg_class
    assert report.evidence_counts["curated"] > 0
    assert report.evidence_counts["predicted"] > 0
    assert "clinical" in report.clinical_boundary_disclaimer.lower()


def test_scientific_benchmarks_all_passing():
    """Verify all 9 MTIE scientific research benchmarks pass at 100%."""
    res = MTIEBenchmarkSuite.run_all_benchmarks()
    assert res["status"] == "PASSED"
    assert res["passed_benchmarks"] == 9
    assert res["total_benchmarks"] == 9
    assert res["pass_rate_percent"] == 100.0
