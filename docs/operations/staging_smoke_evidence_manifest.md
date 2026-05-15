# Staging Smoke Evidence Manifest

## Metadata

- generated_at_utc: `2026-05-15T18:58:09.759684+00:00`
- branch: `codex/production_readiness`
- commit: `0bac413d3f09cb144fd6b8674f770e725ddc282f`
- target_environment: `test`

## Required Smoke Checks

| Check | Command |
| --- | --- |
| runtime import smoke | `python3 -m py_compile app/api_v2.py` |
| OpenAPI drift smoke | `make openapi-check` |
| staging release gate | `make staging-release-gate-check` |
| release evidence artifacts | `make release-evidence-artifacts-check` |
| Cluster D deployment closure | `make cluster-d-closure-check` |
| Cluster E data resilience closure | `make cluster-e-closure-check` |
| Cluster F AI safety closure | `make cluster-f-closure-check` |
| Cluster G frontend journey closure | `make cluster-g-closure-check` |

## Release Boundary

Staging smoke evidence records required checks. It does not itself prove the
checks were executed unless paired with CI logs or signed release evidence.

## Command

```bash
make staging-smoke-evidence-manifest
```
