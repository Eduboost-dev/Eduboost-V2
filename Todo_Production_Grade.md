# Todo Production Grade

Last updated: 2026-06-01
Branch: remediation/phase0-phase1

## Completed So Far

- [x] Sprint 1: settings bootstrap + production compose contract hardening
- [x] Sprint 1: added/validated prod compose contract checks
- [x] Sprint 2: P0 auth/security coverage tranche completed
- [x] Sprint 2: auth router tests expanded to full route-path coverage
- [x] Sprint 2: security helper and jwt keyring runtime paths covered
- [x] Sprint 3: POPIA/consent runtime coverage tranche completed
- [x] Sprint 3: canonical consent service behavior tests added
- [x] Sprint 3: canonical consent repository behavior tests added
- [x] Sprint 3: POPIA data-rights router contract tests added
- [x] Sprint 4: P1 core product coverage
- [x] Sprint 4: content factory service tests added (27 new tests covering ETLProvenanceService, ContentValidationService, stable_json_hash)
- [x] Sprint 4: lesson generation pipeline tests added (9 new tests covering LessonGenerator validation branches)
- [x] Sprint 4: assessment service v2 tests added (8 new tests covering field variants, normalization, edge cases)

## Evidence Snapshot

- Sprint 1 commit: af708814
- Sprint 2 commits: 2dc7cbfd, cf2af16c
- Sprint 3 commit: f6a800d8
- Sprint 4 commits: 5f89a1c8 (POPIA transactional lifecycle), 73c60db0 (content factory + lesson generation), 0634c6cb (assessment service v2)
- Focused module coverage after Sprint 2/3 work:
  - app/api_v2_routers/auth.py: 100%
  - app/core/security.py: 97%
  - app/services/jwt_keyring.py: 99%
  - app/core/token_config.py: 94%
  - app/services/popia_transactional_lifecycle.py: 100%

## Remaining To Reach Production Grade

- [ ] Sprint 5: P1 repository coverage expansion
- [ ] Add direct repository tests with in-memory DB for remaining critical repositories
- [ ] Add integration tests for critical production paths end-to-end
- [ ] Resolve coverage-instrumented collection instability (Table guardians is already defined) and re-run authoritative coverage
- [ ] Raise and stabilize overall backend coverage toward production target (80%+)
- [ ] Final production hardening, release validation, and go/no-go evidence refresh

## Current Risk Notes

- Sprint 1-4 security/compliance coverage foundations are materially improved.
- Core product services (content factory, lesson generation, assessment) now have comprehensive unit test coverage.
- Full production readiness is still blocked by broader product-path coverage and end-to-end release validation.
- Coverage instrumentation run currently has a metadata initialization defect that must be fixed before final authoritative coverage reporting.
