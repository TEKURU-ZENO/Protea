"""
Unit & Integration Test Suite for PROTEA Phase 11:
Multi-Omics & Evolution Intelligence Engine (MOEIE)
"""

import pytest
from ai.moeie.schema import (
    OmicsDataset,
    BiologicalSample,
    OmicsMeasurement,
    OmicsModality,
    CellPopulation,
    SpatialRegion,
    OrthologGroup,
    ConservationTier,
    EvolutionaryModule,
    EvidenceProvenance
)
from ai.moeie.ingestion.adapters import ModalityIngestionAdapters
from ai.moeie.ingestion.identifiers import CrossSpeciesIdentifierResolver
from ai.moeie.ingestion.registry import DatasetRegistry
from ai.moeie.preprocessing.normalization import MultiOmicsNormalizer
from ai.moeie.preprocessing.quality_control import QualityControlEngine
from ai.moeie.representation.latent_models import SharedPrivateLatentModel
from ai.moeie.representation.cross_modal_alignment import CrossModalAligner
from ai.moeie.cellular.cell_annotation import CellAnnotationEngine
from ai.moeie.cellular.trajectory import TrajectoryEngine
from ai.moeie.cellular.cell_communication import CellCommunicationEngine
from ai.moeie.spatial.spatial_graph import SpatialGraphEngine
from ai.moeie.spatial.spatial_programs import SpatialProgramEngine
from ai.moeie.regulatory.tf_activity import TFActivityInferenceEngine
from ai.moeie.regulatory.grn_reconstruction import GRNReconstructionEngine
from ai.moeie.regulatory.protein_rna_discordance import ProteinRNADiscordanceAnalyzer
from ai.moeie.evolution.orthology import OrthologyInferenceEngine
from ai.moeie.evolution.conservation import SequenceConservationEngine
from ai.moeie.evolution.phylogeny import PhylogeneticEngine
from ai.moeie.evolutionary_interactome.cross_species_mapping import CrossSpeciesMappingEngine
from ai.moeie.evolutionary_interactome.network_alignment import NetworkAlignmentEngine
from ai.moeie.evolutionary_interactome.coverage_uncertainty import CoverageUncertaintyEstimator
from ai.moeie.prediction.evolution_ppi_transfer import EvolutionPPITransferEngine
from ai.moeie.prediction.evolution_mutation import EvolutionMutationPredictor
from ai.moeie.systems.pathway_evolution import PathwayEvolutionEngine
from ai.moeie.therapeutics.target_conservation import EvolutionaryTherapeuticPrioritizer
from ai.moeie.validation.leakage_guard import ScientificLeakageGuard
from ai.moeie.validation.provenance_tracker import ProvenanceTracker
from ai.moeie.evaluation.benchmarks import MOEIEBenchmarkSuite
from services.api.services.moeie_service import MOEIEService


def test_multi_omics_ingestion_and_identifiers():
    """Module 1: Test ingestion adapters for all modalities and cross-species identifier resolution."""
    adapters = ModalityIngestionAdapters()
    resolver = CrossSpeciesIdentifierResolver()

    # 1. Transcriptomics ingestion: sample_id -> {gene: count}
    tx_res = adapters.ingest_transcriptomics(
        dataset_name="Melanoma_Bulk_RNA",
        expression_matrix={
            "s1": {"EGFR": 45.2, "TP53": 89.1},
            "s2": {"EGFR": 12.0, "TP53": 95.4}
        },
        metadata={"platform": "Illumina NovaSeq", "technology": "bulk RNA-seq"}
    )
    assert tx_res["dataset"].modality == OmicsModality.TRANSCRIPTOMICS
    assert tx_res["features_count"] == 2
    assert tx_res["measurements_count"] == 4

    # 2. Proteomics ingestion: sample_id -> {protein: intensity}
    prot_res = adapters.ingest_proteomics(
        dataset_name="Melanoma_TMT_Proteome",
        intensity_matrix={
            "s1": {"EGFR": 1.2, "TP53": -0.5},
            "s2": {"EGFR": -0.4, "TP53": 0.8}
        }
    )
    assert prot_res["measurements_count"] == 4

    # 3. Single-cell metadata ingestion
    sc_res = adapters.ingest_single_cell(
        dataset_name="Melanoma_10X_scRNA",
        n_cells=5000,
        n_genes=22000,
        cell_types=["T_Cell_CD8", "Melanocyte_Malignant", "Macrophage"]
    )
    assert sc_res["n_cells"] == 5000
    assert sc_res["dataset"].modality == OmicsModality.SINGLE_CELL

    # 4. Cross-species identifier resolution
    human_tp53 = resolver.resolve_identifier("TP53", 9606)
    assert human_tp53.gene_symbol == "TP53"
    assert human_tp53.protein_accession == "P04637"
    assert human_tp53.organism_taxonomy_id == 9606

    mouse_braf = resolver.resolve_identifier("Braf", 10090)
    assert mouse_braf.gene_symbol == "Braf"
    assert mouse_braf.organism_taxonomy_id == 10090
    assert mouse_braf.protein_accession == "P28028"


