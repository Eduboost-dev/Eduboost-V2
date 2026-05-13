# 3. Authentication, sessions, RBAC, and object-level authorization

## 3.1 Authentication flows

- [x] `P0` Verify guardian signup success path. Evidence: `app/api_v2_routers/auth.py`, `tests/smoke/test_v2_smoke.py::TestAuthEndpoints::test_register_success`.
- [x] `P0` Verify guardian signup validation errors. Evidence: `app/api_v2_routers/auth.py`, `tests/smoke/test_v2_smoke.py::TestAuthEndpoints::test_register_duplicate_email`.
- [x] `P0` Verify duplicate email handling. Evidence: `app/api_v2_routers/auth.py`, `tests/smoke/test_v2_smoke.py::TestAuthEndpoints::test_register_duplicate_email`.
- [x] `P0` Verify login success path. Evidence: `app/api_v2_routers/auth.py`, `tests/smoke/test_v2_smoke.py::TestAuthEndpoints::test_login_success`.
- [x] `P0` Verify login invalid password path. Evidence: `app/api_v2_routers/auth.py`, `tests/smoke/test_v2_smoke.py::TestAuthEndpoints::test_login_invalid_password`.
- [x] `P0` Verify login nonexistent account path. Evidence: `app/api_v2_routers/auth.py`, `tests/smoke/test_v2_smoke.py::TestAuthEndpoints::test_login_nonexistent_account`.
- [x] `P0` Verify logout revokes current token. Evidence: `app/api_v2_routers/auth.py`, `tests/unit/test_token_denylist.py`.
- [x] `P0` Verify logout clears refresh cookie where applicable. Evidence: `app/api_v2_routers/auth.py`.
- [x] `P0` Verify refresh-token success path. Evidence: `app/api_v2_routers/auth.py`, `tests/unit/test_refresh_token_rotation.py`.
- [x] `P0` Verify refresh-token expired path. Evidence: `app/core/security.py`, `tests/unit/test_refresh_token_rotation.py`.
- [x] `P0` Verify refresh-token reuse detection. Evidence: `app/core/refresh_tokens.py`, `tests/unit/test_refresh_token_rotation.py`.
- [x] `P0` Verify refresh-token family revocation. Evidence: `app/core/refresh_tokens.py`, `tests/unit/test_refresh_token_rotation.py`.
- [ ] `P0` Verify email verification flow.
- [ ] `P0` Verify password reset request.
- [ ] `P0` Verify password reset token expiry.
- [ ] `P0` Verify password reset completion.
- [ ] `P0` Verify password reset invalid token behavior.
- [ ] `P1` Add account lockout or risk-based throttling after repeated failures.
- [ ] `P1` Add security alert event for suspicious auth behavior.
- [ ] `P1` Add tests for all auth abuse paths.

## 3.2 Password security

- [x] `P0` Verify password hashing uses bcrypt or Argon2id with tuned cost. Evidence: `app/core/security.py`, `app/core/config.py::PASSWORD_BCRYPT_ROUNDS=12`, `tests/unit/test_password_policy.py::test_bcrypt_hash_uses_configured_cost_and_verifies`.
- [x] `P0` Verify configured bcrypt rounds are production-safe. Evidence: `app/core/config.py::PASSWORD_BCRYPT_ROUNDS=12`.
- [x] `P0` Verify password strength policy. Evidence: `app/core/password_policy.py`, `tests/unit/test_password_policy.py`.
- [x] `P0` Add password strength tests. Evidence: `tests/unit/test_password_policy.py`.
- [ ] `P1` Add breached-password check if feasible.
- [ ] `P1` Add password change flow.
- [ ] `P1` Add password change audit event.
- [ ] `P2` Add optional passphrase guidance.

## 3.3 Token policy

- [x] `P0` Confirm access-token TTL is 15 minutes or documented override. Evidence: `app/core/config.py::JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15`.
- [x] `P0` Confirm refresh-token TTL is 7 days or documented override. Evidence: `app/core/security.py::REFRESH_TOKEN_EXPIRE_DAYS=7`.
- [x] `P0` Verify refresh tokens are hashed at rest. Evidence: `app/core/refresh_tokens.py`.
- [x] `P0` Verify refresh tokens are revocable. Evidence: `app/core/refresh_tokens.py`, `app/core/token_revocation.py`.
- [x] `P0` Verify refresh tokens are bound to token family. Evidence: `app/core/security.py`, `tests/unit/test_refresh_token_rotation.py`.
- [x] `P0` Verify refresh-token rotation on use. Evidence: `app/api_v2_routers/auth.py`, `tests/unit/test_refresh_token_rotation.py`.
- [x] `P0` Verify token-family reuse detection. Evidence: `app/core/refresh_tokens.py`, `tests/unit/test_refresh_token_rotation.py`.
- [x] `P0` Verify Redis-backed revocation. Evidence: `app/core/refresh_tokens.py`.
- [ ] `P0` Decide behavior when Redis revocation store is unavailable.
- [ ] `P1` Add persistent fallback for revocation if required.
- [ ] `P1` Add JWT signing-key rotation with `kid`.
- [ ] `P1` Add current signing key.
- [ ] `P1` Add previous signing key validation window.
- [ ] `P1` Add emergency revoke-all procedure.
- [ ] `P1` Add tests for `kid` rotation.
- [ ] `P1` Add tests for emergency revoke-all.

