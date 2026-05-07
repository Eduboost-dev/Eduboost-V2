# Repository Governance

Purpose: Document canonical repository, branch policy, release authority, and secret rotation responsibilities for EduBoost-V2.

1. Canonical repository
- Owner: NkgoloL/Eduboost-V2 (canonical upstream owner: `NkgoloL`).
- Mirrors: None configured by default. Add mirrors and sync policy if needed.

2. Branch policy
- Canonical protected branches: `main` (protected).
- PR requirements: CI green, 1+ approver, no force-push, require passing checks (lint, tests, typecheck), signed commits optional.

3. Release authority
- Who can tag releases: `NkgoloL` (individual or appointed release manager).
- Release checklist location: `docs/release_checklist.md` (create if missing and require a checklist artifact for tagged releases).

4. Secret management
- Production secrets owner: `NkgoloL` until a team/rotation policy is defined.
- Rotation schedule and emergency revoke procedure: Document rotation cadence and emergency revoke steps in a separate `docs/secrets.md`.

5. Security patching
- Responsibility for dependency updates, CVE triage, and critical patching: `NkgoloL` and any designated maintainers.
- Enable Dependabot or Renovate for Python, npm, Docker, and GitHub Actions unless org policy overrides.

6. Archive and deprecation policy
- How and when repositories are archived: Follow org policy; tag releases and move retired code to an `archive/` folder with a NOTICE.

7. Next steps
- Fill in organizational contacts and consider adding CODEOWNERS, issue templates, and PR templates (some have been added to `.github/`).

Keep this file updated in `docs/` as governance decisions change.
# Repository Governance

This document defines the management, contribution, and release policies for the EduBoost V2 repository.

## 1. Canonical Repository
The source of truth for all EduBoost V2 development is:
**`NkgoloL/Eduboost-V2`** (on GitHub)

## 2. Branching Policy
- **`main` / `master`**: Production-ready code. Every commit must be tagged and pass all CI checks.
- **`develop`**: Integration branch for the next release.
- **`feature/*`**: Individual feature development. Merged into `develop` via Pull Request.
- **`hotfix/*`**: Urgent production fixes. Merged into `main` and `develop`.

## 3. Pull Request Requirements
All PRs must:
- Pass `pytest` suite.
- Pass linting (`ruff`, `black`).
- Include updated documentation if applicable.
- Receive at least one approval from a designated code owner.
- Link to a relevant issue or task.

## 4. Release Authority
- Releases are tagged by the Technical Lead or designated Release Manager.
- Tag format: `vX.Y.Z[-beta.N]`.
- Every release must satisfy the `docs/release_checklist.md`.

## 5. Security & Secret Rotation
- No secrets (keys, passwords) shall be committed to the repository.
- Use `app/core/secret_rotation.py` for automated rotation where supported.
- Vulnerability reports should be directed to [Security Email] and handled as P0 incidents.

## 6. Archive Policy
- Stale branches (older than 3 months) will be deleted after merging or documented abandonment.
- Repository mirrors are maintained for disaster recovery purposes.
