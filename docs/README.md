# EduBoost V2 Documentation Index

Last updated: 2026-06-02

This is the authoritative entry point for EduBoost engineering documentation. The corpus still contains historical and generated evidence, so start from the domain indexes below before browsing individual reports.

## Authoritative Domain Indexes

| Area | Current index |
|---|---|
| Backend | [backend/README.md](backend/README.md) |
| Frontend | [frontend/README.md](frontend/README.md) |
| Diagnostics and assessment | [diagnostics/README.md](diagnostics/README.md) |
| IRT engine | [irt/README.md](irt/README.md) |
| ETL and source evidence | [etl/README.md](etl/README.md) |
| POPIA and data rights | [popia/README.md](popia/README.md) |
| Security | [security/README.md](security/README.md) |
| Testing | [testing/README.md](testing/README.md) |
| Deployment and operations | [deployment/README.md](deployment/README.md) |
| Roadmap | [roadmap/README.md](roadmap/README.md) |

## Live Project State

- Root overview: [../README.md](../README.md)
- Live tracker: [../TODO.md](../TODO.md)
- Deep audit baseline: [../audits/deep_app_audit/implementation_reality_report.md](../audits/deep_app_audit/implementation_reality_report.md)
- Documentation consolidation report: [../audits/deep_app_audit/documentation_consolidation_report.md](../audits/deep_app_audit/documentation_consolidation_report.md)
- Repository cleanup report: [../audits/deep_app_audit/repository_spring_cleaning_report.md](../audits/deep_app_audit/repository_spring_cleaning_report.md)

## Documentation Rules

- Human-authored domain READMEs are the preferred current references.
- Generated inventories and reports belong under `docs/generated/`.
- Historical or superseded roadmap/TODO material belongs under `docs/archive/` with a manifest.
- Release evidence must not claim production readiness unless runtime, CI, staging, and external approval evidence exist.

## Discovery

Use `git grep -l "<topic>" docs/ audits/` when a topic is not linked here. Missing authoritative coverage is itself an audit finding.
