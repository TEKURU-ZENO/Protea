import time
import uuid
import hashlib
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

# Core imports
from services.api.core.config import settings
from services.api.core.logging import logger
from ai.protein_foundation.registry import registry
from ai.protein_foundation.fusion import fusion_registry
from pipelines.preprocessing.fasta_parser import FastaParser
from pipelines.preprocessing.structure_ingestion import PdbParser
from graph.embeddings.qdrant_sync import qdrant_sync
from services.api.core.embedding_cache import embedding_cache
from services.api.core.redis import redis_client

router = APIRouter(prefix="/protein", tags=["Protein Intelligence"])
fasta_parser = FastaParser()
pdb_parser = PdbParser()

# Request schemas
class EmbedRequest(BaseModel):
    sequence: str
    uniprot_id: Optional[str] = "P12345"
    name: Optional[str] = "Unidentified Protein"
    model_name: Optional[str] = "esm2" # esm2 or protbert
    pdb_content: Optional[str] = None # Optional PDB string to run Cross-fusion

class SearchRequest(BaseModel):
    sequence: str
    limit: Optional[int] = 5
    collection: Optional[str] = "proteins_fused"

class CompareRequest(BaseModel):
    sequence_a: str
    sequence_b: str
    model_name: Optional[str] = "esm2"

class BatchIngestRequest(BaseModel):
    fasta_content: str
    model_name: Optional[str] = "esm2"

# MLflow telemetry logging helper
def log_to_mlflow(metrics: Dict[str, float], params: Dict[str, Any]):
    try:
        # Just logging local trace telemetry. If MLflow client is installed, 
        # it can be imported and push parameters/metrics.
        logger.info(f"[MLflow Telemetry] Logging Run - Params: {params} - Metrics: {metrics}")
    except Exception as e:
        logger.warning(f"Failed to record metrics in MLflow: {e}")

# Process batch worker
async def process_batch_job(job_id: str, fasta_content: str, model_name: str):
    r = redis_client.client
    if r:
        await r.set(f"batch_job:{job_id}:status", "processing", ex=3600)

    try:
        entries = fasta_parser.parse_string(fasta_content)
        success_count = 0
        
        for entry in entries:
            seq = entry["sequence"]
            u_id = entry["id"]
            
            # Fetch embedding
            adapter = registry.get(model_name)
            emb_res = await embedding_cache.get_embedding(seq, model_name)
            
            if not emb_res:
                emb_res = adapter.embed(seq)
                await embedding_cache.set_embedding(seq, model_name, emb_res)
            
            # Sync to Qdrant
            vector = emb_res["pooled"].tolist()
            qdrant_sync.upsert_protein(
                collection_name=f"proteins_{model_name.lower()}",
                uniprot_id=u_id,
                vector=vector,
                payload={
                    "uniprot_id": u_id,
                    "name": entry["name"],
                    "length": entry["length"],
                    "organism": entry["organism"],
                    "gene": entry["gene"],
                    "model": model_name
                }
            )
            success_count += 1
            
        if r:
            await r.set(f"batch_job:{job_id}:status", "completed", ex=3600)
            await r.set(f"batch_job:{job_id}:results", json.dumps({"processed": success_count, "total": len(entries)}), ex=3600)
            
    except Exception as e:
        logger.error(f"Batch ingestion job {job_id} failed: {e}")
        if r:
            await r.set(f"batch_job:{job_id}:status", "failed", ex=3600)

