# JWT Security Implementation and Token Management

EduBoost V2's JWT authentication system with dual-token architecture: short-lived access tokens (15 min) and single-use refresh tokens with family-based rotation. Features include kid-based key rotation via jwt_keyring, Redis-backed token storage with family reuse detection, multi-layer revocation (JTI, user-level, family-based), and canonical claims building. Notable entry points: login flow at [1b], token creation with keyring at [2d], verification with revocation at [3c], refresh rotation at [4b], and claims building at [5b].

## Trace ID: 1
**Title:** Login Flow: Credentials to Token Pair with HTTP-Only Cookie

**Description:** Primary auth system - traces user login from API endpoint through password verification to JWT token pair issuance with Redis storage and secure cookie delivery

**Motivation:**
EduBoost V2 implements a dual-token authentication system to balance security with user experience. Short-lived access tokens (15 minutes) minimize the window for token theft, while longer-lived refresh tokens enable seamless session renewal without requiring re-authentication. The system uses HTTP-only cookies for refresh token storage to protect against XSS attacks, and family-based refresh token rotation to detect and prevent replay attacks. This approach separates concerns: access tokens for API calls (stateless, short-lived) and refresh tokens for session renewal (stateful, single-use with rotation). The login flow validates credentials with bcrypt, generates both tokens, stores the refresh token in Redis, and returns the access token in the response body with the refresh token in a secure cookie.

**Details:**
- **Execution Flow:** FastAPI Auth Router POST /auth/login → auth_service.login() → auth_lifecycle_impl.login_impl() → Password Verification (verify_password() with bcrypt) → Token Generation (create_refresh_token() with family_id, create_access_token() with role + claims) → Token Storage (store_refresh_token() with Redis hash storage) → Response (_set_refresh_cookie() with HTTP-only cookie)
- **Concurrency Safety:** Password verification uses constant-time bcrypt comparison to prevent timing attacks. Redis operations for token storage are atomic. No distributed locks needed as login is idempotent (multiple concurrent logins with same credentials create independent token pairs). Redis provides atomic operations for token storage
- **Covered Objects:** User credentials (email, password), User record (from database), Refresh token (JWT with family_id, JTI), Access token (JWT with claims), Redis storage (hashed refresh token with TTL), HTTP response (cookies), Bcrypt password hashing
- **Timeouts:** Password verification: ~100-300ms (bcrypt 12 rounds). Redis SETEX operation: <5ms. Token generation: ~10-50ms. Overall login latency: ~200-400ms typical
- **Migration Path:** From session-based authentication (server-side sessions) to JWT-based stateless authentication. Migration requires: 1) Implement JWT token generation, 2) Add Redis for token storage, 3) Update API endpoints to use JWT, 4) Implement refresh token rotation, 5) Migrate existing sessions to JWT tokens
- **Error Handling:** Invalid credentials return 401 without revealing specific error. Database failures return 500. Redis failures fail closed (refuse login) to prevent issuing tokens without storage. All errors logged with structured logging for monitoring
- **Security Considerations:** Rate limiting on login endpoint prevents brute force. Account lockout after repeated failures. HTTPS required in production for cookie security. Password strength validation enforced at registration. HTTP-only, SameSite=strict cookies prevent XSS and CSRF. Refresh tokens hashed before storage

**Trace text diagram:**
```
Login Flow: Credentials → Token Pair
├── FastAPI Auth Router
│   └── POST /auth/login <-- 1a
│       └── auth_service.login()
│           └── auth_lifecycle_impl.login_impl() <-- auth_lifecycle_impl.py:140
│               ├── Password Verification
│               │   └── verify_password() <-- 1b
│               ├── Token Generation
│               │   ├── create_refresh_token() <-- 1c
│               │   │   └── JWT with family_id <-- security.py:73
│               │   └── create_access_token() <-- 1d
│               │       └── JWT with role + claims <-- security.py:52
│               ├── Token Storage
│               │   └── store_refresh_token() <-- 1e
│               │       └── Redis hash storage <-- refresh_tokens.py:68
│               └── Response
│                   └── _set_refresh_cookie() <-- 1f
│                       └── HTTP-only cookie <-- auth_lifecycle_impl.py:42
```

**Location ID: 1a**
- **Title:** Login endpoint delegates to service
- **Description:** FastAPI route receives LoginRequest and delegates to auth application service
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/api_v2_routers/auth.py:115

**Location ID: 1b**
- **Title:** Verify password with bcrypt
- **Description:** Constant-time password comparison using bcrypt from security.py
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/auth_lifecycle_impl.py:152

**Location ID: 1c**
- **Title:** Create refresh token JWT
- **Description:** Generates JWT refresh token with family_id for rotation tracking
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/auth_lifecycle_impl.py:156

**Location ID: 1d**
- **Title:** Create access token with claims
- **Description:** Generates short-lived access token (15 min) with role and learner IDs
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/auth_lifecycle_impl.py:162

**Location ID: 1e**
- **Title:** Store refresh token in Redis
- **Description:** Hashes and stores refresh token with family binding for reuse detection
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/auth_lifecycle_impl.py:164

**Location ID: 1f**
- **Title:** Set HTTP-only cookie
- **Description:** Returns refresh token in secure, HTTP-only, SameSite=strict cookie
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/auth_lifecycle_impl.py:165

### AI Guide: Login Flow

