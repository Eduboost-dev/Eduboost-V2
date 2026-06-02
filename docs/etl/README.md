# ETL And Source Evidence

The ETL layer ingests curriculum/source material, normalizes chunks, tracks provenance, and feeds content generation and retrieval.

## Runtime map

- ETL services: `app/services/etl/`
- ETL tools: `tools/etl/`
- ETL admin frontend: `app/frontend/src/components/admin/ETLAdminDashboard.tsx`
- Content Factory integration: `app/services/content_generation/` and `app/services/content_factory_*`

## Current implementation notes

- Full-text retrieval and canonical document storage exist.
- Semantic/vector retrieval remains an open deep-audit finding until full vectors and cosine search are implemented.
- Department of Education scraping evidence must be stored as provenance, not only claimed in generated docs.

## Verification

- `make test-fast` for current unit coverage
- Focused ETL tests under `tests/unit/test_etl_pipeline.py`, `test_phase2_data_pipeline.py`, and content factory tests

Back to the main index: [docs/README.md](../README.md). Root overview: [README.md](../../README.md).
