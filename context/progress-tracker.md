# Progress Tracker

**Last updated:** 2026-06-10
**Authoritative trackers:** RoadMap.md (17-phase plan), TODO.md (North Star tasks)

Update after every completed RoadMap phase or major TODO milestone.

## Current Status

**Active RoadMap Phase:** Phase 4 (Runtime and Environment Alignment)
**Last completed:** Phase 3 (Frontend Build and Test Health) - 2026-06-10
**Next:** Phase 4 (Runtime and Environment Alignment)
**Quality gate:** RED (9/11 checks passing as of 2026-05-17)
**Local unit tests:** 2051 passed, 1 skipped, 1 warning

## RoadMap Phase Progress

### Phase 0 -- Branch, Evidence, and Audit Artifacts (complete)
- [x] Audit report added (eduboost-v2-technical-audit-2026-06-02.md)
- [x] RoadMap.md created (17 phases)
- [x] Gap analysis added (Eduboost-V2_Gap_Analysis.md)
- [x] TODO.md updated with 5 gap categories + beta period
- [x] Context files updated (this directory)
- [x] Clean implementation branch from master (phase-1/release-blocking-correctness)

### Phase 1 -- Release-Blocking Correctness Fixes (complete 2026-06-09)
- [x] 1.1 Fix compileall syntax error (no errors found; CI gate verified) in audit_todo_backlog.py
- [x] 1.1 Add CI compile gate for app and scripts (already active in ci-cd.yml)
- [x] 1.2 Fix all F821 (undefined name) findings (0 findings; gate passes)
- [x] 1.2 Add CI Ruff gate: E9,F63,F7,F82,F821 (already active; ~1,000 non-blocking debt in ruff_debt.md)

Evidence: `docs/release/phase_1_evidence.md`, `docs/backlog/ruff_debt.md`

### Phase 2 -- Practice Session Security
- [ ] 2.1 Authenticate practice session continuation routes
- [ ] 2.1 Add tests for unauthorized/wrong-user/consent-denied
- [ ] 2.2 Replace in-memory _SESSIONS with durable storage
- [ ] 2.2 Add expiry and cleanup behavior

### Phase 3 -- Frontend Build Health (complete 2026-06-10)
- [x] 3.1 Reconcile frontend dependencies (dexie) - 651 packages, pnpm install --frozen-lockfile ✅
- [x] 3.2 Fix TypeScript errors - 0 runtime errors, 2 known non-blocking dexie type errors
- [x] 3.3 Fix Vitest TSX parsing - 147/147 tests passing in 26.55s ✅

Evidence: `docs/release/phase_3_evidence.md`, `PHASE_3_EXECUTION_PLAN.md`

### Phases 4-16
See RoadMap.md for full phase plans. This tracker will be updated as phases are executed.

## Verified Baseline (Already Implemented)

These are repository-side complete but need CI/staging/production proof:

- Backend: 2051 unit tests passing, 355 API routes, 28 routers, 22 modules
- Content: 120 Grade 4 Math diagnostic items, 24 lessons live
- POPIA: Consent, audit, erasure, export workflows (partial)
- Auth: JWT + keyring, token revocation, Redis-backed
- ETL: Content Factory pipeline with provenance tracking
- Monitoring: 3 Grafana dashboards, Prometheus metrics, structured logging
- CI/CD: 42 workflow files (many need gate tightening per Phase 9)

## Gap Categories (from Gap Analysis)

| Gap | Category | RoadMap Phase | Status |
|-----|----------|:---:|--------|
| GAP-1 | Technical Debt | Phase 11 | Pending |
| GAP-2 | Security Posture | Phase 12 | Pending |
| GAP-3 | Frontend/Product | Phase 13 | Pending |
| GAP-4 | Operational Readiness | Phase 14 | Pending |
| GAP-5 | Governance/Process | Phase 15 | Pending |
| -- | Beta Period | Phase 16 | Pending |

## Decisions Made During Build

| Date | Decision | Rationale | Reference |
|------|----------|-----------|-----------|
| 2026-05 | V1 deleted, V2 modular monolith | Architecture audit recommendation | CHANGELOG.md |
| 2026-05 | Celery replaced by ARQ | Single-node simplicity, Redis-backed | Phase 6 |
| 2026-05 | Groq primary LLM, Anthropic fallback | Speed + quality balance | .env.example |
| 2026-05 | PostgreSQL audit trail (not RabbitMQ) | Async writes, simpler ops | core/audit.py |
| 2026-06 | 17-phase RoadMap adopted | Gap analysis revealed 5 uncovered categories | RoadMap.md |
| 2026-06 | Python 3.12.3 selected as target | Align with CI and requirements generation | Phase 4 |

## Notes

- All tracking is now dual: RoadMap.md for phases, TODO.md for tasks
- Context files reference both; update them together
- The 5 gap categories (GAP-1 through GAP-5) were identified 2026-06-09
- Beta period (Phase 16) is the final gate before any production claim

| 2026-06-09 | Phase 1 complete (no fixes needed) | Codebase already clean; compileall + ruff gates pass | phase_1_evidence.md |
| 2026-06-09 | ~1,000 Ruff findings deferred to Phase 11 | Only correctness-blocking rules gated; style debt tracked | ruff_debt.md |
