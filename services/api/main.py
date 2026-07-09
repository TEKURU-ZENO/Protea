import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response

# Import core configurations and database managers
from services.api.core.config import settings
from services.api.core.logging import logger
from services.api.core.postgres import postgres_client
from services.api.core.neo4j import neo4j_client
from services.api.core.redis import redis_client
from services.api.core.vector_db import qdrant_client
from services.api.core.storage import storage_client

# Import sub-routers
from services.api.routers import (
    system, graph, protein, interaction, pathway, simulation, twins, agents
)

# Metrics definitions
REQUEST_COUNT = Counter(
    "http_requests_total", "Total HTTP requests", ["method", "endpoint", "status"]
)
REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds", "HTTP request latency", ["endpoint"]
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize all database connections
    logger.info("Initializing PROTEA platform services...")
    
    # 1. Postgres
    try:
        await postgres_client.connect()
    except Exception as e:
        logger.warning(f"Lifespan Postgres connection failed (ignoring for bootstrap): {e}")

    # 2. Neo4j
    try:
        neo4j_client.connect()
    except Exception as e:
        logger.warning(f"Lifespan Neo4j connection failed (ignoring for bootstrap): {e}")

    # 3. Redis
    try:
        await redis_client.connect()
    except Exception as e:
        logger.warning(f"Lifespan Redis connection failed (ignoring for bootstrap): {e}")

    # 4. Qdrant
    try:
        qdrant_client.connect()
    except Exception as e:
        logger.warning(f"Lifespan Qdrant connection failed (ignoring for bootstrap): {e}")

    # 5. MinIO Storage
    try:
        storage_client.connect()
    except Exception as e:
        logger.warning(f"Lifespan S3/MinIO connection failed (ignoring for bootstrap): {e}")

    logger.info("PROTEA platform services initialization completed.")
    yield
    
    # Shutdown: Disconnect databases
    logger.info("Shutting down PROTEA platform services...")
    await postgres_client.disconnect()
    neo4j_client.disconnect()
    await redis_client.disconnect()
    qdrant_client.disconnect()
    logger.info("PROTEA platform services offline.")

app = FastAPI(
    title="PROTEA Platform API",
    description="REST/GraphQL Gateway for Protein Relational Organism-wide Topology & Evolutionary Analytics",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS Middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request logger/metrics middleware
@app.middleware("http")
async def monitor_requests(request: Request, call_next):
    start_time = time.time()
    endpoint = request.url.path
    method = request.method
    
    try:
        response = await call_next(request)
        status_code = str(response.status_code)
        return response
    except Exception as e:
        status_code = "500"
        raise e
    finally:
        latency = time.time() - start_time
        REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=status_code).inc()
        REQUEST_LATENCY.labels(endpoint=endpoint).observe(latency)

# API Version 1 Routers mounting
api_v1_prefix = "/api/v1"
app.include_router(system.router, prefix=api_v1_prefix)
app.include_router(graph.router, prefix=api_v1_prefix)
app.include_router(protein.router, prefix=api_v1_prefix)
app.include_router(interaction.router, prefix=api_v1_prefix)
app.include_router(pathway.router, prefix=api_v1_prefix)
app.include_router(simulation.router, prefix=api_v1_prefix)
app.include_router(twins.router, prefix=api_v1_prefix)
app.include_router(agents.router, prefix=api_v1_prefix)

# --- Kubernetes-ready Health Checks & Observability ---

@app.get("/health", tags=["Health"])
async def get_health():
    """General aggregated health check."""
    return {"status": "ok", "timestamp": time.time()}

@app.get("/liveness", tags=["Health"])
async def get_liveness():
    """Liveness probe - checks if API process is up."""
    return {"status": "alive"}

@app.get("/readiness", tags=["Health"])
async def get_readiness():
    """Readiness probe - checks database connection states."""
    db_states = {
        "postgres": await postgres_client.check_health(),
        "neo4j": neo4j_client.check_health(),
        "redis": await redis_client.check_health(),
        "qdrant": qdrant_client.check_health(),
        "minio": storage_client.check_health(),
    }
    
    # Degraded or ready check
    ready = all(db_states.values())
    status = "ready" if ready else "degraded"
    
    return {
        "status": status,
        "timestamp": time.time(),
        "services": db_states
    }

@app.get("/metrics", tags=["Observability"])
def get_metrics():
    """Exposes Prometheus scraper metrics."""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
