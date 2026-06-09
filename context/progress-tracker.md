# Progress Tracker

**Last updated:** 2026-06-09
**Authoritative trackers:** RoadMap.md (17-phase plan), TODO.md (North Star tasks)

Update after every completed RoadMap phase or major TODO milestone.

## Current Status

**Active RoadMap Phase:** Phase 0 (Branch, Evidence, Audit Artifacts) -- in progress
**Last completed:** N/A (RoadMap implementation beginning)
**Next:** Phase 1 (Release-Blocking Correctness Fixes)
**Quality gate:** RED (9/11 checks passing as of 2026-05-17)
**Local unit tests:** 2051 passed, 1 skipped, 1 warning

## RoadMap Phase Progress

### Phase 0 -- Branch, Evidence, and Audit Artifacts (in progress)
- [x] Audit report added (eduboost-v2-technical-audit-2026-06-02.md)
- [x] RoadMap.md created (17 phases)
- [x] Gap analysis added (Eduboost-V2_Gap_Analysis.md)
- [x] TODO.md updated with 5 gap categories + beta period
- [x] Context files updated (this directory)
- [ ] Clean implementation branch from master

### Phase 1 -- Release-Blocking Correctness Fixes
- [ ] 1.1 Fix compileall syntax error in audit_todo_backlog.py
- [ ] 1.1 Add CI compile gate for app and scripts
- [ ] 1.2 Fix all F821 (undefined name) findings
- [ ] 1.2 Add CI Ruff gate: E9,F63,F7,F82,F821

### Phase 2 -- Practice Session Security
- [ ] 2.1 Authenticate practice session continuation routes
- [ ] 2.1 Add tests for unauthorized/wrong-user/consent-denied
- [ ] 2.2 Replace in-memory _SESSIONS with durable storage
- [ ] 2.2 Add expiry and cleanup behavior

### Phase 3 -- Frontend Build Health
- [ ] 3.1 Reconcile frontend dependencies (dexie)
- [ ] 3.2 Fix TypeScript errors
- [ ] 3.3 Fix Vitest TSX parsing (15 failing suites)

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