**Motivation:**
The login flow transforms user credentials into a dual-token authentication system. The system validates credentials, generates JWT tokens, stores refresh tokens securely, and delivers tokens via secure HTTP-only cookies to provide secure authentication.

**Details:**

**Password Verification and Token Generation**
Password verification uses bcrypt for constant-time comparison to prevent timing attacks and validates against stored hash [1b]. Token generation creates refresh token with family_id for rotation and creates access token with claims (role, learner IDs) with short-lived access (15 min) for security [1c][1d].

**Token Storage and Cookie Delivery**
Token storage hashes refresh token with SHA-256, stores in Redis with TTL, and uses triple-key storage (JTI, family, user) for tracking [1e]. Cookie delivery returns refresh token in HTTP-only cookie with SameSite=strict to prevent CSRF and Secure flag for HTTPS [1f].

**Dual-Token Pattern**
The dual-token pattern separates access (stateless, short-lived) from refresh (stateful, single-use) to balance security with UX.

## Trace ID: 2
**Title:** Access Token Creation with Kid-Based Keyring

**Description:** Primary JWT system - demonstrates how access tokens are signed using the current key from jwt_keyring with kid header for rotation support

**Motivation:**
EduBoost V2 implements a kid-based key rotation system to enable seamless JWT signing key updates without breaking existing tokens. The jwt_keyring maintains multiple keys with status (current, previous, future) and includes the key ID (kid) in the JWT header. During verification, the system tries keys in order (matching kid first, then current, then previous) to support graceful key rotation. This approach allows for regular key rotation for security while maintaining backward compatibility with tokens signed by previous keys. The keyring is parsed from JWT_KEYRING environment variable (JSON) or falls back to legacy JWT_SECRET for backward compatibility.

**Details:**
- **Execution Flow:** create_access_token() entry → Build JWT payload dict (Add sub, role, exp, iat, Generate unique JTI, Add type="access" + extra claims) → jwt.encode() with keyring → current_jwt_signing_key() → current_jwt_key() (Select key with status="current") → current_jwt_algorithm() (Extract algorithm from current key) → current_jwt_headers() (Return {"kid": key.kid})
- **Concurrency Safety:** Keyring parsing is read-only and thread-safe. Key selection is deterministic based on status. JWT encoding is stateless. No distributed locks needed as operations are read-only. Multiple token creations can run concurrently
- **Covered Objects:** create_access_token() function, JWT payload (sub, role, exp, iat, jti, type), jwt_keyring (current, previous, future keys), kid header, JWT signing key, JWT algorithm, Extra claims
- **Timeouts:** Payload building: ~1-5ms. Keyring parsing: ~1-5ms. Key selection: <1ms. JWT encoding: ~10-50ms. Total token creation: ~10-60ms
- **Migration Path:** From single JWT secret to keyring-based rotation. Migration requires: 1) Parse JWT_KEYRING from environment, 2) Implement key status management, 3) Add kid to JWT headers, 4) Update verification to try multiple keys, 5) Support legacy JWT_SECRET fallback
- **Error Handling:** Missing keyring raises error. Invalid keyring JSON raises error. No current key raises error. Encoding failures raise error. All errors logged with context
- **Security Considerations:** Keyring from environment (not in code). Kid in header enables rotation. Support for previous keys ensures compatibility. Regular key rotation for security. Fail closed on missing keys

**Trace text diagram:**
```
Access Token Creation with Keyring
├── create_access_token() entry <-- 2a
│   ├── Build JWT payload dict <-- 2b
│   │   ├── Add sub, role, exp, iat <-- security.py:53
│   │   ├── Generate unique JTI <-- 2c
│   │   └── Add type="access" + extra claims <-- security.py:58
│   └── jwt.encode() with keyring <-- 2d
│       ├── current_jwt_signing_key() <-- 2e
│       │   └── current_jwt_key() <-- jwt_keyring.py:185
│       │       └── Select key with status="current" <-- jwt_keyring.py:179
│       ├── current_jwt_algorithm() <-- jwt_keyring.py:188
│       │   └── Extract algorithm from current key <-- jwt_keyring.py:190
│       └── current_jwt_headers() <-- 2f
│           └── Return {"kid": key.kid} <-- jwt_keyring.py:194
```

**Location ID: 2a**
- **Title:** Access token creation entry point
- **Description:** Creates JWT access token with subject, role, and optional extra claims
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/security.py:50

**Location ID: 2b**
- **Title:** Build JWT payload with claims
- **Description:** Constructs payload with sub, role, exp, iat, jti, and type claims
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/security.py:52

**Location ID: 2c**
- **Title:** Generate unique token ID
- **Description:** Creates JTI claim for per-token revocation tracking
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/security.py:57

**Location ID: 2d**
- **Title:** Encode JWT with keyring
- **Description:** Signs token using current key from keyring with kid header
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/security.py:61

**Location ID: 2e**
- **Title:** Get current signing key
- **Description:** Retrieves the active signing key from parsed keyring
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/jwt_keyring.py:184

**Location ID: 2f**
- **Title:** Add kid to JWT header
- **Description:** Includes key ID in JWT header for rotation support
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/jwt_keyring.py:193

### AI Guide: Access Token Creation with Keyring

**Motivation:**
The access token creation system uses a kid-based keyring to enable seamless key rotation. Tokens are signed with the current key while including the kid header for verification compatibility to support key rotation without breaking existing tokens.

**Details:**

