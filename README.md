# PROTEA: An AI-Native Computational Interactomics Platform

PROTEA (Protein Relational Organism-wide Topology & Evolutionary Analytics) is an AI-first, research-grade computational interactomics platform designed to model biological networks, protein structure, pathway semantics, cell simulations, and multi-agent scientific discovery.

## Repository Architecture

The codebase is organized as a Turborepo-managed monorepo structured for high scalability, scientific computing, and modular expansion:

```
PROTEA/
├── apps/                 # Web, Desktop, Mobile, and Docs applications
│   └── web/              # Biological Discovery Studio (Next.js 15 / React 19)
├── packages/             # Shared TypeScript packages (types, eslint, tsconfig)
├── platform/             # Infrastructure layers (auth, telemetry, orchestration, events)
├── services/             # API gateways and microservices (FastAPI backend)
├── ai/                   # AI/ML models (embeddings, GNNs, diffusion, simulation)
├── graph/                # Biological knowledge graph queries, cypher, and GDS algorithms
├── simulation/           # Numerical and Neural ODE solvers
├── agents/               # Swarm orchestrator and domain-expert agents
├── feature_store/        # Dynamic molecular and node features
├── models/               # Weights registry (foundation, trained, experimental)
├── plugins/              # Core extensibility hooks (AlphaFold, ESM3, Chai)
├── sdk/                  # TS/Python client libraries for programmatic execution
├── datasets/             # Local database cache and registry (versioned metadata)
├── pipelines/            # Ingestion, preprocessing, and training pipelines
├── events/               # Event bus publishers/subscribers (Kafka schemas)
├── docs/                 # Platform architecture, ADRs, and research docs
├── research/             # Scientific notebooks and paper publications
├── benchmarks/           # Standardized model evaluation pipelines
├── infrastructure/       # Docker Compose, Kubernetes manifests, and Terraform
├── configs/              # Global application configuration
└── shared/               # Cross-component configurations, types, and schemas
```

## Quick Start (Phase 1)

### Prerequisites

Ensure you have the following installed:

- [Docker & Docker Compose](https://www.docker.com/)
- [Node.js (v18+)](https://nodejs.org/)
- [uv (Python package installer/manager)](https://github.com/astral-sh/uv)

### Launching the Stack

1. **Clone & Install Node Dependencies**:

   ```bash
   npm install
   ```

2. **Start Infrastructure & Backend/Frontend Services**:

   ```bash
   docker compose up --build
   ```

3. **Verify running components**:
   - Biological Discovery Studio: `http://localhost:3000`
   - FastAPI REST API Gateway: `http://localhost:8000/docs`
   - Neo4j Browser: `http://localhost:7474`
   - Qdrant Vector Dashboard: `http://localhost:6333/dashboard`
   - MinIO Object Storage Console: `http://localhost:9001`
   - MLflow Dashboard: `http://localhost:5000`
   - Grafana Metrics Panel: `http://localhost:3001`
