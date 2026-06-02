# Deep Application Audit - Repository Spring Cleaning Report

Generated: `2026-06-02T09:44:17Z`
Branch: `remediation/phase0-phase1`
Commit: `50227d1820b251be4513732b75e7d1ce390f0392`

## Root Layout Findings

- Tracked root files: `57`.
- Root files outside the proposed allowlist: `20`.
- The repo contains useful material, but the root directory mixes canonical entrypoints, generated docs, historical release scripts, old PR summaries, and transient coverage artifacts.

## Proposed Root Allowlist

Keep root limited to project essentials, package/config files, primary compose files, and top-level documentation that a new contributor needs on day one.

## Root Files To Move Or Archive

| Path | Proposed destination | Reason |
|---|---|---|
| `EDUBOOST_NEXT_BATCH_ALL_OUTSTANDING_TASKS.md` | `audits/reports/ or docs/archive/` | noncanonical root artifact |
| `OUTSTANDING_TODO_ITEMS.md.bak` | `docs/archive/` | backup/superseded document |
| `PR_INTEGRATION_SUMMARY.md` | `audits/reports/ or docs/archive/` | noncanonical root artifact |
| `RoadMap.md` | `docs/archive/roadmaps-or-todos/` | superseded or specialized tracker requiring consolidation |
| `Todo_Production_Grade.md` | `docs/archive/roadmaps-or-todos/` | superseded or specialized tracker requiring consolidation |
| `Todo_Test_Velocity_And_Coverage.md` | `docs/archive/roadmaps-or-todos/` | superseded or specialized tracker requiring consolidation |
| `code_1831_1870_release_go_no_go_status_rollup.sh` | `scripts/archive/` | historical/release batch script |
| `code_1871_1910_beta_blocker_burndown_plan.sh` | `scripts/archive/` | historical/release batch script |
| `db_rollback_test.sql` | `audits/archive/` | operational evidence or temporary data artifact |
| `deploy-eduboost-demo.sh` | `scripts/archive/` | historical/release batch script |
| `deployment_data.md` | `audits/reports/ or docs/archive/` | noncanonical root artifact |
| `docs_gap_report.md` | `docs/generated/documentation_intelligence/` | generated documentation intelligence artifact |
| `docs_generation_plan.md` | `docs/generated/documentation_intelligence/` | generated documentation intelligence artifact |
| `docs_inventory.json` | `docs/generated/documentation_intelligence/` | generated documentation intelligence artifact |
| `docs_inventory.md` | `docs/generated/documentation_intelligence/` | generated documentation intelligence artifact |
| `eduboost_next_batch_all_outstanding_tasks.sh` | `scripts/archive/` | historical/release batch script |
| `prometheus.yml` | `audits/reports/ or docs/archive/` | noncanonical root artifact |
| `setup_redmine_repo.sh` | `scripts/archive/` | historical/release batch script |
| `task_matrix.csv` | `audits/archive/` | operational evidence or temporary data artifact |
| `wsl_copilot.sh` | `scripts/archive/` | historical/release batch script |

## Hygiene Controls Required

- Add a script that fails when generated docs are tracked at root.
- Add a script that fails on tracked cache/coverage artifacts.
- Add a script or Makefile target that reports root files outside the allowlist.
- Keep archive manifests so moved files remain discoverable.
