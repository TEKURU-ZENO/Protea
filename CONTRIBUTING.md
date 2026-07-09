# Contributing to PROTEA

Thank you for your interest in contributing to PROTEA! As a research-grade computational interactomics platform, we maintain high standards for code quality, scientific validity, and documentation.

## Development Workflow

1. **Fork the Repository**: Clone the main branch and create your feature branch.
2. **Monorepo Commands**:
   - Install all JS/TS dependencies: `npm install`
   - Run building checks: `npm run build`
   - Spin up infrastructure: `docker compose up -d`
3. **Python Development**:
   - We use `uv` for python package management.
   - Run python formatters and tests before committing:
     - Install requirements via `uv pip install -r services/api/pyproject.toml`
4. **Writing Architecture Decisions (ADRs)**:
   - For major architectural shifts or new model plugins, please document the rationale in `docs/adr/`.

## Scientific Guidelines

If your contribution updates biological algorithms, database schemas, or modeling engines:
- Include unit/integration tests comparing performance against established benchmarks under `benchmarks/`.
- Ensure changes to property graph schemas are reflected in `graph/knowledge_graph/seed_schema.cypher`.
- Reference peer-reviewed literature or models (e.g. ESM-3, Boltz-2) in code comments and pull request descriptions.
