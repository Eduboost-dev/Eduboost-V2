# Security

Security work covers authentication, authorization, secrets, JWT rotation, object authorization, dependency posture, and production environment gates.

## Runtime map

- Auth routes/services: `app/api_v2_routers/auth.py`, `app/services/auth_application_service.py`, `app/services/auth_service.py`
- Security helpers: `app/security/`, `app/core/security.py`, `app/services/jwt_keyring.py`
- Security docs and evidence: `docs/security/`

## Current implementation notes

- Canonical V2 auth should use repository-backed service paths.
- Legacy auth compatibility shims are bounded and must not become production auth behavior.
- Production secret placeholders and Key Vault behavior are guarded by tests.

## Verification

- `make environment-security-check`
- `make production-secret-placeholder-check`
- `make privacy-boundary-check`
- Security tests under `tests/unit/test_*security*`, `test_auth_*`, and `test_jwt_*`

Back to the main index: [docs/README.md](../README.md). Root overview: [README.md](../../README.md).