**Payload Building and Keyring Selection**
Payload building constructs JWT payload with standard claims (sub, role, exp, iat), generates unique JTI for revocation tracking, and adds type="access" and extra claims [2b][2c]. Keyring selection selects current signing key from keyring where the key has status="current" and supports multiple keys for rotation [2e].

**Algorithm Extraction and Kid Header**
Algorithm extraction extracts algorithm from current key (typically HS256 or RS256) which is configured per key. The kid header adds kid to JWT header to enable verification to select correct key, which is critical for rotation support [2f].

**JWT Encoding**
JWT encoding signs token with selected key, includes kid in header, and returns encoded JWT string [2d].

## Trace ID: 3
**Title:** Token Verification with Multi-Layer Revocation Checks

**Description:** Primary JWT system - traces token validation from HTTP bearer extraction through keyring signature verification to Redis-backed revocation checks (JTI and user-level)

**Motivation:**
EduBoost V2 implements multi-layer token verification to ensure comprehensive security. The system extracts Bearer tokens from Authorization headers, verifies signatures using the keyring (trying current and previous keys), checks token type (access vs refresh), and validates revocation status at multiple levels (per-token JTI blacklist and user-level revocation). This layered approach catches compromised tokens at multiple points: signature verification prevents tampering, type checking prevents token misuse, JTI revocation enables per-token invalidation (logout), and user-level revocation enables forced invalidation (password reset). The keyring-based verification supports key rotation by trying keys in order (matching kid first, then current, then previous).

**Details:**
- **Execution Flow:** FastAPI Dependency Injection → get_current_user() dependency → decode_token() → decode_jwt_with_keyring() → get_unverified_header() → parse_jwt_keyring() (Select matching key by kid) → jwt.decode() signature verify → Revocation Checks → Per-token JTI check (is_token_revoked() with Redis GET operation) → User-level revocation check (is_user_revoked() with Redis GET revoked_user:{id}) → Return validated payload
- **Concurrency Safety:** Token verification is stateless and thread-safe. Redis operations are atomic. Keyring parsing is read-only. No distributed locks needed as operations are read-only. Multiple verifications can run concurrently
- **Covered Objects:** FastAPI dependency injection, Bearer token extraction, JWT header (kid), jwt_keyring (current, previous keys), Signature verification, Redis blacklist (revoked_jti), User revocation (revoked_user), Token payload
- **Timeouts:** Token extraction: <1ms. Header parsing: <1ms. Keyring parsing: ~1-5ms. Signature verification: ~10-50ms. JTI revocation check: ~5-10ms. User revocation check: ~5-10ms. Total verification: ~20-80ms
- **Migration Path:** From simple JWT verification to multi-layer checks. Migration requires: 1) Add keyring-based verification, 2) Implement JTI revocation blacklist, 3) Add user-level revocation, 4) Add token type checking, 5) Update error handling
- **Error Handling:** Missing token returns 401. Invalid signature returns 401. Expired token returns 401. Revoked token returns 401. Invalid token type returns 401. All errors logged with context
- **Security Considerations:** Multi-layer revocation (JTI + user-level). Keyring supports key rotation. Signature verification prevents tampering. Type checking prevents token misuse. Redis provides fast revocation checks. Fail closed on Redis unavailability

**Trace text diagram:**
```
Token Verification Flow
├── FastAPI Dependency Injection
│   └── get_current_user() dependency <-- 3a
│       └── decode_token() <-- 3b
│           └── decode_jwt_with_keyring() <-- 3c
│               ├── get_unverified_header() <-- 3d
│               ├── parse_jwt_keyring() <-- jwt_keyring.py:228
│               │   └── Select matching key by kid <-- jwt_keyring.py:229
│               └── jwt.decode() signature verify <-- 3e
├── Revocation Checks
│   ├── Per-token JTI check <-- 3f
│   │   └── is_token_revoked() <-- token_revocation.py:71
│   │       └── Redis GET operation <-- token_revocation.py:75
│   └── User-level revocation check <-- 3g
│       └── is_user_revoked() <-- token_revocation.py:103
│           └── Redis GET revoked_user:{id} <-- token_revocation.py:107
└── Return validated payload <-- security.py:124
```

**Location ID: 3a**
- **Title:** FastAPI dependency extracts token
- **Description:** Dependency injection extracts Bearer token from Authorization header
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/security.py:93

**Location ID: 3b**
- **Title:** Decode and verify token
- **Description:** Decodes JWT and verifies signature using keyring
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/security.py:100

**Location ID: 3c**
- **Title:** Decode with keyring fallback
- **Description:** Attempts verification with current and previous keys from keyring
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/security.py:80

**Location ID: 3d**
- **Title:** Extract kid from header
- **Description:** Reads kid claim to determine which key to try first
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/jwt_keyring.py:226

**Location ID: 3e**
- **Title:** Verify signature with key
- **Description:** Cryptographically validates JWT signature and expiry
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/jwt_keyring.py:233

**Location ID: 3f**
- **Title:** Check per-token revocation
- **Description:** Queries Redis blacklist for revoked JTI
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/security.py:108

**Location ID: 3g**
- **Title:** Check user-level revocation
- **Description:** Verifies user hasn't had all tokens revoked (e.g., password reset)
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/security.py:117

### AI Guide: Token Verification with Multi-Layer Revocation Checks

**Motivation:**
The token verification system implements multi-layer security checks to ensure comprehensive token validation. The system verifies signatures, checks revocation at multiple levels, and supports key rotation to provide robust token validation.

