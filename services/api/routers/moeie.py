"""
PROTEA Phase 11: Multi-Omics & Evolution Intelligence Engine (MOEIE) - API Router
Provides comprehensive REST endpoints for multi-omics integration, single-cell dynamics,
spatial biology, regulatory networks, evolutionary genomics, interactome alignment,
and evolution-guided therapeutics.
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel, Field

from services.api.services.moeie_service import MOEIEService

router = APIRouter(prefix="/moeie", tags=["Multi-Omics & Evolution Intelligence (MOEIE)"])
service = MOEIEService()


# --- Pydantic Request Models ---

class DatasetRegisterRequest(BaseModel):
    dataset: Dict[str, Any] = Field(..., description="OmicsDataset dictionary")


class TranscriptomicsIngestRequest(BaseModel):
    name: str = Field(..., description="Dataset name, e.g. Single-Cell Melanoma Cohort")
    matrix: Dict[str, Dict[str, float]] = Field(..., description="Gene -> Sample -> Expression value")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadata dictionary")


class QCRequest(BaseModel):
    measurements: List[Dict[str, Any]] = Field(..., description="List of OmicsMeasurement dictionaries")


class PreprocessRequest(BaseModel):
    measurements: List[Dict[str, Any]] = Field(..., description="List of OmicsMeasurement dictionaries")
    modality: str = Field("transcriptomics", description="Modality to normalize (transcriptomics, proteomics, etc.)")


class LatentRepresentationRequest(BaseModel):
    entity_id: str = Field(..., description="Identifier of the entity (sample, cell, donor)")
    modality_profiles: Dict[str, List[float]] = Field(
        ...,
        description="Dictionary mapping modality name to numerical feature vector"
    )


class CellAnnotationRequest(BaseModel):
    dataset_id: str = Field(..., description="Omics dataset ID")
    detected_genes: List[str] = Field(..., description="List of detected gene symbols")
    total_cells: int = Field(5000, description="Total number of cells in sample")


class TrajectoryRequest(BaseModel):
    populations: List[str] = Field(..., description="Cell population names")
    root_population: str = Field(..., description="Root cell population identifier")


class CommunicationRequest(BaseModel):
    active_populations: List[str] = Field(..., description="Active cell population names")


class SpatialAnalysisRequest(BaseModel):
    sample_id: str = Field(..., description="Biological sample identifier")
    n_spots: int = Field(100, description="Number of spatial capture spots")


class TFActivityRequest(BaseModel):
    expression_profile: Dict[str, float] = Field(..., description="Gene symbol -> expression level mapping")


class DiscordanceRequest(BaseModel):
    rna_expression: Dict[str, float] = Field(..., description="Gene symbol -> RNA abundance")
    protein_abundance: Dict[str, float] = Field(..., description="Gene symbol -> Protein abundance")
    phospho_abundance: Optional[Dict[str, float]] = Field(None, description="Gene symbol -> Phospho abundance")


class NetworkAlignmentRequest(BaseModel):
    query_species: str = Field("Homo sapiens", description="Query organism")
    target_species: str = Field("Mus musculus", description="Target organism")
    subsystem: str = Field("MAPK_Signaling", description="Biological subsystem to align")


class CoverageUncertaintyRequest(BaseModel):
    pair: str = Field(..., description="Interacting protein pair label, e.g. EGFR-GRB2")
    observed_species: List[int] = Field(..., description="Taxonomy IDs where interaction is experimentally observed")
    unobserved_species: List[int] = Field(..., description="Taxonomy IDs where interaction is unobserved")


class PPITransferRequest(BaseModel):
    protein_a: str = Field(..., description="First protein identifier")
    protein_b: str = Field(..., description="Second protein identifier")
    source_taxid: int = Field(9606, description="Source organism NCBI taxonomy ID")
    target_taxid: int = Field(10090, description="Target organism NCBI taxonomy ID")


class EvolutionMutationRequest(BaseModel):
    gene: str = Field(..., description="Gene symbol, e.g. TP53")
    wildtype_aa: str = Field(..., description="Wild-type amino acid")
    position: int = Field(..., description="Residue position")
    mutant_aa: str = Field(..., description="Mutant amino acid")
    esm_score: float = Field(-7.5, description="Protein language model zero-shot log-likelihood ratio")


class PartitionAuditRequest(BaseModel):
    train: List[Dict[str, Any]] = Field(..., description="Training split records")
    test: List[Dict[str, Any]] = Field(..., description="Test split records")
    key: str = Field("donor_id", description="Disjoint partitioning key (donor_id, gene_family, species_taxid)")


# --- REST Endpoints ---

# 1. Dataset Registry & Ingestion
@router.post("/datasets/register", summary="Register an omics dataset in the catalog")
async def register_dataset(payload: DatasetRegisterRequest):
    return service.register_dataset(payload.dataset)


@router.get("/datasets", summary="List registered datasets")
async def list_datasets(modality: Optional[str] = Query(None, description="Optional modality filter")):
    return service.list_datasets(modality=modality)


@router.get("/datasets/{dataset_id}", summary="Retrieve a dataset by ID")
async def get_dataset(dataset_id: str):
    ds = service.get_dataset(dataset_id)
    if not ds:
        raise HTTPException(status_code=404, detail=f"Dataset '{dataset_id}' not found.")
    return ds


@router.post("/datasets/ingest/transcriptomics", summary="Ingest gene expression matrix")
async def ingest_transcriptomics(payload: TranscriptomicsIngestRequest):
    return service.ingest_transcriptomics(payload.name, payload.matrix, payload.metadata)


# 2. Preprocessing & Quality Control
@router.post("/preprocessing/qc", summary="Evaluate multi-omics quality control and batch confounding")
async def run_qc(payload: QCRequest):
    return service.run_qc(payload.measurements)


@router.post("/preprocessing/normalize", summary="Normalize omics measurements preserving raw & corrected data")
async def preprocess_measurements(payload: PreprocessRequest):
    return service.preprocess_measurements(payload.measurements, payload.modality)


# 3. Representation Learning
@router.post("/representations/latent", summary="Compute shared and private latent representations")
async def compute_latent_representation(payload: LatentRepresentationRequest):
    return service.compute_latent_representation(payload.entity_id, payload.modality_profiles)


# 4. Cellular Intelligence
@router.post("/cellular/annotate", summary="Annotate single-cell subpopulations with marker signatures")
async def annotate_cells(payload: CellAnnotationRequest):
    return service.annotate_cells(payload.dataset_id, payload.detected_genes, payload.total_cells)


@router.post("/cellular/trajectory", summary="Infer pseudotime trajectory with scientific caveat")
async def infer_trajectory(payload: TrajectoryRequest):
    return service.infer_trajectory(payload.populations, payload.root_population)


@router.post("/cellular/communication", summary="Infer cell-cell ligand-receptor communication network")
async def infer_communication(payload: CommunicationRequest):
    return service.infer_cell_communication(payload.active_populations)


# 5. Spatial Biology
@router.post("/spatial/tissue", summary="Segment tissue domains and build spatial neighborhood graph")
async def analyze_spatial_tissue(payload: SpatialAnalysisRequest):
    return service.analyze_spatial_tissue(payload.sample_id, payload.n_spots)


@router.get("/spatial/programs", summary="Discover spatial expression programs with Moran's I")
async def discover_spatial_programs():
    return service.discover_spatial_programs()


# 6. Regulatory Intelligence
@router.post("/regulatory/tf-activity", summary="Infer transcription factor activities from expression profile")
async def infer_tf_activity(payload: TFActivityRequest):
    return service.infer_tf_activity(payload.expression_profile)


@router.get("/regulatory/grn/{focal_gene}", summary="Reconstruct gene regulatory network and linked chromatin peaks")
async def reconstruct_grn(focal_gene: str):
    return service.reconstruct_grn(focal_gene)


@router.post("/regulatory/discordance", summary="Analyze RNA vs protein discordance and phospho signaling flux")
async def analyze_discordance(payload: DiscordanceRequest):
    return service.analyze_rna_protein_discordance(
        payload.rna_expression, payload.protein_abundance, payload.phospho_abundance
    )


# 7. Evolutionary Genomics
@router.get("/evolution/orthology/{gene_symbol}", summary="Retrieve cross-species ortholog group")
async def get_orthology(gene_symbol: str):
    return service.get_orthology(gene_symbol)


@router.get("/evolution/conservation/{gene_symbol}", summary="Evaluate sequence conservation and constraint")
async def get_conservation(gene_symbol: str, position: int = Query(1, description="Residue position")):
    return service.evaluate_conservation(gene_symbol, position)


@router.get("/evolution/phylogeny/{gene_symbol}", summary="Build phylogenetic tree and identify evolutionary events")
async def get_phylogeny(gene_symbol: str):
    return service.build_phylogeny(gene_symbol)


# 8. Evolutionary Interactome
@router.post("/evolution/interactome/align", summary="Align cross-species interactomes to detect conserved vs rewired modules")
async def align_interactomes(payload: NetworkAlignmentRequest):
    return service.align_interactomes(payload.query_species, payload.target_species, payload.subsystem)


@router.post("/evolution/interactome/uncertainty", summary="Model coverage-aware absence vs non-observation uncertainty")
async def evaluate_coverage_uncertainty(payload: CoverageUncertaintyRequest):
    return service.evaluate_coverage_uncertainty(payload.pair, payload.observed_species, payload.unobserved_species)


# 9. Evolution-Aware Prediction
@router.post("/evolution/predict/ppi", summary="Predict cross-species PPI transferability")
async def predict_evolutionary_ppi_transfer(payload: PPITransferRequest):
    return service.predict_evolutionary_ppi_transfer(
        payload.protein_a, payload.protein_b, payload.source_taxid, payload.target_taxid
    )


@router.post("/evolution/predict/mutation", summary="Score mutation impact combining evolution constraint and ESM likelihood")
async def predict_evolutionary_mutation(payload: EvolutionMutationRequest):
    return service.predict_evolutionary_mutation(
        payload.gene, payload.wildtype_aa, payload.position, payload.mutant_aa, payload.esm_score
    )


# 10. Systems & Therapeutics
@router.get("/systems/pathway-evolution/{pathway_id}", summary="Compare pathway conservation across evolutionary clades")
async def compare_pathway_evolution(pathway_id: str, pathway_name: str = Query("Path", description="Pathway name")):
    return service.compare_pathway_evolution(pathway_id, pathway_name)


@router.get("/therapeutics/prioritize/{gene}", summary="Prioritize therapeutic target balancing conservation and safety")
async def prioritize_target_evolution(gene: str):
    return service.prioritize_target_evolution(gene)


# 11. Validation & Benchmarks
@router.post("/validation/leakage-audit", summary="Audit dataset partitions for donor/family/species leakage")
async def audit_partitions(payload: PartitionAuditRequest):
    return service.audit_partitions(payload.train, payload.test, payload.key)


@router.get("/benchmarks", summary="Run all 10 MOEIE standardized benchmarks")
async def run_benchmarks():
    return service.run_benchmarks()
