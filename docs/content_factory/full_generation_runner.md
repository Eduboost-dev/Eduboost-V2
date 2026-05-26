# Full Generation Runner

## Overview

The Full Generation Runner is an overnight-safe batch generation system that fills all configured Content Factory gaps across all scopes and layers without promoting anything to production or bypassing review.

## Core Rule

Overnight automation may:
- Generate and validate
- Submit valid artifacts to pending_review
- Seed only already-approved artifacts to staging
- Verify staging/readiness

Overnight automation must not:
- Approve, bulk approve, or promote production

Human review stays manual.

## Supported Layers

- diagnostic_items
- lessons
- assessment_blueprints
- study_plan_templates

## Usage

### Plan Only

```bash
python3 scripts/content_factory/run_full_generation.py \
  --all-scopes \
  --layers diagnostic_items,lessons,assessment_blueprints,study_plan_templates \
  --plan-only \
  --write-report
```

### Full Overnight Run

```bash
nohup python3 scripts/content_factory/run_full_generation.py \
  --all-scopes \
  --layers diagnostic_items,lessons,assessment_blueprints,study_plan_templates \
  --max-concurrency 2 \
  --max-artifacts 2000 \
  --budget-cap 50 \
  --resume \
  --seed-approved-to-staging \
  --verify-staging \
  --write-report \
  > reports/content_factory/full_generation_overnight.log 2>&1 &
```

## Configuration

Required environment variables:

```bash
CONTENT_FACTORY_GENERATION_ENABLED=true
CONTENT_FACTORY_PROVIDER=deterministic  # or llm
CONTENT_LEARNER_READ_MODE=production_only
```

Optional configuration:

```bash
CONTENT_FACTORY_MAX_ARTIFACTS_PER_TASK=10
CONTENT_FACTORY_MAX_SCOPE_RUN_ARTIFACTS=250
CONTENT_FACTORY_MAX_FULL_RUN_ARTIFACTS=2000
CONTENT_FACTORY_MAX_CONCURRENCY=2
CONTENT_FACTORY_BUDGET_CAP=50
CONTENT_FACTORY_RETRY_LIMIT=2
CONTENT_FACTORY_FULL_RUN_LOCK_TTL_MINUTES=180
```

## Reports

Reports are written to:

```
reports/content_factory/full_generation/<timestamp>/
```

Artifacts:
- summary.md
- summary.json
- scope_readiness_before.json
- scope_readiness_after.json
- planned_tasks.csv
- executed_tasks.csv
- generated_artifacts.csv
- pending_review.csv
- validation_failed.csv
- source_blockers.csv
- staging_seed_results.csv
- staging_verification.json
- errors.log

## Safety Guarantees

- No learner-visible content is generated or promoted
- No production promotion occurs
- No automatic approval
- Staging preview never exposes learner content
- Lock prevents concurrent full runs
- Budget and artifact caps prevent runaway generation
- Resumable execution handles interruptions