**Details:**

**Token Extraction and Signature Verification**
Token extraction uses FastAPI dependency to extract Bearer token from Authorization header and returns 401 if missing [3a]. Signature verification decodes JWT with keyring, tries keys in order (kid, current, previous), verifies cryptographic signature, and checks expiry [3b][3c][3d][3e].

**JTI and User Revocation**
JTI revocation checks per-token revocation blacklist by querying Redis for revoked_jti:{jti} to enable logout and forced invalidation [3f]. User revocation checks user-level revocation by querying Redis for revoked_user:{id} to enable password reset revocation [3g].

**Multi-Layer Defense**
The multi-layer defense includes signature verification to prevent tampering, JTI revocation to enable per-token invalidation, user revocation to enable forced invalidation, and keyring to support rotation.

## Trace ID: 4
**Title:** Refresh Token Rotation: Single-Use Consumption with Family Reuse Detection

**Description:** Primary JWT system - demonstrates single-use refresh token consumption with constant-time hash comparison, family-based reuse detection, and new token pair issuance

**Motivation:**
EduBoost V2 implements single-use refresh token rotation with family-based reuse detection to prevent replay attacks and enhance security. Each refresh token can only be used once; consumption deletes it from Redis. Tokens are grouped into families (linked by family_id) to detect reuse attempts: if a token from a family is used twice, the entire family is revoked, indicating a potential replay attack. The system uses constant-time hash comparison (hmac.compare_digest) to prevent timing attacks when validating token hashes. This approach balances security (single-use tokens, reuse detection) with user experience (automatic token refresh without re-authentication). The rotation flow validates the token, consumes it, checks for family revocation, and issues a new token pair with the same family_id.

**Details:**
- **Execution Flow:** FastAPI Auth Router POST /auth/refresh → auth_service.refresh() → auth_lifecycle_impl.refresh_impl() → consume_refresh_token() → Token Consumption & Validation (is_refresh_family_revoked(), hmac.compare_digest() check, revoke_refresh_family() if reuse detected, cache_delete(jti)) → New Token Pair Issuance (create_refresh_token(family_id), create_access_token(), store_refresh_token() with Redis persistence)
- **Concurrency Safety:** Token consumption is atomic (delete in Redis). Family revocation is atomic. Constant-time comparison prevents timing attacks. No distributed locks needed as Redis provides atomic operations. Multiple refresh attempts on same token fail (single-use)
- **Covered Objects:** Refresh token (JWT with family_id, JTI), Redis storage (hashed token), Family revocation (refresh_family_revoked), Constant-time hash comparison, New token pair (refresh + access), Reuse detection
- **Timeouts:** Token validation: ~10-50ms. Hash comparison: <1ms. Family revocation check: ~5-10ms. Token deletion: ~5-10ms. New token generation: ~10-50ms. Total refresh: ~30-120ms
- **Migration Path:** From long-lived refresh tokens to single-use rotation. Migration requires: 1) Implement family_id in tokens, 2) Add hash comparison for validation, 3. Implement single-use consumption, 4) Add family revocation on reuse, 5) Update client to handle rotation
- **Error Handling:** Missing token returns 401. Invalid signature returns 401. Revoked family returns 401. Hash mismatch triggers family revocation. Redis failures logged but don't block. All errors logged with context
- **Security Considerations:** Single-use tokens prevent replay attacks. Family-based reuse detection catches replay. Constant-time comparison prevents timing attacks. Family revocation on reuse (fail secure). Hash tokens before storage. HTTP-only cookies prevent XSS

**Trace text diagram:**
```
Refresh Token Rotation Flow
├── FastAPI Auth Router
│   └── POST /auth/refresh <-- 4a
│       └── auth_service.refresh() <-- auth.py:158
│           └── auth_lifecycle_impl.refresh_impl() <-- auth_lifecycle_impl.py:171
│               └── consume_refresh_token() <-- 4b
│
├── Token Consumption & Validation
│   └── refresh_tokens.py
│       ├── is_refresh_family_revoked() <-- 4c
│       ├── hmac.compare_digest() check <-- 4d
│       ├── revoke_refresh_family() <-- 4e
│       │   └── (if reuse detected)
│       └── cache_delete(jti) <-- 4f
│
└── New Token Pair Issuance
    └── auth_lifecycle_impl.refresh_impl() <-- auth_lifecycle_impl.py:171
        ├── create_refresh_token(family_id) <-- 4g
        ├── create_access_token() <-- auth_lifecycle_impl.py:200
        └── store_refresh_token() <-- 4h
            └── Redis persistence <-- refresh_tokens.py:68
```

**Location ID: 4a**
- **Title:** Refresh endpoint delegates to service
- **Description:** FastAPI route receives refresh token from cookie and delegates to service
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/api_v2_routers/auth.py:158

**Location ID: 4b**
- **Title:** Consume refresh token
- **Description:** Validates and deletes refresh token in single atomic operation
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/auth_lifecycle_impl.py:182

**Location ID: 4c**
- **Title:** Check family revocation
- **Description:** Detects if token family was revoked due to reuse (security breach)
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/refresh_tokens.py:78

**Location ID: 4d**
- **Title:** Timing-safe hash comparison
- **Description:** Verifies token hash matches stored value using constant-time comparison
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/refresh_tokens.py:82

