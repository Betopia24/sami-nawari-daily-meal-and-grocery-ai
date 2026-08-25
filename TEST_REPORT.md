# Test Report

Generated: 2026-08-25

## Executed in this build environment

- Python compile check: **PASS**
- Unit + API tests: **30 passed**
- Docker/live tests skipped locally: **3**
- Application coverage on local unit/API suite: **87%**
- Docker Compose YAML parse validation: **PASS**

Command executed:

```bash
pytest -q -m "not integration and not live" --cov=app --cov-report=term-missing
```

## Included but not executed in this environment

Docker daemon is not available in the artifact-generation environment, so the repository includes Docker integration tests and CI automation for execution on your machine/CI:

```bash
make test-integration
```

That stack starts `pgvector/pgvector:pg16`, Redis, a mock main backend, applies Alembic migrations, and runs the suite against production adapters.

## Optional paid OpenAI smoke test

```bash
RUN_OPENAI_LIVE=1 OPENAI_API_KEY=... pytest -q -m live
```

This is skipped by default to avoid unintended API cost.