def test_normalization_and_qc_confounding():
    """Module 2: Test raw vs corrected normalization retention and batch confounding evaluation."""
    normalizer = MultiOmicsNormalizer()
    qc = QualityControlEngine()

    measurements = [
        OmicsMeasurement(
            measurement_id="m1",
            sample_id="s1",
            feature_id="EGFR",
            modality=OmicsModality.TRANSCRIPTOMICS,
            raw_value=100.0,
            normalized_value=100.0,
            unit="counts",
            quality_flag="PASS"
        ),
        OmicsMeasurement(
            measurement_id="m2",
            sample_id="s2",
            feature_id="EGFR",
            modality=OmicsModality.TRANSCRIPTOMICS,
            raw_value=250.0,
            normalized_value=250.0,
            unit="counts",
            quality_flag="PASS"
        ),
        OmicsMeasurement(
            measurement_id="m3",
            sample_id="s3",
            feature_id="EGFR",
            modality=OmicsModality.TRANSCRIPTOMICS,
            raw_value=0.0,
            normalized_value=0.0,
            unit="counts",
            is_missing=True,
            quality_flag="LOW_DEPTH"
        )
    ]

    normalized = normalizer.normalize_measurements(measurements, OmicsModality.TRANSCRIPTOMICS)
    assert len(normalized) == 3
    # Check that both raw_value and normalized_value are preserved
    for m in normalized:
        assert m.raw_value is not None
        assert m.normalized_value is not None

    # Evaluate QC
    qc_res = qc.evaluate_quality(normalized)
    assert qc_res["total_measurements"] == 3
    assert qc_res["status"] == "PASSED"
    assert qc_res["missing_rate"] == pytest.approx(0.3333, rel=1e-2)

    # Evaluate batch confounding
    samples = [
        BiologicalSample("s1", "ds1", "d1", "Skin", disease_state="Melanoma", batch_id="batch_A"),
        BiologicalSample("s2", "ds1", "d2", "Skin", disease_state="Melanoma", batch_id="batch_A"),
        BiologicalSample("s3", "ds1", "d3", "Skin", disease_state="Healthy", batch_id="batch_B")
    ]
    conf_res = qc.evaluate_batch_confounding(samples)
    assert "confounding_score" in conf_res
    assert conf_res["confounding_score"] > 0.0


def test_shared_private_latent_model_and_imputation():
    """Module 3: Test shared/private factor decomposition and missing-modality imputation."""
    model = SharedPrivateLatentModel(shared_dim=8, private_dim=4)
    aligner = CrossModalAligner()

    modality_profiles = {
        "transcriptomics": [2.5, 3.1, 0.4, 1.8, 5.0, 0.2, 1.1, 4.3],
        "proteomics": [1.8, 2.9, 0.2, 1.5, 4.2, 0.1, 0.9, 3.8]
    }

    latent_rep = model.encode("sample_melanoma_01", modality_profiles)
    assert len(latent_rep.shared_factors) == 8
    assert "transcriptomics" in latent_rep.private_factors
    assert "proteomics" in latent_rep.private_factors
    assert "transcriptomics" in latent_rep.variance_explained

    # Cross-modal imputation from shared factors
    imputed = aligner.impute_missing_modality(latent_rep, "phosphoproteomics", n_features=6)
    assert len(imputed) == 6
    assert any(v != 0.0 for v in imputed)