**Location ID: 4e**
- **Title:** Revoke family on reuse
- **Description:** Immediately revokes entire token family if reuse detected (replay attack)
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/refresh_tokens.py:83

**Location ID: 4f**
- **Title:** Delete consumed token
- **Description:** Removes token from Redis ensuring single-use property
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/refresh_tokens.py:89

**Location ID: 4g**
- **Title:** Issue new refresh token
- **Description:** Creates new refresh token inheriting same family_id for rotation chain
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/auth_lifecycle_impl.py:189

**Location ID: 4h**
- **Title:** Store new token
- **Description:** Persists new refresh token completing the rotation cycle
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/auth_lifecycle_impl.py:201

### AI Guide: Refresh Token Rotation

**Motivation:**
The refresh token rotation system implements single-use tokens with family-based reuse detection. The system validates tokens, detects replay attacks, and issues new token pairs to maintain security while providing a good user experience.

**Details:**

**Token Consumption and Family Check**
Token consumption validates and deletes token atomically to ensure single-use property and prevent replay attacks [4b]. Family check checks if family is revoked which indicates previous reuse and returns 401 if revoked [4c].

**Hash Comparison and Revoke on Reuse**
Hash comparison uses constant-time comparison to prevent timing attacks and validates token integrity [4d]. Revoke on reuse revokes entire family on reuse as a fail-secure approach to detect replay attacks [4e].

**New Token Issuance**
New token issuance creates new refresh token with same family_id, creates new access token, and stores in Redis [4g][4h].

## Trace ID: 5
**Title:** Building Canonical Access Token Claims with Authorization Scope

**Description:** Token claims system - traces how access token claims are built from user data, preserving guardian_learner_ids and other authorization-relevant claims during token refresh

**Motivation:**
EduBoost V2 implements a canonical claims building system to ensure consistent authorization scope across token refresh. The system builds access token claims from user data, preserving critical authorization information like guardian_learner_ids during refresh operations. This ensures that authorization checks remain consistent even as tokens are refreshed, preventing authorization scope drift. The claims builder extracts user_id, role, guardian_learner_ids, and other authorization-relevant fields, normalizes them, and creates a canonical AuthTokenClaims object. This approach centralizes claims logic, ensures consistency across login and refresh flows, and provides a clear contract for what claims are included in access tokens.

**Details:**
- **Execution Flow:** Refresh Implementation → auth_lifecycle_impl.refresh_impl() → Build canonical claims → Claims Builder (auth_token_claims.py) → build_access_token_claims() → Extract user_id from user/claims → Extract guardian_learner_ids (_normalize_str_tuple() to merge user + existing claims) → Build AuthTokenClaims object (sub, user_id, role, guardian_learner_ids, learner_id, parent_id) → Serialize to payload dict (claims.to_payload())
- **Concurrency Safety:** Claims building is stateless and thread-safe. Data extraction is read-only. Normalization is deterministic. No distributed locks needed as operations are read-only. Multiple claims builds can run concurrently
- **Covered Objects:** User object, Existing claims, AuthTokenClaims object, guardian_learner_ids, user_id, role, learner_id, parent_id, Extra claims, Payload dict
- **Timeouts:** User extraction: ~1-5ms. Claims normalization: ~1-5ms. Object creation: ~1-5ms. Serialization: ~1-5ms. Total claims building: ~5-20ms
- **Migration Path:** From ad-hoc claims building to canonical builder. Migration requires: 1) Create AuthTokenClaims class, 2) Implement claims builder function, 3) Normalize claims extraction, 4) Update login and refresh flows, 5) Ensure backward compatibility
- **Error Handling:** Missing user_id raises ValueError. Invalid data types raise error. Normalization failures logged. All errors logged with context
- **Security Considerations:** Preserve authorization scope across refresh. Normalize claims for consistency. Validate required fields. Prevent scope drift. No sensitive data in claims (only IDs and roles)

**Trace text diagram:**
```
Access Token Claims Building Flow
├── Refresh Implementation
│   └── auth_lifecycle_impl.refresh_impl() <-- auth_lifecycle_impl.py:171
│       └── Build canonical claims <-- 5a
│
└── Claims Builder (auth_token_claims.py)
    └── build_access_token_claims() <-- 5b
        ├── Extract user_id from user/claims <-- 5c
        ├── Extract guardian_learner_ids <-- 5d
        │   └── _normalize_str_tuple() <-- auth_token_claims.py:85
        │       └── Merge user + existing claims
        ├── Build AuthTokenClaims object <-- 5e
        │   ├── sub, user_id, role <-- auth_token_claims.py:29
        │   ├── guardian_learner_ids <-- auth_token_claims.py:33
        │   └── learner_id, parent_id <-- auth_token_claims.py:34
        └── Serialize to payload dict <-- 5f
            └── claims.to_payload() <-- auth_token_claims.py:39
```

**Location ID: 5a**
- **Title:** Build canonical claims during refresh
- **Description:** Calls claims builder with existing claims to preserve authorization scope
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/auth_lifecycle_impl.py:196

**Location ID: 5b**
- **Title:** Claims builder entry point
- **Description:** Builds canonical access-token claims for register/login/refresh
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/auth_token_claims.py:95

**Location ID: 5c**
- **Title:** Extract stable user ID
- **Description:** Reads user_id from user object or preserves from existing claims
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/auth_token_claims.py:110

