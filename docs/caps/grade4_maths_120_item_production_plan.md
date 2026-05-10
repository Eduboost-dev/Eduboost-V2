# Grade 4 Mathematics 120-Item Production Plan

This document reflects the current repository state after the CAPS item-bank
phase integration. The code, seed tooling, validation tooling, CI gates, and
observability assets are integrated. The item content bank is not yet at the
production target.

## Current State

| CAPS Ref | Topic | Approved Now | Production Target | Outstanding |
| --- | --- | ---: | ---: | ---: |
| `4.M.1.1` | Whole Numbers | 4 | 40 | 36 |
| `4.M.1.2` | Common Fractions | 5 | 40 | 35 |
| `4.M.1.3` | 2D Shapes | 5 | 40 | 35 |
| **Total** |  | **14** | **120** | **106** |

Current validation status:

- `scripts/validate_item_bank.py --path data/caps/grade4_maths_item_bank.json --fail-on-any-error` passes for the 14 approved starter items.
- Production CI thresholds are intentionally configurable until the content bank reaches 120 approved items.
- Enable production thresholds with `ITEM_BANK_MIN_APPROVED=40` and `ITEM_BANK_MIN_APPROVED_TOTAL=120`.

## Required Difficulty Distribution

Each CAPS ref needs this final distribution:

| Band | b-parameter range | Target per CAPS ref |
| --- | --- | ---: |
| Easy | `b < -1.0` | 10 |
| Moderate | `-1.0 <= b < 0.0` | 12 |
| On-level | `0.0 <= b < 1.0` | 12 |
| Challenging | `b >= 1.0` | 6 |

Outstanding by band:

| CAPS Ref | Easy | Moderate | On-level | Challenging | Total Needed |
| --- | ---: | ---: | ---: | ---: | ---: |
| `4.M.1.1` | 7 | 11 | 12 | 6 | 36 |
| `4.M.1.2` | 10 | 9 | 10 | 6 | 35 |
| `4.M.1.3` | 9 | 10 | 10 | 6 | 35 |

## Batch Execution Plan

Generate more candidates than the exact gap so validation and review can reject
weak items without dropping below target. Aim for roughly 1.5x the outstanding
count per band.

1. Generate Whole Numbers candidates:
   - `4.M.1.1 easy`: generate 11 candidates to approve 7.
   - `4.M.1.1 moderate`: generate 17 candidates to approve 11.
   - `4.M.1.1 on_level`: generate 18 candidates to approve 12.
   - `4.M.1.1 challenging`: generate 9 candidates to approve 6.

2. Generate Common Fractions candidates:
   - `4.M.1.2 easy`: generate 15 candidates to approve 10.
   - `4.M.1.2 moderate`: generate 14 candidates to approve 9.
   - `4.M.1.2 on_level`: generate 15 candidates to approve 10.
   - `4.M.1.2 challenging`: generate 9 candidates to approve 6.

3. Generate 2D Shapes candidates:
   - `4.M.1.3 easy`: generate 14 candidates to approve 9.
   - `4.M.1.3 moderate`: generate 15 candidates to approve 10.
   - `4.M.1.3 on_level`: generate 15 candidates to approve 10.
   - `4.M.1.3 challenging`: generate 9 candidates to approve 6.

Example command:

```bash
make generate-items CAPS_REF=4.M.1.1 N=18 BAND=on_level
```

## Acceptance Gates

Run these after every generation batch:

```bash
make validate-items
python scripts/assign_irt_params.py
make seed-items
```

Once the seed file reaches 120 approved items, run the production gates:

```bash
ITEM_BANK_MIN_APPROVED=40 make coverage-gate
ITEM_BANK_MIN_APPROVED_TOTAL=120 python -m pytest tests/ci/test_item_bank_ci_jobs.py::TestCISeedValidation -q --no-cov
make coverage-matrix
```

## Human Review Criteria

An item may be marked `approved` only when all checks pass:

- The answer key is unambiguously correct.
- At least four MCQ options are present.
- Every wrong option has a plausible distractor rationale.
- The stem is Grade 4 readable and CAPS-aligned.
- The item uses safe, generic South African context with no PII or brand names.
- `reviewer_id`, `reviewed_at`, `safety_passed`, and `quality_score` are populated.
- Misconception tags are useful for lesson remediation.

## Production Completion Definition

The Grade 4 Mathematics item bank can be called production-complete only when:

- `4.M.1.1`, `4.M.1.2`, and `4.M.1.3` each have at least 40 approved items.
- Total approved items are at least 120.
- `validate_item_bank.py` reports zero failures for all approved items.
- Production CI thresholds are enabled and passing.
- The coverage matrix has been regenerated from the seeded database.
- The release evidence bundle records the real approved counts.
