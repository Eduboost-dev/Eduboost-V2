# Phase 4 Evidence - Runtime and Environment Alignment

**Evidence date:** 2026-06-13  
**Status:** Primary runtime alignment supported; minor workflow drift remains

## Evidence Sources

- `.python-version`
- `docker/Dockerfile.api`
- `docker/Dockerfile.v2`
- `docker/Dockerfile.inference`
- `docs/adr/ADR-026-python-version-alignment.md`
- `.github/workflows/*`

## Current Evidence

```text
.python-version: 3.12.3
docker/Dockerfile.api: FROM python:3.12.3-slim AS base
docker/Dockerfile.v2: FROM python:3.12.3-slim AS base
docker/Dockerfile.inference: FROM python:3.12.3-slim AS builder/runtime
```

ADR-026 records Python 3.12.3 as the chosen runtime for local, Docker, and CI environments.

## Current Drift

The 2026-06-13 audit found these minor alignment issues:

- some GitHub workflows use `python-version: '3.12'` instead of `3.12.3`
- `.github/workflows/migration_check.yml` contains a stale step label saying "Set up Python 3.11" while configuring `3.12.3`

## Verdict

The central Phase 4 implementation is supported, but strict "3.12.3 everywhere" should not be claimed until the remaining workflow selectors/labels are reconciled.