**Location ID: 5d**
- **Title:** Preserve guardian_learner_ids
- **Description:** Extracts or preserves guardian_learner_ids for authorization checks
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/auth_token_claims.py:116

**Location ID: 5e**
- **Title:** Build claims object
- **Description:** Creates canonical AuthTokenClaims with all authorization-relevant fields
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/auth_token_claims.py:122

**Location ID: 5f**
- **Title:** Convert to payload dict
- **Description:** Serializes claims object to dictionary for JWT encoding
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/auth_token_claims.py:133

### AI Guide: Building Canonical Access Token Claims

**Motivation:**
The canonical claims building system ensures consistent authorization scope across token refresh. The system builds claims from user data while preserving authorization-relevant information to maintain consistent authorization.

**Details:**

**Claims Builder and User ID Extraction**
The claims builder is centralized claims building logic used by login and refresh to ensure consistency [5b]. User ID extraction extracts stable user_id from user object or existing claims and preserves it across refresh [5c].

**Guardian Learner IDs and Claims Object**
Guardian learner IDs extracts authorization scope, normalizes to string tuple, and merges user + existing claims [5d]. The claims object creates AuthTokenClaims object as a canonical representation including all auth-relevant fields [5e].

**Serialization**
Serialization converts to payload dict for JWT encoding and maintains structure [5f].

## Trace ID: 6
**Title:** Refresh Token Storage: Triple-Key Redis Persistence with Hashing

**Description:** Token storage system - shows how refresh tokens are hashed and stored in Redis with three keys (jti, family, user) for fast lookup and family tracking

**Motivation:**
EduBoost V2 implements triple-key Redis storage for refresh tokens to enable efficient lookup and family tracking. Tokens are hashed with SHA-256 before storage to prevent plaintext storage in Redis. Three keys are stored for each token: by JTI (for consumption lookup), by family (for family tracking and revocation), and by user session (for session listing). This multi-key approach enables fast lookups for different operations (consumption, family revocation, session management) while maintaining security through hashing. The TTL is calculated from token expiry to ensure automatic cleanup. This design balances performance (fast Redis lookups) with security (hashed storage, automatic cleanup).

**Details:**
- **Execution Flow:** store_refresh_token() entry → Decode & validate token (_require_refresh_payload() with decode_token()) → Extract claims (jti, subject, family_id) → Calculate TTL from expiry → Hash token with SHA-256 (token_hash()) → Triple-key Redis persistence → Store by JTI (cache_set(refresh:{jti}, hash)) → Store by family (cache_set(refresh_family:{fam}:{jti})) → Store by user session (cache_set(refresh_user:{sub}:{jti}))
- **Concurrency Safety:** Redis operations are atomic. Hash computation is deterministic. TTL calculation is stateless. No distributed locks needed as Redis provides atomic operations. Multiple storage operations can run concurrently
- **Covered Objects:** Refresh token (JWT), SHA-256 hash, Redis keys (refresh:{jti}, refresh_family:{fam}:{jti}, refresh_user:{sub}:{jti}), TTL, Token claims (jti, subject, family_id)
- **Timeouts:** Token decoding: ~10-50ms. Hash computation: ~1-5ms. TTL calculation: <1ms. Redis SET operations: ~5-10ms each. Total storage: ~20-80ms
- **Migration Path:** From single-key to triple-key storage. Migration requires: 1) Implement token hashing, 2) Add family key storage, 3) Add user session key storage, 4) Calculate TTL from expiry, 5) Update consumption logic
- **Error Handling:** Invalid token raises error. Redis failures logged but don't block. Hash computation failures raise error. TTL calculation failures raise error. All errors logged with context
- **Security Considerations:** Hash tokens before storage. SHA-256 for cryptographic security. TTL for automatic cleanup. Triple-key for different lookups. No plaintext in Redis. Fail closed on Redis failures

**Trace text diagram:**
```
Refresh Token Storage Flow
├── store_refresh_token() entry <-- 6a
│   ├── Decode & validate token
│   │   └── _require_refresh_payload() <-- 6b
│   │       └── decode_token() <-- security.py:80
│   ├── Extract claims (jti, subject, family_id) <-- refresh_tokens.py:62
│   ├── Calculate TTL from expiry <-- refresh_tokens.py:65
│   ├── Hash token with SHA-256 <-- 6c
│   │   └── token_hash() <-- refresh_tokens.py:25
│   └── Triple-key Redis persistence
│       ├── Store by JTI <-- 6d
│       │   └── cache_set(refresh:{jti}, hash)
│       ├── Store by family <-- 6e
│       │   └── cache_set(refresh_family:{fam}:{jti})
│       └── Store by user session <-- 6f
│           └── cache_set(refresh_user:{sub}:{jti})
```

**Location ID: 6a**
- **Title:** Store refresh token entry point
- **Description:** Stores refresh token in Redis with hashing and family binding
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/refresh_tokens.py:60

**Location ID: 6b**
- **Title:** Decode and validate token
- **Description:** Decodes JWT and validates it's a refresh token with required claims
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/refresh_tokens.py:61

**Location ID: 6c**
- **Title:** Hash token with SHA-256
- **Description:** Creates SHA-256 hash of token for secure storage
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/refresh_tokens.py:66

**Location ID: 6d**
- **Title:** Store by JTI key
- **Description:** Stores hashed token with refresh:{jti} key for consumption lookup
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/refresh_tokens.py:68