@router.post("/embed")
async def get_embeddings(payload: EmbedRequest):
    """Tokenizes and returns sequence and structural fused representations."""
    start_time = time.time()
    seq = payload.sequence.strip()
    
    if len(seq) == 0:
        raise HTTPException(status_code=400, detail="Protein sequence is empty.")
        
    model_name = payload.model_name.lower()
    
    # 1. Redis Cache check
    cache_hit = True
    emb_data = await embedding_cache.get_embedding(seq, model_name)
    
    if not emb_data:
        cache_hit = False
        try:
            adapter = registry.get(model_name)
            emb_data = adapter.embed(seq)
            # Write back to cache
            await embedding_cache.set_embedding(seq, model_name, emb_data)
        except Exception as e:
            logger.error(f"Inference execution failed: {e}")
            raise HTTPException(status_code=500, detail=f"Inference engine failure: {e}")

    # 2. Structural Parsing & Fusion if PDB content supplied
    fused_vector = None
    struct_meta = {}
    fused_status = "none"
    
    if payload.pdb_content:
        try:
            struct_feat = pdb_parser.parse_string(payload.pdb_content)
            struct_meta = {
                "num_residues": struct_feat["num_residues"],
                "secondary_structure_summary": struct_feat["secondary_structure"][:10]
            }
            # Run pluggable cross-attention fusion strategy
            strategy = fusion_registry.get("cross_attention")
            fused_arr = strategy.fuse(emb_data["per_residue"], struct_feat)
            fused_vector = np.mean(fused_arr, axis=0).tolist()
            fused_status = "cross_attention_fused"
            
            # Sync fused representation to Qdrant
            qdrant_sync.upsert_protein(
                collection_name="proteins_fused",
                uniprot_id=payload.uniprot_id,
                vector=fused_vector,
                payload={
                    "uniprot_id": payload.uniprot_id,
                    "name": payload.name,
                    "length": len(seq),
                    "model": "fused_cross_attention"
                }
            )
        except Exception as e:
            logger.warning(f"Structural fusion bypassed due to parser error: {e}")
            
    # Sync original representation to Qdrant
    qdrant_sync.upsert_protein(
        collection_name=f"proteins_{model_name}",
        uniprot_id=payload.uniprot_id,
        vector=emb_data["pooled"].tolist(),
        payload={
            "uniprot_id": payload.uniprot_id,
            "name": payload.name,
            "length": len(seq),
            "model": model_name
        }
    )

    elapsed = time.time() - start_time
    
    # 3. Log metrics to MLflow
    log_to_mlflow(
        metrics={"inference_time_seconds": elapsed, "sequence_length": len(seq)},
        params={"model": model_name, "cache_hit": cache_hit, "fused": fused_status}
    )

    return {
        "uniprot_id": payload.uniprot_id,
        "name": payload.name,
        "sequence_length": len(seq),
        "model_used": model_name,
        "embedding_dimension": len(emb_data["pooled"]),
        "cache_status": "hit" if cache_hit else "miss",
        "fused_status": fused_status,
        "pooled_vector_preview": emb_data["pooled"][:5].tolist(), # Preview first few numbers
        "structure_summary": struct_meta
    }

@router.post("/search")
async def search_protein(payload: SearchRequest):
    """Finds nearest neighbor proteins based on query sequence."""
    adapter = registry.get("esm2") # Default to ESM2 representation
    emb_data = adapter.embed(payload.sequence)
    query_vector = emb_data["pooled"].tolist()
    
    # Run KNN query
    nearest = qdrant_sync.search_nearest(
        collection_name=payload.collection,
        query_vector=query_vector,
        limit=payload.limit
    )
    return {"query_length": len(payload.sequence), "results": nearest}

@router.post("/nearest")
async def get_nearest(payload: SearchRequest):
    """Retrieve nearest protein vectors in the database."""
    return await search_protein(payload)

@router.post("/compare")
async def compare_proteins(payload: CompareRequest):
    """Computes cosine similarity between two sequence embeddings."""
    adapter = registry.get(payload.model_name)
    emb_a = adapter.embed(payload.sequence_a)["pooled"]
    emb_b = adapter.embed(payload.sequence_b)["pooled"]
    
    # Cosine similarity
    dot = np.dot(emb_a, emb_b)
    norm_a = np.linalg.norm(emb_a)
    norm_b = np.linalg.norm(emb_b)
    similarity = float(dot / (norm_a * norm_b)) if (norm_a > 0 and norm_b > 0) else 0.0
    
    return {
        "cosine_similarity": similarity,
        "model_used": payload.model_name
    }

@router.post("/similarity")
async def get_similarity(payload: CompareRequest):
    return await compare_proteins(payload)

@router.post("/ingest-batch")
async def ingest_batch(payload: BatchIngestRequest, background_tasks: BackgroundTasks):
    """Queues a batch FASTA ingestion job to process asynchronously."""
    job_id = str(uuid.uuid4())
    
    r = redis_client.client
    if r:
        await r.set(f"batch_job:{job_id}:status", "queued", ex=3600)
        
    # Queue execution
    background_tasks.add_task(
        process_batch_job,
        job_id,
        payload.fasta_content,
        payload.model_name
    )
    
    return {
        "job_id": job_id,
        "status": "queued",
        "message": "Batch ingestion job added successfully to queue. Check status via Redis."
    }

import json
import numpy as np