def test_cell_annotation_and_trajectory():
    """Module 4: Test single-cell marker annotation and pseudotime inference with scientific caveat."""
    annotation_engine = CellAnnotationEngine()
    trajectory_engine = TrajectoryEngine()

    detected_genes = ["CD8A", "GZMB", "EPCAM", "COL1A1", "CD14"]
    subpopulations = annotation_engine.annotate_subpopulations("sc_dataset_01", detected_genes, total_cells=5000)
    assert len(subpopulations) >= 4

    pop_names = [p.cell_type for p in subpopulations]
    root = pop_names[0]
    traj = trajectory_engine.infer_trajectory(pop_names, root)

    assert "trajectory_nodes" in traj
    assert "pseudotime_caution" in traj
    assert "pseudotime measures inferred transcriptomic similarity distance" in traj["pseudotime_caution"].lower()


def test_cell_communication_hypotheses():
    """Module 5: Test ligand-receptor communication network scoring and hypothesis status."""
    comm_engine = CellCommunicationEngine()
    active_pops = ["Malignant_Epithelial", "T_Cell_CD8_Cytotoxic", "Cancer_Associated_Fibroblast"]

    comm_res = comm_engine.infer_communication_network(active_pops)
    assert comm_res["total_interactions_inferred"] > 0
    assert len(comm_res["interactions"]) > 0
    assert "caution_note" in comm_res
    assert "statistical hypotheses inferred from expression" in comm_res["caution_note"].lower()


def test_spatial_graph_and_morans_i():
    """Module 6: Test spatial neighborhood graph, tissue domains, and Moran's I SVGs."""
    spatial_graph = SpatialGraphEngine()
    spatial_programs = SpatialProgramEngine()

    regions = spatial_graph.segment_tissue_domains("sample_spatial_01", n_spots=50)
    assert len(regions) >= 40

    coords = [(r.x_microns, r.y_microns) for r in regions]
    graph = spatial_graph.build_spatial_neighborhood_graph(coords, k_neighbors=4)
    assert graph["total_spots"] == len(regions)
    assert graph["total_neighborhood_edges"] > 0
    assert "guardrail_notice" in graph

    # Moran's I calculation
    clustered_vals = [5.0, 4.8, 5.2, 4.9, 0.2, 0.1, 0.3, 0.1]
    edges = [
        {"source_spot": 0, "target_spot": 1, "spatial_weight": 0.9},
        {"source_spot": 1, "target_spot": 2, "spatial_weight": 0.85},
        {"source_spot": 4, "target_spot": 5, "spatial_weight": 0.9},
        {"source_spot": 5, "target_spot": 6, "spatial_weight": 0.85}
    ]
    moran = spatial_programs.compute_morans_i("VEGFA", clustered_vals, edges)
    assert "morans_i" in moran
    assert moran["is_spatially_variable"] is True


def test_regulatory_tf_activity_and_grn():
    """Module 7: Test TF regulon activity inference, chromatin-gene linkage, and GRN reconstruction."""
    tf_engine = TFActivityInferenceEngine()
    grn_engine = GRNReconstructionEngine()

    expression_profile = {
        "CDKN1A": 8.5,
        "MDM2": 6.2,
        "BAX": 7.1,
        "FAS": 4.9,
        "JUN": 1.2
    }

    tf_activities = tf_engine.infer_tf_activity(expression_profile)
    assert len(tf_activities) >= 4
    tp53_act = next((t for t in tf_activities if t["transcription_factor"] == "TP53"), None)
    assert tp53_act is not None
    assert tp53_act["activity_zscore"] > 1.5

    grn = grn_engine.reconstruct_local_network("TP53")
    assert grn["focal_gene"] == "TP53"
    assert len(grn["nodes"]) >= 5

    peaks = grn_engine.link_chromatin_to_genes("TP53")
    assert len(peaks) > 0
    assert peaks[0]["target_gene"] == "TP53"


