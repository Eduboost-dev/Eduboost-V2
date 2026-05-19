# Beta Blocker Burn-Down Plan

Generated at: `2026-05-19T14:54:48Z`
Commit: `c01648dd42d169b26a7bf6daa2295efa9a75c629`

- Source decision: `NO-GO`
- Source beta blocker count: `6`
- Burn-down status: `blocked`
- Release mode allowed: `False`

## Ordered blocker actions

| Priority | ID | Category | Owner | Status | Local close? | Next action | Verification |
|---|---|---|---|---|---:|---|---|
| `P0` | `CI-001` | `ci-authority` | `release` | `external-blocked` | False | Attach a passing GitHub Actions run URL for codex/production_readiness, then rerun CI authority release check. | `make ci-authority-release-check` |
| `P0` | `CONTENT-001` | `content` | `content` | `external-blocked` | False | Obtain educator/content approval for beta scope and replace pending metadata in content_approval.md. | `make external-approval-release-check` |
| `P0` | `EXT-GATE-001` | `external` | `release` | `runtime-passing` | False | Resolve registry blocker: external approval remains incomplete | `make external-approval-release-check` |
| `P0` | `LEGAL-001` | `legal` | `legal` | `external-blocked` | False | Obtain POPIA/legal approval and replace pending metadata in legal_approval.md. | `make external-approval-release-check` |
| `P0` | `SEC-001` | `security` | `security` | `external-blocked` | False | Obtain security approval or pen-test sign-off and replace pending metadata in security_approval.md. | `make external-approval-release-check` |
| `P0` | `STAGING-001` | `staging` | `release` | `external-blocked` | False | Run staging acceptance, attach evidence URL, and replace pending metadata in staging_acceptance.md. | `make external-approval-release-check` |

## No false-closure rules

- Do not close CI-001 from local command output.
- Do not close external approvals from generated templates.
- Do not close staging acceptance without a staging evidence URL.
- Do not change release decision to GO while any beta-blocking registry item remains incomplete.

## Interpretation

This plan is an execution queue. It does not mark any blocker as resolved.