**Location ID: 6e**
- **Title:** Store by family key
- **Description:** Stores subject with refresh_family:{family}:{jti} for family tracking
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/refresh_tokens.py:69

**Location ID: 6f**
- **Title:** Store by user session key
- **Description:** Stores family_id with refresh_user:{subject}:{jti} for session listing
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/refresh_tokens.py:70

### AI Guide: Refresh Token Storage

**Motivation:**
The refresh token storage system uses triple-key Redis persistence with hashing for security. Tokens are hashed and stored with multiple keys for efficient lookup and family tracking to ensure secure and efficient token storage.

**Details:**

**Token Validation and Hashing**
Token validation decodes and validates token to ensure it's a refresh token and extracts required claims [6b]. Hashing uses SHA-256 hash of token to prevent plaintext storage and provide cryptographic security [6c].

**TTL Calculation and Triple-Key Storage**
TTL calculation is calculated from token expiry for automatic cleanup to prevent stale data. Triple-key storage uses JTI key for consumption, family key for tracking, and user session key for listing to enable different lookups [6d][6e][6f].

**Redis Persistence**
Redis persistence uses atomic SET operations for fast lookups and automatic expiration.

## Trace ID: 7
**Title:** JWT Keyring Validation: Startup Guard Against Placeholder Secrets

**Description:** Keyring system - demonstrates application startup validation that fails closed if production environment uses placeholder JWT secrets, preventing deployment with default credentials

**Motivation:**
EduBoost V2 implements startup validation for JWT keyring configuration to prevent deployment with insecure placeholder secrets. The system validates the keyring at application startup, detecting placeholder secrets (e.g., "change_me", "placeholder") and failing closed in production environments. This fail-closed approach prevents accidental deployment with default credentials, which would be a critical security vulnerability. The keyring is parsed from JWT_KEYRING environment variable (JSON format) or falls back to legacy JWT_SECRET for backward compatibility. This validation ensures that production deployments always use secure, non-placeholder secrets, providing a safety net against configuration errors.

**Details:**
- **Execution Flow:** Application Startup → validate_jwt_keyring_environment() → Parse Configuration (parse_jwt_keyring() with Load JWT_KEYRING from env, Fallback to JWT_SECRET) → Security Check (Detect placeholders with is_placeholder_secret()) → Production Guard (if production + placeholders) → raise JWTKeyringError → Result: Fail closed or continue startup
- **Concurrency Safety:** Validation is stateless and thread-safe. Keyring parsing is read-only. Placeholder detection is deterministic. No distributed locks needed as operations are read-only. Validation runs once at startup
- **Covered Objects:** JWT_KEYRING environment variable, JWT_SECRET fallback, Keyring configuration, Placeholder detection logic, Production environment flag, JWTKeyringError
- **Timeouts:** Keyring parsing: ~1-5ms. Placeholder detection: ~1-5ms. Total validation: ~2-10ms
- **Migration Path:** From no validation to startup guard. Migration requires: 1) Implement placeholder detection, 2) Add production guard, 3) Call validation at startup, 4) Support JWT_KEYRING and JWT_SECRET, 5) Fail closed on validation failure
- **Error Handling:** Invalid keyring JSON raises error. Missing keyring raises error. Placeholder secrets in production raise JWTKeyringError. All errors logged with context
- **Security Considerations:** Fail closed on placeholder secrets. Detect common placeholder values. Production-only enforcement. Prevents deployment with defaults. Keyring from environment (not in code). Supports legacy JWT_SECRET

**Trace text diagram:**
```
JWT Keyring Startup Validation
├── Application Startup
│   └── validate_jwt_keyring_environment() <-- 7a
│       ├── Parse Configuration
│       │   └── parse_jwt_keyring() <-- 7b
│       │       ├── Load JWT_KEYRING from env <-- jwt_keyring.py:134
│       │       └── Fallback to JWT_SECRET <-- jwt_keyring.py:136
│       ├── Security Check
│       │   └── Detect placeholders <-- 7c
│       │       └── is_placeholder_secret() <-- jwt_keyring.py:197
│       └── Production Guard
│           └── if production + placeholders <-- 7d
│               └── raise JWTKeyringError <-- 7e
└── Result: Fail closed or continue startup
```

**Location ID: 7a**
- **Title:** Startup validation entry point
- **Description:** Validates JWT keyring configuration at application startup
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/jwt_keyring.py:207

**Location ID: 7b**
- **Title:** Parse keyring configuration
- **Description:** Loads JWT_KEYRING JSON or falls back to legacy JWT_SECRET
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/jwt_keyring.py:209

**Location ID: 7c**
- **Title:** Detect placeholder secrets
- **Description:** Identifies keys with insecure default secrets (change_me, placeholder)
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/jwt_keyring.py:210

**Location ID: 7d**
- **Title:** Production placeholder guard
- **Description:** Fails application startup if production uses placeholder secrets
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/jwt_keyring.py:211

**Location ID: 7e**
- **Title:** Fail closed on invalid config
- **Description:** Raises error preventing deployment with insecure configuration
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/jwt_keyring.py:212

### AI Guide: JWT Keyring Validation

**Motivation:**
The JWT keyring validation system prevents deployment with placeholder secrets. The system validates keyring configuration at startup and fails closed in production to ensure secure deployments.

**Details:**

**Startup Validation and Keyring Parsing**
Startup validation is called at application startup to validate keyring configuration and prevent insecure deployments [7a]. Keyring parsing loads JWT_KEYRING from environment, falls back to JWT_SECRET, and supports both formats [7b].