def test_protein_rna_discordance():
    """Module 8: Test post-transcriptional discordance and phospho signaling flux."""
    analyzer = ProteinRNADiscordanceAnalyzer()

    rna = {"TP53": 10.0, "EGFR": 2.0, "MYC": 8.0}
    prot = {"TP53": 1.5, "EGFR": 9.5, "MYC": 7.9}
    phospho = {"TP53": 0.2, "EGFR": 11.0, "MYC": 2.1}

    results = analyzer.analyze_discordance(rna, prot, phospho)
    assert len(results) == 3

    tp53_res = next(r for r in results if r["gene"] == "TP53")
    assert tp53_res["discordance_delta"] < -1.5
    assert "Degradation" in tp53_res["regulatory_mode"]

    egfr_res = next(r for r in results if r["gene"] == "EGFR")
    assert egfr_res["discordance_delta"] > 1.5
    assert egfr_res["is_hyperphosphorylated"] is True
    assert egfr_res["ptm_flux_active"] is True


def test_orthology_and_sequence_conservation():
    """Module 9: Test orthology groupings, phyloP/phastCons scores, and gene constraint metrics."""
    ortho_engine = OrthologyInferenceEngine()
    cons_engine = SequenceConservationEngine()

    og = ortho_engine.get_ortholog_group("TP53")
    assert og.ortholog_group_id == "OG_P53_FAMILY"
    assert og.evolutionary_depth == "Bilateria"
    assert len(og.member_genes) >= 4

    cons = cons_engine.evaluate_residue_conservation("TP53", position=175)
    assert cons["is_evolutionarily_invariant"] is True
    assert cons["phylop_score"] > 6.0
    assert cons["constraint_tier"] == "HIGH_CONSTRAINT"

    metrics = cons_engine.get_gene_constraint_metrics("TP53")
    assert metrics["gene"] == "TP53"
    assert metrics["pli"] > 0.70


def test_phylogenetic_tree_and_events():
    """Module 10: Test phylogenetic tree reconstruction, gene duplication, and loss events."""
    phylo_engine = PhylogeneticEngine()

    tree = phylo_engine.build_tree("EGFR")
    assert tree.tree_id.startswith("tree_egfr")
    assert len(tree.species_included) >= 5
    assert tree.newick_string.startswith("(")

    events = phylo_engine.infer_evolutionary_events("BRAF")
    assert len(events) >= 1
    assert events[0].gene_symbol == "BRAF"
    assert events[0].event_type == "gene_duplication"


def test_network_alignment_and_coverage_uncertainty():
    """Module 11: Test cross-species interactome alignment and coverage-aware uncertainty."""
    alignment_engine = NetworkAlignmentEngine()
    coverage_engine = CoverageUncertaintyEstimator()

    analysis = alignment_engine.align_interactomes("Homo sapiens", "Mus musculus", "MAPK_Signaling")
    assert analysis.alignment_f1 >= 0.85
    assert analysis.conserved_features_count > 20

    modules = alignment_engine.get_evolutionary_modules()
    assert len(modules) >= 3

    # Coverage uncertainty: observed in Human & Mouse, unobserved in Zebrafish (low coverage)
    cov_res = coverage_engine.evaluate_conservation_with_coverage(
        interaction_pair="EGFR-GRB2",
        observed_in_taxa=[9606, 10090],
        unobserved_in_taxa=[7955]
    )
    assert cov_res["coverage_gap_risk"] == "HIGH"
    assert "data scarcity, not evolutionary deletion" in cov_res["scientific_conclusion"].lower()


def test_evolution_ppi_transfer_and_mutation():
    """Module 12: Test evolution-aware PPI transferability and mutation pathogenicity scoring."""
    transfer_engine = EvolutionPPITransferEngine()
    mutation_predictor = EvolutionMutationPredictor()

    transfer = transfer_engine.predict_cross_species_transfer("BRAF", "MAP2K1")
    assert transfer["is_transfer_supported"] is True
    assert transfer["confidence_tier"] in ["HIGH", "MODERATE"]
    assert transfer["predictions"]["evolution_aware_multimodal"] > transfer["predictions"]["sequence_only_baseline"]

    mut_res = mutation_predictor.predict_evolutionary_impact("TP53", "R", 175, "H", base_esm_score=-9.8)
    assert mut_res["constraint_status"] == "STRICTLY_INVARIANT_DNA_BINDING"
    assert mut_res["calibrated_evolution_score"] < -9.8
    assert mut_res["ortholog_tolerance_detected"] is False


