"""
PROTEA Phase 10: Mutation & Therapeutic Intelligence Engine (MTIE) - API Router
Provides 17 precision REST endpoints for variants, mutation effects, structural disruption,
interactome rewiring, target discovery, drug intelligence, resistance, combination synergy,
in-silico therapeutic simulation, and ACMG clinical validation.
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel, Field

from services.api.services.mutation_therapeutics_service import MutationTherapeuticsService

router = APIRouter(prefix="/therapeutics", tags=["Mutation & Therapeutic Intelligence (MTIE)"])
service = MutationTherapeuticsService()


# --- Pydantic Request Models ---

class VcfIngestRequest(BaseModel):
    vcf_content: str = Field(..., description="VCF formatted string with variants")


class VariantNormalizeRequest(BaseModel):
    variant: Dict[str, Any] = Field(..., description="Raw GenomicVariant dictionary")


class VariantAnnotateRequest(BaseModel):
    variant: Optional[Dict[str, Any]] = Field(None, description="GenomicVariant dictionary")
    key_hint: Optional[str] = Field(None, description="Lookup key hint, e.g. BRAF_V600E")


class MutationEffectRequest(BaseModel):
    gene_symbol: str = Field(..., example="BRAF")
    wildtype_aa: str = Field(..., example="V")
    position: int = Field(..., example=600)
    mutant_aa: str = Field(..., example="E")


class MutationRewiringRequest(BaseModel):
    gene_symbol: str = Field(..., example="BRAF")
    wildtype_aa: str = Field(..., example="V")
    position: int = Field(..., example=600)
    mutant_aa: str = Field(..., example="E")
    functional_class: Optional[str] = Field("gain_of_function", example="gain_of_function")


class DiseaseMechanismRequest(BaseModel):
    gene_symbol: str = Field(..., example="BRAF")
    mutation_label: str = Field(..., example="BRAF_V600E")


class TargetDiscoveryRequest(BaseModel):
    mutant_gene: str = Field(..., example="BRAF")
    candidate_genes: Optional[List[str]] = Field(None, example=["MAP2K1", "MAP2K2", "EGFR", "MET"])


class DrugDockingRequest(BaseModel):
    drug_id: str = Field(..., example="DRUG_VEMURAFENIB")
    target_id: str = Field(..., example="TGT_BRAF")
    mutation_context: Optional[str] = Field(None, example="BRAF_V600E")


class ResistancePredictRequest(BaseModel):
    mutation_label: str = Field(..., example="EGFR_T790M")
    drug_id: str = Field(..., example="DRUG_GEFITINIB")
    target_id: str = Field(..., example="TGT_EGFR")


class CombinationAnalyzeRequest(BaseModel):
    gene_symbol: str = Field(..., example="BRAF")
    mutation_label: str = Field(..., example="BRAF_V600E")


class SimulationRunRequest(BaseModel):
    mutant_context: str = Field(..., example="BRAF_V600E")
    interventions: List[Dict[str, Any]] = Field(..., example=[{"name": "Dabrafenib"}, {"name": "Trametinib"}])
    duration_hours: float = Field(48.0, example=48.0)


# --- REST Endpoints ---

@router.post("/variants/ingest", summary="Parse and ingest VCF content")
async def ingest_vcf(payload: VcfIngestRequest):
    variants = service.ingest_vcf(payload.vcf_content)
    return {"count": len(variants), "variants": variants}


@router.post("/variants/normalize", summary="Normalize variant coordinates and resolve transcripts")
async def normalize_variant(payload: VariantNormalizeRequest):
    return service.normalize_variant(payload.variant)


@router.post("/variants/annotate", summary="Annotate variant with ClinVar, VEP, dbSNP, gnomAD, and COSMIC")
async def annotate_variant(payload: VariantAnnotateRequest):
    if payload.variant:
        return service.annotate_variant(payload.variant)
    return service.variant_annotator.annotate(key_hint=payload.key_hint)


@router.post("/mutations/predict", summary="Predict missense effect, ESM score, and LoF/GoF functional class")
async def predict_mutation_effect(payload: MutationEffectRequest):
    return service.predict_mutation_effect(
        gene_symbol=payload.gene_symbol,
        wildtype_aa=payload.wildtype_aa,
        position=payload.position,
        mutant_aa=payload.mutant_aa
    )


@router.post("/mutations/structure", summary="Evaluate structural deformation, pLDDT, and interface perturbation")
async def analyze_structure(payload: MutationEffectRequest):
    return service.analyze_structure(
        gene_symbol=payload.gene_symbol,
        wildtype_aa=payload.wildtype_aa,
        position=payload.position,
        mutant_aa=payload.mutant_aa
    )


@router.post("/mutations/stability", summary="Predict DeltaDeltaG folding stability and allosteric pocket distortion")
async def analyze_stability(payload: MutationEffectRequest):
    return service.analyze_stability(
        gene_symbol=payload.gene_symbol,
        wildtype_aa=payload.wildtype_aa,
        position=payload.position,
        mutant_aa=payload.mutant_aa
    )


@router.post("/mutations/rewiring", summary="Predict interactome rewiring (retention, loss, and candidate novel gains)")
async def predict_rewiring(payload: MutationRewiringRequest):
    return service.predict_rewiring(
        gene_symbol=payload.gene_symbol,
        wildtype_aa=payload.wildtype_aa,
        position=payload.position,
        mutant_aa=payload.mutant_aa,
        functional_class=payload.functional_class or "gain_of_function"
    )


@router.post("/disease/mechanisms", summary="Map disrupted pathways and trace causal disease mechanisms")
async def analyze_disease_mechanism(payload: DiseaseMechanismRequest):
    return service.analyze_disease_mechanism(
        gene_symbol=payload.gene_symbol,
        mutation_label=payload.mutation_label
    )


@router.get("/disease/bypass-mechanisms", summary="Retrieve known compensatory and bypass signaling routes")
async def get_bypass_mechanisms(gene_symbol: str = Query(..., description="Target gene symbol, e.g. BRAF")):
    return {"gene_symbol": gene_symbol, "bypass_mechanisms": service.get_bypass_mechanisms(gene_symbol)}


@router.post("/targets/discover", summary="Prioritize therapeutic targets by Centrality, DepMap, Druggability, Safety")
async def discover_targets(payload: TargetDiscoveryRequest):
    targets = service.discover_targets(
        mutant_gene=payload.mutant_gene,
        candidate_genes=payload.candidate_genes
    )
    return {"mutant_gene": payload.mutant_gene, "targets": targets}


@router.get("/targets/{gene_symbol}/druggability", summary="Get target pocket volume and tractability tier")
async def get_druggability(gene_symbol: str):
    return service.get_druggability(gene_symbol)


@router.get("/drugs/search", summary="Search approved and investigational drugs by target or clinical phase")
async def search_drugs(targets: Optional[str] = Query(None, description="Comma-separated target gene symbols")):
    target_list = [t.strip().upper() for t in targets.split(",")] if targets else None
    drugs = service.search_drugs(targets=target_list)
    return {"count": len(drugs), "drugs": drugs}


@router.post("/drugs/docking", summary="Evaluate molecular docking score with caution guardrail disclosure")
async def evaluate_docking(payload: DrugDockingRequest):
    return service.evaluate_docking(
        drug_id=payload.drug_id,
        target_id=payload.target_id,
        mutation_context=payload.mutation_context
    )


@router.post("/resistance/predict", summary="Predict secondary resistance mutations and Hill dose-response shift")
async def predict_resistance(payload: ResistancePredictRequest):
    return service.predict_resistance(
        mutation_label=payload.mutation_label,
        drug_id=payload.drug_id,
        target_id=payload.target_id
    )


@router.post("/combinations/analyze", summary="Analyze multi-metric combination synergy (Bliss, Loewe, HSA, ZIP)")
async def analyze_combinations(payload: CombinationAnalyzeRequest):
    combos = service.analyze_combinations(
        gene_symbol=payload.gene_symbol,
        mutation_label=payload.mutation_label
    )
    return {"combinations": combos}


@router.post("/simulations/run", summary="Simulate dynamic cellular perturbation and verify Pareto optimality")
async def run_simulation(payload: SimulationRunRequest):
    return service.run_simulation(
        mutant_context=payload.mutant_context,
        interventions=payload.interventions,
        duration_hours=payload.duration_hours
    )


@router.post("/validate", summary="Generate ACMG/AMP clinical research validation report and uncertainty bounds")
async def validate_variant(payload: MutationEffectRequest):
    return service.validate_variant(
        gene_symbol=payload.gene_symbol,
        wildtype_aa=payload.wildtype_aa,
        position=payload.position,
        mutant_aa=payload.mutant_aa
    )


@router.get("/benchmarks/run", summary="Execute 9 standardized MTIE scientific research benchmarks")
async def run_benchmarks():
    return service.run_benchmarks()