## 3.4 Cookie security

- [x] `P0` Verify cookies are `HttpOnly`. Evidence: `app/api_v2_routers/auth.py::_set_refresh_cookie`.
- [x] `P0` Verify cookies are `Secure` in production. Evidence: `app/api_v2_routers/auth.py::_set_refresh_cookie`.
- [x] `P0` Verify cookies use correct `SameSite`. Evidence: `app/api_v2_routers/auth.py::_set_refresh_cookie`.
- [ ] `P0` Verify cookie domain is correct per environment.
- [x] `P0` Verify cookie path is correct. Evidence: `app/api_v2_routers/auth.py::_set_refresh_cookie`.
- [x] `P0` Verify no refresh token is JavaScript-readable. Evidence: `app/api_v2_routers/auth.py::_set_refresh_cookie`.
- [ ] `P0` Verify no access token is stored insecurely in frontend.
- [ ] `P1` Add cookie policy tests.
- [ ] `P1` Document cookie strategy.

## 3.5 RBAC and roles

- [x] `P0` Define role `student` (maps to learner). Evidence: `app/models/__init__.py::UserRole`.
- [x] `P0` Define role `parent` (maps to guardian). Evidence: `app/models/__init__.py::UserRole`.
- [x] `P0` Define role `teacher`. Evidence: `app/models/__init__.py::UserRole`.
- [x] `P0` Define role `admin`. Evidence: `app/models/__init__.py::UserRole`.
- [ ] `P0` Define role `support_operator`.
- [ ] `P0` Define role `content_reviewer`.
- [ ] `P0` Define role `compliance_auditor`.
- [ ] `P1` Document role permissions.
- [x] `P1` Add tests for each role. Evidence: `tests/unit/test_authorization_policy.py`, `tests/unit/test_object_authorization.py`.
- [ ] `P1` Add route policy matrix.

## 3.6 Object-level authorization

- [x] `P0` Add policy helper `can_view_learner`. Evidence: `app/core/authorization.py`, `app/security/object_authorization.py`.
- [x] `P0` Add policy helper `can_update_learner`. Evidence: `app/security/object_authorization.py`.
- [ ] `P0` Add policy helper `can_generate_lesson_for_learner`.
- [ ] `P0` Add policy helper `can_start_diagnostic_for_learner`.
- [ ] `P0` Add policy helper `can_view_study_plan`.
- [ ] `P0` Add policy helper `can_view_parent_report`.
- [ ] `P0` Add policy helper `can_export_learner_data`.
- [ ] `P0` Add policy helper `can_request_erasure`.
- [ ] `P0` Add policy helper `can_view_billing`.
- [x] `P0` Add test that learner cannot access another learner. Evidence: `tests/unit/test_object_authorization.py`.
- [x] `P0` Add test that guardian can access only linked learners. Evidence: `tests/unit/test_authorization_policy.py`.
- [ ] `P0` Add test that teacher can access only assigned learners/classes.
- [ ] `P0` Add test that support cannot view unnecessary PII.
- [ ] `P0` Add test that compliance auditor can view audit records without broad data mutation rights.
- [ ] `P0` Add audit events for privileged access.
- [verify] `P1` Add policy tests for every router. Evidence: `docs/security/PHASE2_AUTHORIZATION_CLOSURE.md`, `scripts/check_phase2_authorization_evidence.py`, `scripts/check_privacy_boundary_evidence.py`; verification gap: every router still needs item-level reconciliation before this can become `[x]`.
- [ ] `P1` Move from basic RBAC to policy-based authorization for sensitive workflows.
- [ ] `P2` Add tightly audited admin impersonation only if absolutely required.

## 3.7 Rate limiting and abuse prevention

- [x] `P0` Add rate limit to login. Evidence: `app/api_v2_routers/auth.py::login`.
- [x] `P0` Add rate limit to signup. Evidence: `app/api_v2_routers/auth.py::register`.
- [x] `P0` Add rate limit to refresh. Evidence: `app/api_v2_routers/auth.py::refresh_token`.
- [ ] `P0` Add rate limit to password reset.
- [ ] `P0` Add rate limit to email verification.
- [ ] `P0` Add rate limit to LLM lesson generation.
- [ ] `P0` Add rate limit to data export.
- [ ] `P0` Add rate limit to billing webhook endpoints if applicable.
- [ ] `P1` Add account-level throttling.
- [ ] `P1` Add IP-level throttling.
- [ ] `P1` Add risk-based throttling.
- [ ] `P1` Add rate-limit tests.

---