def test_pathway_evolution_and_systems():
    """Module 13: Test cross-species pathway conservation across evolutionary clades."""
    pathway_engine = PathwayEvolutionEngine()

    pw_res = pathway_engine.compare_pathway_conservation("KEGG_04010", "MAPK Signaling Pathway")
    assert pw_res["pathway_id"] == "KEGG_04010"
    assert "conserved_core_elements" in pw_res
    assert len(pw_res["conserved_core_elements"]) >= 4
    assert len(pw_res["vertebrate_expanded_elements"]) >= 3
    assert pw_res["core_conservation_percentage"] > 90.0


def test_evolutionary_target_prioritization():
    """Module 14: Test therapeutic target prioritization balancing conservation and toxicity risk."""
    prioritizer = EvolutionaryTherapeuticPrioritizer()

    target_res = prioritizer.prioritize_target_evolution("BRAF")
    assert target_res["gene_symbol"] == "BRAF"
    assert target_res["is_therapeutically_favored"] is True
    assert 0.0 <= target_res["composite_evolutionary_priority"] <= 1.0

    # Pan-essential POLR2A should not be therapeutically favored
    polr_res = prioritizer.prioritize_target_evolution("POLR2A")
    assert polr_res["is_therapeutically_favored"] is False
    assert target_res["composite_evolutionary_priority"] > polr_res["composite_evolutionary_priority"]


def test_scientific_leakage_and_provenance():
    """Module 15: Test partition auditing (donor/family/species disjoint) and 5-tier provenance."""
    guard = ScientificLeakageGuard()
    tracker = ProvenanceTracker()

    train_data = [{"donor_id": "D1"}, {"donor_id": "D2"}, {"donor_id": "D3"}]
    test_clean = [{"donor_id": "D4"}, {"donor_id": "D5"}]
    test_leaky = [{"donor_id": "D3"}, {"donor_id": "D6"}]

    clean_audit = guard.audit_partitions(train_data, test_clean, "donor_id")
    assert clean_audit["is_leakage_free"] is True
    assert clean_audit["overlap_count"] == 0

    leaky_audit = guard.audit_partitions(train_data, test_leaky, "donor_id")
    assert leaky_audit["is_leakage_free"] is False
    assert leaky_audit["overlap_count"] == 1
    assert "D3" in leaky_audit["overlapping_keys"]

    prov = tracker.create_provenance_envelope(
        analysis_type="target_prioritization",
        result_payload={"target": "BRAF"},
        provenance_tier=EvidenceProvenance.INFERRED,
        dataset_versions=["CPTAC_v3", "UniProt_2024_01"]
    )
    assert prov["provenance_tier"] == EvidenceProvenance.INFERRED.value
    assert prov["is_computational_hypothesis"] is True


def test_moeie_benchmarks_all_passing():
    """Module 16: Test that all 10 MOEIE standardized benchmarks pass at 100%."""
    suite = MOEIEBenchmarkSuite()
    summary = suite.run_all_benchmarks()
    assert summary["status"] == "PASSED"
    assert summary["passed_benchmarks"] == 10
    assert summary["total_benchmarks"] == 10
    assert summary["pass_rate_percent"] == 100.0


def test_moeie_service_and_api():
    """Module 17: Test the MOEIEService singleton API facade."""
    service = MOEIEService()
    assert service is not None

    ortho = service.get_orthology("BRAF")
    assert "ortholog_group" in ortho
    assert "canonical_identity" in ortho

    qc_res = service.run_qc([])
    assert qc_res["total_measurements"] == 0

    benchmarks = service.run_benchmarks()
    assert benchmarks["status"] == "PASSED"
