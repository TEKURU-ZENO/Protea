"""
PROTEA Multi-Omics & Evolution Intelligence Engine (MOEIE) - Service Layer
Encapsulates all Phase 11 multi-omics, single-cell, spatial, and evolutionary systems biology logic.
"""

from typing import Dict, Any, List, Optional
from ai.moeie.schema import (
    OmicsDataset,
    BiologicalSample,
    OmicsMeasurement,
    OmicsModality,
    EvidenceProvenance,
    ConservationTier
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


class MOEIEService:
    """Singleton service orchestrating the Multi-Omics & Evolution Intelligence Engine."""

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(MOEIEService, cls).__new__(cls, *args, **kwargs)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return

        self.registry = DatasetRegistry()
        self.adapters = ModalityIngestionAdapters()
        self.identifier_resolver = CrossSpeciesIdentifierResolver()
        self.normalizer = MultiOmicsNormalizer()
        self.qc_engine = QualityControlEngine()
        self.latent_model = SharedPrivateLatentModel(shared_dim=16, private_dim=8)
        self.aligner = CrossModalAligner()
        self.cell_annotation = CellAnnotationEngine()
        self.trajectory_engine = TrajectoryEngine()
        self.cell_communication = CellCommunicationEngine()
        self.spatial_graph = SpatialGraphEngine()
        self.spatial_programs = SpatialProgramEngine()
        self.tf_engine = TFActivityInferenceEngine()
        self.grn_engine = GRNReconstructionEngine()
        self.discordance_analyzer = ProteinRNADiscordanceAnalyzer()
        self.orthology_engine = OrthologyInferenceEngine()
        self.conservation_engine = SequenceConservationEngine()
        self.phylogeny_engine = PhylogeneticEngine()
        self.cross_species_mapping = CrossSpeciesMappingEngine()
        self.network_alignment = NetworkAlignmentEngine()
        self.coverage_estimator = CoverageUncertaintyEstimator()
        self.evolution_ppi_transfer = EvolutionPPITransferEngine()
        self.evolution_mutation = EvolutionMutationPredictor()
        self.pathway_evolution = PathwayEvolutionEngine()
        self.therapeutic_prioritizer = EvolutionaryTherapeuticPrioritizer()
        self.leakage_guard = ScientificLeakageGuard()
        self.provenance_tracker = ProvenanceTracker()
        self.benchmark_suite = MOEIEBenchmarkSuite()

        self._initialized = True

    # 1. Dataset Ingestion & Management
    def register_dataset(self, dataset_dict: Dict[str, Any]) -> Dict[str, Any]:
        dataset = OmicsDataset.from_dict(dataset_dict)
        registered = self.registry.register_dataset(dataset)
        return registered.to_dict()

    def get_dataset(self, dataset_id: str) -> Optional[Dict[str, Any]]:
        ds = self.registry.get_dataset(dataset_id)
        return ds.to_dict() if ds else None

    def list_datasets(self, modality: Optional[str] = None) -> List[Dict[str, Any]]:
        mod_enum = OmicsModality(modality) if modality else None
        datasets = self.registry.list_datasets(mod_enum)
        return [d.to_dict() for d in datasets]

    def ingest_transcriptomics(
        self,
        name: str,
        matrix: Dict[str, Dict[str, float]],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        res = self.adapters.ingest_transcriptomics(name, matrix, metadata)
        self.registry.register_dataset(res["dataset"])
        return {
            "dataset": res["dataset"].to_dict(),
            "sample_ids": res["sample_ids"],
            "features_count": res["features_count"],
            "measurements_count": res["measurements_count"]
        }

    # 2. Preprocessing & Quality Control
    def run_qc(self, measurements_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        measurements = [OmicsMeasurement.from_dict(m) for m in measurements_data]
        return self.qc_engine.evaluate_quality(measurements)

    def preprocess_measurements(
        self,
        measurements_data: List[Dict[str, Any]],
        modality: str = "transcriptomics"
    ) -> List[Dict[str, Any]]:
        measurements = [OmicsMeasurement.from_dict(m) for m in measurements_data]
        mod_enum = OmicsModality(modality)
        norm_list = self.normalizer.normalize_measurements(measurements, mod_enum)
        return [m.to_dict() for m in norm_list]

    # 3. Representation Learning
    def compute_latent_representation(
        self,
        entity_id: str,
        modality_profiles: Dict[str, List[float]]
    ) -> Dict[str, Any]:
        latent_rep = self.latent_model.encode(entity_id, modality_profiles)
        return latent_rep.to_dict()

    # 4. Cellular Intelligence
    def annotate_cells(
        self,
        dataset_id: str,
        detected_genes: List[str],
        total_cells: int = 5000
    ) -> List[Dict[str, Any]]:
        populations = self.cell_annotation.annotate_subpopulations(dataset_id, detected_genes, total_cells)
        return [p.to_dict() for p in populations]

    def infer_trajectory(self, populations: List[str], root_population: str) -> Dict[str, Any]:
        return self.trajectory_engine.infer_trajectory(populations, root_population)

    def infer_cell_communication(self, active_populations: List[str]) -> Dict[str, Any]:
        return self.cell_communication.infer_communication_network(active_populations)

    # 5. Spatial Intelligence
    def analyze_spatial_tissue(self, sample_id: str, n_spots: int = 100) -> Dict[str, Any]:
        regions = self.spatial_graph.segment_tissue_domains(sample_id, n_spots)
        coords = [(r.x_microns, r.y_microns) for r in regions]
        graph = self.spatial_graph.build_spatial_neighborhood_graph(coords)
        return {
            "sample_id": sample_id,
            "total_regions": len(regions),
            "regions": [r.to_dict() for r in regions],
            "neighborhood_graph": graph
        }

    def discover_spatial_programs(self) -> List[Dict[str, Any]]:
        return self.spatial_programs.discover_spatial_programs()

    # 6. Regulatory Intelligence
    def infer_tf_activity(self, expression_profile: Dict[str, float]) -> List[Dict[str, Any]]:
        return self.tf_engine.infer_tf_activity(expression_profile)

    def reconstruct_grn(self, focal_gene: str) -> Dict[str, Any]:
        grn = self.grn_engine.reconstruct_local_network(focal_gene)
        chromatin_links = self.grn_engine.link_chromatin_to_genes(focal_gene)
        return {
            "gene_regulatory_network": grn,
            "chromatin_peaks": chromatin_links
        }

    def analyze_rna_protein_discordance(
        self,
        rna_expression: Dict[str, float],
        protein_abundance: Dict[str, float],
        phospho_abundance: Optional[Dict[str, float]] = None
    ) -> List[Dict[str, Any]]:
        return self.discordance_analyzer.analyze_discordance(rna_expression, protein_abundance, phospho_abundance)

    # 7. Evolutionary Genomics
    def get_orthology(self, gene_symbol: str) -> Dict[str, Any]:
        og = self.orthology_engine.get_ortholog_group(gene_symbol)
        canonical = self.identifier_resolver.resolve_identifier(gene_symbol)
        return {
            "ortholog_group": og.to_dict(),
            "canonical_identity": canonical.to_dict()
        }

    def evaluate_conservation(self, gene_symbol: str, position: int) -> Dict[str, Any]:
        residue_res = self.conservation_engine.evaluate_residue_conservation(gene_symbol, position)
        constraint = self.conservation_engine.get_gene_constraint_metrics(gene_symbol)
        return {
            "residue_conservation": residue_res,
            "gene_constraint": constraint
        }

    def build_phylogeny(self, gene_symbol: str) -> Dict[str, Any]:
        tree = self.phylogeny_engine.build_tree(gene_symbol)
        events = self.phylogeny_engine.infer_evolutionary_events(gene_symbol)
        return {
            "phylogenetic_tree": tree.to_dict(),
            "evolutionary_events": [e.to_dict() for e in events]
        }

    # 8. Evolutionary Interactome
    def align_interactomes(self, query_species: str, target_species: str, subsystem: str) -> Dict[str, Any]:
        analysis = self.network_alignment.align_interactomes(query_species, target_species, subsystem)
        modules = self.network_alignment.get_evolutionary_modules()
        return {
            "comparative_analysis": analysis.to_dict(),
            "evolutionary_modules": [m.to_dict() for m in modules]
        }

    def evaluate_coverage_uncertainty(
        self,
        pair: str,
        observed: List[int],
        unobserved: List[int]
    ) -> Dict[str, Any]:
        return self.coverage_estimator.evaluate_conservation_with_coverage(pair, observed, unobserved)

    # 9. Evolution-Aware Prediction
    def predict_evolutionary_ppi_transfer(
        self,
        protein_a: str,
        protein_b: str,
        source_taxid: int = 9606,
        target_taxid: int = 10090
    ) -> Dict[str, Any]:
        return self.evolution_ppi_transfer.predict_cross_species_transfer(
            protein_a, protein_b, source_taxid, target_taxid
        )

    def predict_evolutionary_mutation(
        self,
        gene: str,
        wt: str,
        pos: int,
        mut: str,
        esm_score: float = -7.5
    ) -> Dict[str, Any]:
        return self.evolution_mutation.predict_evolutionary_impact(gene, wt, pos, mut, esm_score)

    # 10. Systems & Therapeutics
    def compare_pathway_evolution(self, pathway_id: str, pathway_name: str) -> Dict[str, Any]:
        return self.pathway_evolution.compare_pathway_conservation(pathway_id, pathway_name)

    def prioritize_target_evolution(self, gene: str) -> Dict[str, Any]:
        return self.therapeutic_prioritizer.prioritize_target_evolution(gene)

    # 11. Validation & Benchmarks
    def audit_partitions(self, train: List[Dict[str, Any]], test: List[Dict[str, Any]], key: str = "donor_id") -> Dict[str, Any]:
        return self.leakage_guard.audit_partitions(train, test, key)

    def run_benchmarks(self) -> Dict[str, Any]:
        return self.benchmark_suite.run_all_benchmarks()
