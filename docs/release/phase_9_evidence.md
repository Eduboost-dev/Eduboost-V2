# Phase 9 Evidence - Coverage, CI, and Evidence Renewal

**Evidence date:** 2026-06-13  
**Status:** Partial; current OpenAPI and CI drift found

## Evidence Sources

- `docs/roadmap/execution/phase_9_execution_plan.md`
- `docs/roadmap/execution/phase_9_implementation_report.md`
- `scripts/generate_openapi.py`
- `.github/workflows/ci-cd.yml`
- `.github/workflows/openapi-contract.yml`
- `docs/release/route_alias_matrix.md`

## Current Passing Evidence

The following current checks passed during the 2026-06-13 traceability audit:

```text
.venv/bin/lint-imports
.venv/bin/python scripts/verify_migration_graph.py
.venv/bin/python scripts/validate_schema_integrity.py
.venv/bin/python scripts/check_runtime_entrypoints.py
```

`check_runtime_entrypoints.py` reported importable v2/legacy app entrypoints.

## Current Failing Evidence

```text
.venv/bin/python scripts/generate_openapi.py --check
# FAIL: OpenAPI drift detected
```

The implementation report references `docs/reference/openapi.json`, but the tracked file found in the current repo is `docs/openapi.json`; `docs/reference/openapi.json` does not exist.

## CI/Workflow Drift

Current workflow inspection found:

- `.github/workflows/ci-cd.yml` defines `schema-drift` twice.
- frontend jobs still use `npm ci` and `package-lock.json` paths in some places, while the frontend declares pnpm and only `app/frontend/pnpm-lock.yaml` exists.
- route compatibility aliases remain documented in `docs/release/route_alias_matrix.md`.

## Verdict

Phase 9 improved evidence and CI scaffolding, but the current repo does not satisfy OpenAPI drift, single-prefix route, or clean CI workflow acceptance criteria.