**Placeholder Detection and Production Guard**
Placeholder detection detects common placeholder values like "change_me" and "placeholder" to identify insecure secrets [7c]. Production guard only enforces in production, allows placeholders in dev/test, and prevents production deployment with defaults [7d].

**Fail Closed**
Fail closed raises JWTKeyringError on failure to prevent application startup and provide a clear error message [7e].

## Trace ID: 8
**Title:** Token Revocation: Redis-Backed JTI Blacklist with TTL

**Description:** Revocation system - traces per-token revocation by storing JTI in Redis blacklist with TTL matching token expiry for logout and forced invalidation

**Motivation:**
EduBoost V2 implements a Redis-backed JTI blacklist for per-token revocation to enable logout and forced invalidation. When a token is revoked (e.g., user logout), its JTI is stored in Redis with a TTL matching the token's remaining lifetime. This ensures the revocation entry automatically expires when the token would naturally expire, preventing unbounded growth of the blacklist. The system provides fast lookup during token verification, checking if a JTI is in the blacklist before accepting the token. This approach balances performance (fast Redis lookups) with storage efficiency (automatic cleanup via TTL). The revocation system supports use cases like logout (revoke current token), password reset (revoke all user tokens), and admin actions (revoke specific tokens).

**Details:**
- **Execution Flow:** Revocation Entry Point → revoke_token(jti, exp_timestamp) → Calculate TTL from expiry (ttl_seconds = max(exp - now, 1)) → Store in Redis blacklist (_redis_set_with_ttl(key, ttl) with Redis SETEX operation, revoked_jti:{jti} = "1") → Verification Entry Point → is_token_revoked(jti) → Redis lookup (get_redis().get(key)) → Returns None if not revoked
- **Concurrency Safety:** Redis operations are atomic. TTL calculation is deterministic. No distributed locks needed as Redis provides atomic operations. Multiple revocations can run concurrently. Multiple verifications can run concurrently
- **Covered Objects:** JTI (token ID), Expiry timestamp, TTL calculation, Redis blacklist (revoked_jti:{jti}), Redis SETEX operation, Verification lookup
- **Timeouts:** TTL calculation: <1ms. Redis SETEX: ~5-10ms. Redis GET: ~5-10ms. Total revocation: ~5-10ms. Total verification: ~5-10ms
- **Migration Path:** From no revocation to JTI blacklist. Migration requires: 1) Implement revoke_token function, 2) Add is_token_revoked check, 3. Calculate TTL from expiry, 4) Integrate with logout flow, 5) Add to token verification
- **Error Handling:** Redis failures logged but don't block (fail open for availability). Invalid JTI logged. TTL calculation failures logged. All errors logged with context
- **Security Considerations:** TTL matches token expiry for automatic cleanup. Fast Redis lookups for verification. Fail open on Redis failures (availability). Per-token revocation granularity. Supports logout and forced invalidation

**Trace text diagram:**
```
Token Revocation Flow
├── Revocation Entry Point
│   └── revoke_token(jti, exp_timestamp) <-- 8a
│       ├── Calculate TTL from expiry
│       │   └── ttl_seconds = max(exp - now, 1) <-- 8b
│       └── Store in Redis blacklist
│           └── _redis_set_with_ttl(key, ttl) <-- 8c
│               └── Redis SETEX operation <-- token_revocation.py:26
│                   └── revoked_jti:{jti} = "1" <-- token_revocation.py:62
│
└── Verification Entry Point
    └── is_token_revoked(jti) <-- 8d
        └── Redis lookup
            └── get_redis().get(key) <-- 8e
                └── Returns None if not revoked <-- token_revocation.py:79
```

**Location ID: 8a**
- **Title:** Revoke token entry point
- **Description:** Revokes token by adding JTI to Redis blacklist with TTL
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/token_revocation.py:50

**Location ID: 8b**
- **Title:** Calculate remaining TTL
- **Description:** Computes TTL so revocation expires when token naturally expires
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/token_revocation.py:60

**Location ID: 8c**
- **Title:** Store in Redis blacklist
- **Description:** Persists revoked_jti:{jti} key in Redis with TTL
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/token_revocation.py:64

**Location ID: 8d**
- **Title:** Check revocation status
- **Description:** Queries Redis to determine if token has been revoked
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/token_revocation.py:71

**Location ID: 8e**
- **Title:** Redis lookup for JTI
- **Description:** Performs fast Redis GET to check blacklist membership
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/token_revocation.py:75

### AI Guide: Token Revocation

**Motivation:**
The token revocation system uses a Redis-backed JTI blacklist with TTL for per-token invalidation. Tokens are revoked and verified against the blacklist to enable logout and forced invalidation.

**Details:**

**Revocation and TTL Calculation**
Revocation is the entry point for token revocation that takes JTI and expiry timestamp and adds to blacklist [8a]. TTL calculation calculates remaining TTL from expiry to ensure automatic cleanup and prevent unbounded growth [8b].

**Redis Storage and Verification**
Redis storage stores revoked_jti:{jti} with TTL using SETEX for atomic operation and fast persistence [8c]. Verification checks if token is revoked by querying Redis blacklist and returns boolean [8d].

**Redis Lookup**
Redis lookup is a fast GET operation that returns None if not revoked with O(1) lookup time [8e].
