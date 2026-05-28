# JWT Security Implementation: Dual-System Architecture

EduBoost V2 implements two parallel JWT systems: the primary system (security.py + jwt_keyring) used by auth routes with JWT-based refresh tokens, and an alternative system (token_config.py) with opaque refresh tokens. Key security features include kid-based key rotation, Redis-backed revocation with DB fallback, and family-based refresh token reuse detection. Notable entry points: login at [1b], token creation at [2a], verification at [3b], and refresh rotation at [4b].

## Trace ID: 1
**Title:** Login Flow: Credentials to Token Pair

**Description:** Primary auth system - traces user login from API route through credential verification to token issuance with HTTP-only cookie

**Motivation:**
EduBoost V2 uses JWT-based authentication with refresh tokens to provide stateless API authentication while maintaining secure sessions. The system implements HTTP-only cookies for refresh token storage to protect against XSS attacks, and family-based refresh token rotation to detect and prevent replay attacks. This approach balances security (short-lived access tokens, single-use refresh tokens) with user experience (automatic token refresh without re-authentication). The dual-token pattern separates concerns: access tokens for API calls (short-lived, stateless) and refresh tokens for obtaining new access tokens (longer-lived, stateful with rotation).

**Details:**
- **Execution Flow:** Client sends credentials to `/auth/login` endpoint → API route delegates to auth service → Service verifies password with bcrypt → Generates refresh token JWT with family_id → Generates access token with user claims → Hashes and stores refresh token in Redis → Returns access token in response body and refresh token in HTTP-only cookie
- **Concurrency Safety:** Password verification uses constant-time bcrypt comparison to prevent timing attacks. Redis operations for token storage are atomic. No distributed locks needed as login is idempotent (multiple concurrent logins with same credentials create independent token pairs)
- **Covered Objects:** User credentials (email, password), User record (from database), Refresh token (JWT with family_id, JTI), Access token (JWT with claims), Redis storage (hashed refresh token with TTL), HTTP response (cookies)
- **Timeouts:** Password verification: ~100-300ms (bcrypt 12 rounds). Redis SETEX operation: <5ms. Overall login latency: ~200-400ms typical
- **Migration Path:** From session-based authentication (server-side sessions) to JWT-based stateless authentication. Existing sessions would need to be invalidated and users re-authenticated during migration
- **Error Handling:** Invalid credentials return 401 without revealing specific error. Database failures return 500. Redis failures fail closed (refuse login) to prevent issuing tokens without storage
- **Security Considerations:** Rate limiting on login endpoint prevents brute force. Account lockout after repeated failures. HTTPS required in production for cookie security. Password strength validation enforced at registration

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

### AI Guide: Login Flow - Credentials to Token Pair

**Motivation:**
The login flow implements a secure authentication mechanism that transforms user credentials into a token pair (access + refresh) with multiple security layers including password verification, JWT token generation, Redis-backed storage, and HTTP-only cookie delivery to ensure comprehensive security against common attack vectors.

**Details:**

**API Endpoint and Password Verification**
The API endpoint is a FastAPI route at `/auth/login` that receives POST requests with credentials and delegates to the auth service layer [1a]. Password verification uses bcrypt for constant-time password comparison to prevent timing attacks [1b].

**Token Generation**
Refresh token generation creates a JWT refresh token with `family_id` claim for rotation tracking [1c]. Access token generation creates a short-lived JWT access token (15 minutes) with user claims [1d].

**Token Storage and Cookie Delivery**
Token storage hashes the refresh token before storage in Redis with TTL matching token expiry [1e]. The HTTP-only cookie returns the refresh token in a secure, HTTP-only, SameSite=strict cookie [1f]. This provides constant-time password comparison to prevent timing attacks, JWT with kid header for key rotation, family-based refresh tokens to detect reuse, HTTP-only cookies for XSS protection, Redis-backed storage for fast validation, and token hashing to prevent plaintext storage.

## Trace ID: 2
**Title:** Access Token Creation with Keyring

**Description:** Primary JWT system - shows how access tokens are signed using the kid-based keyring with current signing key

**Motivation:**
EduBoost V2 implements a keyring-based JWT signing system to enable graceful cryptographic key rotation without service interruption or token invalidation. Traditional single-key JWT systems require all tokens to be invalidated when keys are rotated, causing user disruption. The keyring system uses a `kid` (key ID) header to identify which key signed each token, allowing the system to verify tokens signed with previous keys while signing new tokens with the current key. This approach supports security best practices (regular key rotation) while maintaining availability (no forced re-authentication).

**Details:**
- **Execution Flow:** Token creation function called → Build JWT payload with claims (sub, role, exp, iat, jti, type) → Get current signing key from keyring → Get current algorithm from keyring → Get current headers with kid → Encode JWT with jwt.encode() using key and algorithm → Return signed token
- **Concurrency Safety:** Keyring parsing is read-only and cached. JWT encoding is stateless and thread-safe. No locks needed as keyring is immutable during application runtime
- **Covered Objects:** JWT payload (claims), Keyring configuration (from environment), Current signing key (secret, algorithm, kid), JWT headers (kid), Signed JWT token
- **Timeouts:** Keyring parsing: ~1ms (cached). JWT encoding: ~1-5ms. Overall token creation: ~2-6ms
- **Migration Path:** From single-key JWT system to keyring-based system. Migration requires: 1) Add JWT_KEYRING environment variable with current key marked as 'current', 2) Deploy new code, 3) Gradually rotate keys by adding new key as 'next', 4) Mark new as 'current', old as 'previous', 5) Remove old key after token expiry
- **Error Handling:** Invalid keyring JSON raises JWTKeyringError at startup. Missing current key raises JWTKeyringError. Invalid algorithm raises JWTError. All errors fail closed (refuse to start or sign tokens)
- **Security Considerations:** Keys must be cryptographically random (256-bit minimum). Keyring configuration stored in environment variables, not in code. Production guard prevents placeholder secrets. Key rotation should be regular (every 90 days recommended)

**Trace text diagram:**
```
Access Token Creation Flow
├── create_access_token() entry point <-- security.py:50
│   ├── Build JWT payload with claims <-- security.py:52
│   │   ├── Add subject, role, expiry <-- security.py:53
│   │   └── Generate unique JTI <-- 2e
│   └── Encode JWT with keyring <-- 2a
│       ├── current_jwt_signing_key() <-- jwt_keyring.py:184
│       │   └── Get current signing key <-- 2b
│       │       └── current_jwt_key() <-- jwt_keyring.py:176
│       │           └── Select current key <-- 2c
│       ├── current_jwt_algorithm() <-- jwt_keyring.py:188
│       │   └── Extract algorithm from key <-- jwt_keyring.py:190
│       └── current_jwt_headers() <-- jwt_keyring.py:193
│           └── Add kid to JWT header <-- 2d
└── jwt.encode() signs token <-- security.py:61
```

**Location ID: 2a**
- **Title:** Encode JWT with keyring
- **Description:** Creates signed JWT using current key from keyring with kid header
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/security.py:61

**Location ID: 2b**
- **Title:** Get current signing key
- **Description:** Retrieves the active signing key from parsed keyring
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/jwt_keyring.py:184

**Location ID: 2c**
- **Title:** Select current key from keyring
- **Description:** Finds key marked as 'current' in the keyring configuration
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/jwt_keyring.py:178

**Location ID: 2d**
- **Title:** Add kid to JWT header
- **Description:** Includes key ID in JWT header for rotation support
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/jwt_keyring.py:194

**Location ID: 2e**
- **Title:** Generate unique token ID
- **Description:** Creates JTI claim for per-token revocation tracking
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/security.py:57

### AI Guide: Access Token Creation with Keyring

**Motivation:**
Access token creation demonstrates a sophisticated JWT signing system using a keyring with key rotation support. The system uses a `kid` (key ID) header to identify which key signed the token, enabling graceful key rotation without invalidating existing tokens.

**Details:**

**Keyring Architecture**
The keyring architecture uses JSON-based configuration stored in the `JWT_KEYRING` environment variable with multiple keys having status: `current`, `previous`, and `next` [2a]. Each key has a `kid` (unique ID), `secret` (signing key), and `algorithm` (e.g., HS256), supporting key rotation by marking the new key as `current` [2b].

**Key Rotation Strategy**
The key rotation strategy follows a four-phase process: Pre-Rotation (Key A marked as `current`, all tokens signed with Key A), Rotation Initiation (Add Key B as `next`, keep Key A as `current`), Rotation Complete (Mark Key B as `current`, Key A as `previous`), and Post-Rotation (Remove Key A after all tokens expire) [2c].

**Verification with kid**
Verification with kid extracts the `kid` from the JWT header, searches the keyring for the matching key, tries the matching key first for efficiency, and falls back to other keys if the match fails [2d]. This ensures that tokens signed with previous keys can still be validated during the rotation period.

## Trace ID: 3
**Title:** Token Verification with Revocation Checks

**Description:** Primary JWT system - traces token validation from HTTP bearer extraction through signature verification to revocation checks

**Motivation:**
EduBoost V2 implements multi-layered token verification to ensure both cryptographic validity and runtime security. Cryptographic signature verification ensures tokens haven't been tampered with, while runtime revocation checks enable immediate token invalidation without waiting for natural expiry. This dual approach supports security scenarios like password resets (revoke all user tokens), device logout (revoke specific token), and security incidents (global revocation). The system uses Redis for fast revocation lookups to maintain low latency while providing strong security guarantees.

**Details:**
- **Execution Flow:** FastAPI dependency extracts Bearer token from Authorization header → Decode token with keyring (tries matching kid first, then other keys) → Extract JTI and user_id from payload → Check per-token revocation in Redis (revoked_jti:{jti}) → Check user-level revocation in Redis (revoked_user:{user_id}) → Return validated payload or raise 401
- **Concurrency Safety:** Redis GET operations are atomic and thread-safe. Keyring is read-only and cached. No distributed locks needed as verification is read-only. Multiple concurrent verifications of same token are independent
- **Covered Objects:** Bearer token (from HTTP header), JWT payload (claims), Keyring (cached), Redis revocation storage (revoked_jti, revoked_user), Validated user context
- **Timeouts:** Header extraction: <1ms. Signature verification: ~1-5ms. Redis revocation checks: <1ms each. Total verification: ~2-7ms typical
- **Migration Path:** From simple signature-only verification to multi-layer verification with revocation. Migration requires: 1) Deploy Redis infrastructure, 2) Add revocation checks after signature verification, 3) Implement revocation endpoints, 4) Gradually enable revocation checks
- **Error Handling:** Missing Bearer header returns 401. Invalid signature returns 401. Expired token returns 401. Revoked token returns 401. Redis unavailability fails open (assumes not revoked) to prevent service disruption. All errors logged for security monitoring
- **Security Considerations:** Always check revocation after signature verification. Use appropriate TTL for revocation entries. Implement Redis fallback for high availability. Cache keyring for performance. Log all verification failures for security monitoring

**Trace text diagram:**
```
Token Verification Flow
├── FastAPI Dependency Injection
│   └── get_current_user() dependency <-- 3a
│       └── decode_token() <-- 3b
│           └── decode_jwt_with_keyring() <-- security.py:80
│               ├── get_unverified_header() <-- 3c
│               ├── parse_jwt_keyring() <-- jwt_keyring.py:228
│               └── jwt.decode() signature verify <-- 3d
├── Revocation Checks
│   ├── Per-token JTI check <-- 3e
│   │   └── is_token_revoked() <-- security.py:108
│   │       └── Redis GET operation <-- 3f
│   └── User-level revocation check <-- 3g
│       └── is_user_revoked() <-- security.py:117
│           └── Redis GET revoked_user:{id} <-- token_revocation.py:107
└── Return validated payload <-- security.py:124
```

**Location ID: 3a**
- **Title:** Extract and decode token
- **Description:** FastAPI dependency extracts Bearer token and decodes payload
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/security.py:100

**Location ID: 3b**
- **Title:** Decode with keyring
- **Description:** Attempts verification with current and previous keys from keyring
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/security.py:80

**Location ID: 3c**
- **Title:** Extract kid from header
- **Description:** Reads kid claim to determine which key to try first
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/jwt_keyring.py:226

**Location ID: 3d**
- **Title:** Verify signature with key
- **Description:** Cryptographically validates JWT signature and expiry
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/jwt_keyring.py:233

**Location ID: 3e**
- **Title:** Check per-token revocation
- **Description:** Queries Redis blacklist for revoked JTI
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/security.py:108

**Location ID: 3f**
- **Title:** Redis revocation lookup
- **Description:** Checks if JTI exists in Redis deny-list with TTL
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/token_revocation.py:75

**Location ID: 3g**
- **Title:** Check user-level revocation
- **Description:** Verifies user hasn't had all tokens revoked (e.g., password reset)
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/security.py:117

### AI Guide: Token Verification with Revocation Checks

**Motivation:**
Token verification implements a multi-layered security approach combining cryptographic signature verification with runtime revocation checks. This ensures tokens are both cryptographically valid and haven't been revoked since issuance, providing defense in depth.

**Details:**

**Verification Layers**
The verification layers include token extraction where a FastAPI dependency extracts the `Authorization: Bearer <token>` header [3a], signature verification that validates the signature with the keyring and tries the matching kid first [3b-3d], per-token revocation that checks the Redis blacklist for revoked JTI [3e-3f], and user-level revocation that checks if the user's all tokens have been revoked [3g].

**Revocation Strategies**
Revocation strategies include per-token revocation (revokes individual token by JTI for logout from specific device), user-level revocation (revokes all tokens for a user for password reset), family-based revocation (revokes refresh token family for reuse detection), and global revocation (revokes all tokens issued before timestamp for security incidents).

**Security Benefits**
Security benefits include cryptographic validation ensuring the token hasn't been tampered with, key rotation support verifying tokens signed with previous keys, runtime revocation invalidating tokens before expiry, multi-layer checks providing defense in depth, and fast revocation via Redis sub-millisecond lookups.

## Trace ID: 4
**Title:** Refresh Token Rotation: Consume and Reissue

**Description:** Primary JWT system - shows single-use refresh token consumption with family-based reuse detection and new token pair issuance

**Motivation:**
EduBoost V2 implements single-use refresh token rotation to detect and prevent replay attacks. If a refresh token is stolen (e.g., via XSS), an attacker could use it to obtain new access tokens indefinitely. The single-use property ensures each refresh token can only be used once. Family-based tracking links all tokens in a rotation chain; if reuse is detected, the entire family is revoked, indicating potential token theft. This approach provides strong security while maintaining user experience (automatic token refresh) and graceful degradation (users can re-authenticate if family is revoked).

**Details:**
- **Execution Flow:** Client sends refresh token in HTTP-only cookie → Decode and validate token → Check if family already revoked → Compare token hash with stored hash (constant-time) → If mismatch or missing, revoke family and raise 401 → Delete token from Redis (single-use) → Extract family_id → Create new refresh token with same family_id → Create new access token → Store new refresh token in Redis → Return new token pair
- **Concurrency Safety:** Token consumption uses atomic Redis operations (check and delete). Constant-time hash comparison prevents timing attacks. Family revocation uses Redis SET with TTL. Race conditions possible if same token used concurrently; first request succeeds, second fails with reuse detection
- **Covered Objects:** Refresh token (from cookie), Token hash (SHA-256), Redis storage (hashed token, family metadata), Family ID, New token pair (refresh + access)
- **Timeouts:** Token validation: ~1-5ms. Hash comparison: <1ms. Redis operations: ~2-5ms. Token generation: ~2-6ms. Total refresh: ~5-15ms typical
- **Migration Path:** From long-lived refresh tokens to single-use rotation. Migration requires: 1) Add family_id to existing tokens, 2) Implement consume-and-reissue logic, 3) Deploy new refresh endpoint, 4) Update clients to use new endpoint, 5) Gradually enable single-use enforcement
- **Error Handling:** Invalid token returns 401. Family already revoked returns 401. Token reuse detected triggers family revocation and returns 401. Redis unavailability fails closed (refuse refresh) to prevent token issuance without storage. All errors logged for security monitoring
- **Security Considerations:** Always rotate refresh tokens on use. Use constant-time comparison for hash checks. Log family revocation events for security monitoring. Implement rate limiting on refresh endpoint. Use short refresh token expiry (7-30 days)

**Trace text diagram:**
```
Refresh Token Rotation Flow
├── API Route Handler
│   └── /auth/refresh endpoint <-- auth.py:146
│       └── auth_lifecycle_impl.refresh_impl() <-- auth_lifecycle_impl.py:171
│           └── consume_refresh_token(token) <-- 4a
│
├── Token Consumption & Validation
│   └── refresh_tokens.py
│       ├── is_refresh_family_revoked() <-- 4b
│       ├── hmac.compare_digest() check <-- 4c
│       ├── revoke_refresh_family() <-- 4d
│       │   └── (if reuse detected)
│       └── cache_delete(jti) <-- 4e
│
└── New Token Pair Issuance
    └── auth_lifecycle_impl.refresh_impl() <-- auth_lifecycle_impl.py:171
        ├── create_refresh_token(family_id) <-- 4f
        ├── create_access_token() <-- auth_lifecycle_impl.py:200
        └── store_refresh_token() <-- 4g
            └── Redis persistence <-- refresh_tokens.py:68
```

**Location ID: 4a**
- **Title:** Consume refresh token
- **Description:** Validates and deletes refresh token in single atomic operation
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/auth_lifecycle_impl.py:182

**Location ID: 4b**
- **Title:** Check family revocation
- **Description:** Detects if token family was revoked due to reuse (security breach)
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/refresh_tokens.py:78

**Location ID: 4c**
- **Title:** Timing-safe hash comparison
- **Description:** Verifies token hash matches stored value using constant-time comparison
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/refresh_tokens.py:82

**Location ID: 4d**
- **Title:** Revoke family on reuse
- **Description:** Immediately revokes entire token family if reuse detected (replay attack)
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/refresh_tokens.py:83

**Location ID: 4e**
- **Title:** Delete consumed token
- **Description:** Removes token from Redis ensuring single-use property
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/refresh_tokens.py:89

**Location ID: 4f**
- **Title:** Issue new refresh token
- **Description:** Creates new refresh token inheriting same family_id for rotation chain
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/auth_lifecycle_impl.py:189

**Location ID: 4g**
- **Title:** Store new token
- **Description:** Persists new refresh token completing the rotation cycle
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/auth_lifecycle_impl.py:201

### AI Guide: Refresh Token Rotation: Consume and Reissue

**Motivation:**
Refresh token rotation implements a security-critical single-use token pattern that detects replay attacks through family-based tracking. Each refresh token can only be used once; reuse triggers immediate family revocation to prevent token theft exploitation.

**Details:**

**Rotation Security Model**
The rotation security model includes the single-use property where each refresh token can be used exactly once and is deleted immediately after use [4a], family-based tracking where all tokens in the rotation chain share the same `family_id` for reuse detection [4b], reuse detection where if the hash doesn't match or token is missing it indicates reuse and triggers family revocation [4c], and atomic consumption that validates the token and deletes it in a single operation to prevent race conditions [4d].

**Attack Scenario**
The attack scenario demonstrates the security: an attacker steals the refresh token from XSS, attempts to use the token, the legitimate user refreshes first (token consumed), the attacker's reuse attempt triggers family revocation, and both the user and attacker must re-authenticate.

**Security Benefits**
Security benefits include replay attack prevention via single-use tokens, theft detection through family revocation, graceful degradation (valid users can re-authenticate), audit trail via family revocation event logging, and constant-time comparison preventing timing attacks.

## Trace ID: 5
**Title:** Key Rotation: Validation and Multi-Key Support

**Description:** Keyring system - demonstrates startup validation of JWT keys and multi-key verification for graceful rotation

**Motivation:**
EduBoost V2 implements application startup validation for JWT keyring configuration to prevent deployment with invalid or placeholder secrets. Cryptographic key rotation is a security best practice, but misconfiguration can cause service disruption. The startup validation ensures keys are properly configured before accepting requests, with a production guard that fails closed if placeholder secrets are detected. This prevents accidental deployment with default credentials, which would be a critical security vulnerability. The system also supports legacy JWT_SECRET fallback for backward compatibility during migration.

**Details:**
- **Execution Flow:** Application starts → validate_jwt_keyring_environment() called → Check if running in production environment → Parse JWT_KEYRING from environment or fallback to JWT_SECRET → Build JWTKey objects from configuration → Detect placeholder secrets (change_me, placeholder, default) → If production and placeholders found, raise JWTKeyringError and fail startup → If validation passes, continue application startup
- **Concurrency Safety:** Validation runs once at startup in main process. No concurrency concerns as validation completes before workers fork. Keyring is immutable after validation. No locks needed
- **Covered Objects:** JWT_KEYRING environment variable (JSON), JWT_SECRET environment variable (legacy), JWTKey objects (kid, secret, algorithm, status), Production environment flag, Placeholder detection patterns
- **Timeouts:** Environment check: <1ms. Keyring parsing: ~1-5ms. Placeholder detection: <1ms. Total validation: ~2-7ms at startup
- **Migration Path:** From single JWT_SECRET to keyring-based system. Migration requires: 1) Add JWT_KEYRING environment variable with current key marked as 'current', 2) Keep JWT_SECRET as fallback, 3) Deploy new code, 4) Remove JWT_SECRET after all instances migrated, 5) Enable production placeholder guard
- **Error Handling:** Invalid JSON raises JWTKeyringError. Missing current key raises JWTKeyringError. Placeholder secrets in production raise JWTKeyringError. All errors fail closed (refuse to start). Errors logged with clear messages for debugging
- **Security Considerations:** Keys must be cryptographically random (256-bit minimum). Production guard prevents placeholder secrets. Keyring configuration stored in environment variables, not in code. Legacy JWT_SECRET support for backward compatibility only. Regular key rotation (every 90 days recommended)

**Trace text diagram:**
```
JWT Key Rotation & Validation System
├── Application Startup
│   └── app/api_v2.py
│       └── validate_jwt_keyring_environment() <-- 5a
│           ├── Check environment type
│           │   └── is_production_environment() check <-- jwt_keyring.py:73
│           ├── Parse keyring configuration <-- 5c
│           │   ├── Load JWT_KEYRING JSON <-- jwt_keyring.py:147
│           │   └── Build JWTKey objects <-- 5d
│           │   └── Fallback to JWT_SECRET <-- jwt_keyring.py:136
│           ├── Detect placeholder secrets <-- 5f
│           │   └── Check for "change_me" patterns
│           └── Production guard: fail if placeholder <-- 5b
│
└── Token Verification Flow
    └── decode_jwt_with_keyring() <-- jwt_keyring.py:224
        ├── Extract kid from JWT header <-- jwt_keyring.py:226
        ├── Sort keys by kid match <-- 5e
        │   └── Matching kid tried first
        └── Try each key until success <-- jwt_keyring.py:231
            └── jwt.decode(token, key.secret) <-- jwt_keyring.py:233
```

**Location ID: 5a**
- **Title:** Startup validation
- **Description:** Application startup validates JWT configuration before accepting requests
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/api_v2.py:29

**Location ID: 5b**
- **Title:** Production placeholder guard
- **Description:** Fails closed if production environment uses placeholder secrets
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/jwt_keyring.py:211

**Location ID: 5c**
- **Title:** Parse keyring configuration
- **Description:** Loads JWT_KEYRING JSON or falls back to legacy JWT_SECRET
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/jwt_keyring.py:209

**Location ID: 5d**
- **Title:** Build key objects
- **Description:** Constructs JWTKey objects with kid, secret, algorithm, and status
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/jwt_keyring.py:152

**Location ID: 5e**
- **Title:** Prioritize matching kid
- **Description:** Tries key matching JWT's kid header first, then falls back to others
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/jwt_keyring.py:229

**Location ID: 5f**
- **Title:** Detect placeholder secrets
- **Description:** Identifies insecure default secrets that must not reach production
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/jwt_keyring.py:204

### AI Guide: Key Rotation: Validation and Multi-Key Support

**Motivation:**
The keyring system implements a robust key rotation mechanism with startup validation, placeholder detection, and multi-key verification. This ensures cryptographic keys are properly configured and enables graceful key rotation without service interruption.

**Details:**

**Startup Validation**
Startup validation includes environment check to determine if running in production for stricter validation [5a], keyring parsing to load JWT_KEYRING JSON or fall back to legacy JWT_SECRET [5b], placeholder detection to check for "change_me", "placeholder", "default" patterns [5c], and production guard that fails application startup if placeholders are detected in production [5d].

**Keyring Structure**
The keyring structure is a JSON-based configuration stored in the JWT_KEYRING environment variable with multiple keys having status: `current`, `previous`, and `next`. Each key has a `kid` (unique ID), `secret` (signing key), and `algorithm` (e.g., HS256).

**Rotation Procedure**
The rotation procedure includes preparation (generate new secret, add as `next`, test in staging), rotation (deploy, mark new as `current`, old as `previous`), and cleanup (wait for token expiry, remove old key). Multi-key verification ensures that tokens signed with previous keys can still be validated during the rotation period by extracting the kid from the JWT header, sorting keys by kid match for optimization, trying each key until success, and supporting tokens signed with previous keys.

## Trace ID: 6
**Title:** Token Revocation: Redis with DB Fallback

**Description:** Revocation system - shows dual-layer revocation with fast Redis lookup and persistent DB storage

**Motivation:**
EduBoost V2 implements a dual-layer token revocation system to balance performance with resilience. Redis provides sub-millisecond lookups for runtime revocation checks, ensuring low latency for API requests. Database persistence provides resilience against Redis restarts or failures, preventing revocation data loss. This dual-layer approach supports multiple revocation strategies (per-token, user-level, family-based, global) for different security scenarios while maintaining high availability. The system automatically cleans up expired revocations via TTL to prevent memory bloat.

**Details:**
- **Execution Flow:** Revocation request received → For per-token: Redis SETEX with TTL matching token expiry, then DB INSERT for persistence → For user-level: Redis SET with long TTL (30 days) → For family-based: Redis SET for family_id, then pattern delete all tokens in family → For global: Redis SET epoch timestamp, verification checks token iat against epoch
- **Concurrency Safety:** Redis SETEX and SET operations are atomic. DB INSERT uses primary key constraint for idempotency. Pattern deletion is atomic in Redis. No distributed locks needed as revocation is idempotent (multiple revocations of same token are safe)
- **Covered Objects:** JTI (JWT ID), User ID, Family ID, Epoch timestamp, Redis storage (revoked_jti, revoked_user, revoked_family, revoke_all_epoch), Database table (revoked_tokens)
- **Timeouts:** Redis SETEX: <5ms. DB INSERT: ~5-10ms. Pattern deletion: ~5-10ms. Total revocation: ~10-20ms typical
- **Migration Path:** From Redis-only to dual-layer system. Migration requires: 1) Create revoked_tokens table in database, 2) Add DB INSERT after Redis SETEX, 3) Implement Redis restart recovery to load from DB, 4) Monitor Redis memory usage, 5) Gradually increase TTL for DB fallback
- **Error Handling:** Redis unavailability fails open (assumes not revoked) to prevent service disruption, but logs warning. DB unavailability logs warning but continues with Redis-only. Pattern deletion failures logged but don't block revocation. All errors logged for monitoring
- **Security Considerations:** Use Redis for fast runtime checks. Use DB for persistence and recovery. Set appropriate TTL for revocation entries. Implement Redis restart recovery. Log all revocation events. Monitor Redis memory usage. Use separate Redis instance for security data

**Trace text diagram:**
```
Token Revocation System
├── Per-Token Revocation (JTI-based)
│   ├── revoke_token() in token_revocation.py <-- token_revocation.py:50
│   │   └── Redis SETEX with TTL <-- 6a
│   └── Persistent DB Fallback
│       ├── add_persistent_revocation_fallback() <-- token_config.py:228
│       │   ├── Import persist_revocation <-- 6b
│       │   └── Call repository method <-- token_config.py:241
│       └── GuardianRepository.revoke_jti() <-- auth_repository.py:32
│           └── INSERT INTO revoked_tokens <-- 6c
├── User-Level Revocation (all tokens)
│   └── revoke_user_tokens() <-- token_revocation.py:87
│       └── Redis SET revoked_user:{id} <-- 6d
├── Family-Based Revocation (refresh tokens)
│   └── revoke_refresh_family() <-- refresh_tokens.py:112
│       └── Redis SET family revoked flag <-- 6e
└── Emergency Global Revocation (all tokens)
    └── emergency_revoke_all() <-- token_config.py:220
        └── Redis SET epoch timestamp <-- 6f
```

**Location ID: 6a**
- **Title:** Add JTI to Redis blacklist
- **Description:** Stores revoked JTI in Redis with TTL matching token expiry
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/token_revocation.py:64

**Location ID: 6b**
- **Title:** Import DB fallback
- **Description:** Lazy import of repository for persistent revocation storage
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/token_config.py:240

**Location ID: 6c**
- **Title:** Persist to database
- **Description:** Inserts revoked JTI into revoked_tokens table for Redis restart resilience
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/repositories/auth_repository.py:34

**Location ID: 6d**
- **Title:** User-level revocation
- **Description:** Revokes all tokens for a user (e.g., password reset, account compromise)
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/token_revocation.py:96

**Location ID: 6e**
- **Title:** Family revocation
- **Description:** Marks entire refresh token family as revoked for reuse detection
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/refresh_tokens.py:116

**Location ID: 6f**
- **Title:** Emergency global revocation
- **Description:** Sets epoch timestamp invalidating all tokens issued before that time
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/token_config.py:224

### AI Guide: Token Revocation: Redis with DB Fallback

**Motivation:**
The revocation system implements a dual-layer approach combining fast Redis lookups for runtime performance with persistent database storage for resilience against Redis restarts. Multiple revocation strategies support different security scenarios including per-token, user-level, family-based, and emergency global revocation.

**Details:**

**Revocation Strategies**
Revocation strategies include per-token revocation (revokes individual token by JTI for logout from specific device), user-level revocation (revokes all tokens for a user for password reset), family-based revocation (revokes entire refresh token family for reuse detection), and emergency global revocation (revokes all tokens issued before timestamp for security incidents).

**Dual-Layer Storage**
Dual-layer storage includes Layer 1 (Redis) for fast storage with TTL for automatic cleanup and Layer 2 (Database) for persistent storage for Redis restart resilience. The Redis storage structure uses keys like `revoked_jti:{jti}`, `revoked_user:{user_id}`, `revoked_family:{family_id}`, and `revoke_all_epoch` with appropriate TTL values.

**Database Schema and Recovery**
The database schema includes a `revoked_tokens` table with jti as primary key, revoked_at timestamp, expires_at timestamp, and an index on expires_at. Redis restart recovery loads revocations from the database to rebuild Redis state on startup, ensuring resilience against Redis restarts. This provides fast revocation via Redis sub-millisecond lookups, persistence via DB fallback to survive Redis restarts, multiple strategies for different scenarios, automatic cleanup via TTL to prevent memory bloat, and mass invalidation via global revocation.

## Trace ID: 7
**Title:** Alternative System: Opaque Refresh Tokens

**Description:** Alternative JWT system (token_config.py) - demonstrates opaque random-byte refresh tokens with SHA-256 hashing instead of JWT format

**Motivation:**
EduBoost V2 implements an alternative opaque refresh token system as a simpler alternative to JWT-based refresh tokens. While the primary system uses JWT refresh tokens with embedded claims and signature verification, the alternative system uses cryptographically random bytes with SHA-256 hashing. This approach provides simpler token structure (no JWT claims or signature verification), smaller token size (64 bytes vs JWT with claims), and eliminates key management requirements. The system is designed for scenarios where database lookup performance is acceptable and simpler token management is preferred. This represents a trade-off between simplicity (opaque tokens) and functionality (JWT with embedded claims).

**Details:**
- **Execution Flow:** Token creation: Generate 64 random bytes using secrets.token_urlsafe(64) → Hash token with SHA-256 → Create RefreshTokenRecord with family_id, user_id, hashed_token, expires_at → Return raw token and record. Token verification: Receive raw token → Hash with SHA-256 → Query database for matching hash → If found and not expired, create new token pair → Delete old token (single-use) → Return new tokens
- **Concurrency Safety:** Token generation is stateless and thread-safe. Database operations use primary key constraints for idempotency. Single-use property enforced by DELETE after verification. Race conditions possible if same token used concurrently; first request succeeds, second fails
- **Covered Objects:** Raw token (64 random bytes), Hashed token (SHA-256), RefreshTokenRecord (family_id, user_id, hashed_token, expires_at), Database table (refresh_tokens)
- **Timeouts:** Token generation: <1ms. Hash computation: <1ms. Database INSERT: ~5-10ms. Database lookup: ~5-10ms. Total refresh: ~10-20ms typical
- **Migration Path:** From JWT refresh tokens to opaque tokens. Migration requires: 1) Create refresh_tokens table in database, 2) Deploy new token creation logic, 3) Update clients to handle opaque tokens, 4) Migrate existing JWT tokens to opaque format, 5) Remove JWT refresh token system
- **Error Handling:** Database unavailability fails closed (refuse token issuance). Token not found returns 401. Expired token returns 401. Hash collision negligible (SHA-256). All errors logged for monitoring
- **Security Considerations:** Use cryptographically secure random generation. Hash tokens before storage. Implement single-use property. Use appropriate token expiry (7-30 days). Index database for fast lookups. Database security (encryption at rest, access controls)

**Trace text diagram:**
```
Alternative JWT System (token_config.py)
├── Token Creation Flow
│   ├── auth_service.login() calls <-- auth_service.py:199
│   │   └── _issue_token_pair() <-- 7e
│   │       └── create_refresh_token(family_id) <-- token_config.py:130
│   │           ├── secrets.token_urlsafe(64) <-- 7a
│   │           ├── _hash_token(raw) <-- 7b
│   │           │   └── hashlib.sha256().hexdigest() <-- 7c
│   │           └── RefreshTokenRecord(...) <-- 7d
│   │               └── returns (raw, hashed, record) <-- token_config.py:146
└── Token Verification Flow
    └── auth_service.refresh() receives token <-- auth_service.py:262
        └── hash incoming token <-- 7f
            └── compare with stored hash in DB <-- auth_service.py:269
                └── issue new token pair if valid <-- auth_service.py:297
```

**Location ID: 7a**
- **Title:** Generate opaque token
- **Description:** Creates cryptographically random 64-byte URL-safe token (not a JWT)
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/token_config.py:136

**Location ID: 7b**
- **Title:** Hash with SHA-256
- **Description:** Hashes raw token for at-rest storage, only hash is persisted
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/token_config.py:137

**Location ID: 7c**
- **Title:** SHA-256 hashing function
- **Description:** One-way hash ensures tokens cannot be reconstructed from storage
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/token_config.py:151

**Location ID: 7d**
- **Title:** Create token record
- **Description:** Builds metadata record with family_id, user_id, and expiry
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/token_config.py:140

**Location ID: 7e**
- **Title:** Service layer token issuance
- **Description:** Alternative auth service uses opaque tokens instead of JWT refresh tokens
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/auth_service.py:409

**Location ID: 7f**
- **Title:** Hash for verification
- **Description:** During refresh, incoming token is hashed to match against stored hash
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/auth_service.py:268

### AI Guide: Alternative System: Opaque Refresh Tokens

**Motivation:**
The alternative system implements opaque refresh tokens using cryptographically random bytes instead of JWT format. This approach provides simpler token structure while maintaining security through SHA-256 hashing and database persistence, offering a simpler alternative to the primary JWT-based system.

**Details:**

**Opaque vs JWT Refresh Tokens**
The comparison between opaque tokens and JWT refresh tokens shows differences in format (random bytes vs JSON Web Token), structure (no claims vs contains claims), verification (hash comparison vs signature verification), storage (database only vs Redis + DB fallback), and complexity (simpler vs more complex).

**Token Creation**
Token creation generates a random token using `secrets.token_urlsafe(64)` for cryptographic randomness [7a], hashes the token for storage using SHA-256 [7b][7c], and creates a metadata record with family_id, hashed_token, and expires_at [7d].

**Security Properties**
Security properties include cryptographic randomness (64 bytes = 512 bits of entropy), one-way hashing with SHA-256 before storage, and database persistence for token storage. This provides a simpler alternative to JWT refresh tokens while maintaining strong security through cryptographic randomness and one-way hashing. The single-use property ensures the token is deleted after successful refresh, and family tracking via family_id enables the rotation chain. Advantages include simpler structure with no JWT claims or signature verification, smaller size (64 bytes vs JWT with claims), no key management required, and database-centric for easier auditing. Disadvantages include database dependency for verification, slower verification (DB query vs Redis lookup), no embedded claims requiring database queries for user info, and scalability concerns for high traffic. This system is appropriate when simpler token structure is preferred, database lookup performance is acceptable, traffic volume is lower, and direct token management in database is desired.

## Trace ID: 8
**Title:** Password Security: Bcrypt Hashing and Strength Validation

**Description:** Password system - traces password hashing with bcrypt and strength validation including HIBP breach checking

**Motivation:**
EduBoost V2 implements defense-in-depth password security to protect user credentials against multiple attack vectors. Bcrypt hashing with 12 rounds provides slow, salted hashing resistant to brute force attacks. Password strength validation enforces complex passwords to resist dictionary attacks. Have I Been Pwned (HIBP) breach checking prevents users from choosing passwords that have appeared in known data breaches. Constant-time password comparison prevents timing attacks that could reveal password information. This multi-layered approach ensures passwords are stored securely, users cannot choose weak or compromised passwords, and authentication is resistant to various attack methods.

**Details:**
- **Execution Flow:** Registration/Password Change: Check password strength (length, character types, common passwords) → Check if password breached via HIBP API (SHA-1 hash, send prefix, compare suffixes) → If valid, hash password with bcrypt (12 rounds) → Store hashed password in database. Login/Authentication: Retrieve hashed password from database → Verify password with constant-time bcrypt comparison → Return success or failure
- **Concurrency Safety:** Password hashing is stateless and thread-safe. Bcrypt verification is constant-time and thread-safe. HIBP API calls are independent per request. No locks needed as password operations are independent. Database operations use standard transaction isolation
- **Covered Objects:** Plain password (user input), Hashed password (bcrypt), Password strength rules, HIBP API response, User record (database)
- **Timeouts:** Password strength check: <1ms. HIBP API call: ~100-500ms (with timeout). Bcrypt hashing: ~100-300ms (12 rounds). Bcrypt verification: ~100-300ms. Total registration: ~200-800ms typical
- **Migration Path:** From weaker hashing (e.g., MD5, SHA-1) to bcrypt. Migration requires: 1) Add bcrypt hashing for new passwords, 2) Implement rehash on login for existing passwords, 3) Add password strength validation, 4) Add HIBP breach checking, 5) Force password reset for weak passwords
- **Error Handling:** HIBP API timeout fails open (allows password) to prevent blocking registration. Database failures return 500. Invalid password strength returns 400 with specific errors. Breached password returns 400 with clear message. All errors logged for monitoring
- **Security Considerations:** Use bcrypt with 12+ rounds. Enforce minimum 10-character passwords. Require mix of character types. Check against breach databases. Implement rate limiting on registration. Log failed registration attempts. Educate users on password security. Constant-time comparison prevents timing attacks

**Trace text diagram:**
```
Password Security Flow
├── Registration/Password Change Entry
│   ├── auth_service.guardian_signup() <-- 8f
│   │   └── check_password_strength() validation <-- password.py:78
│   │       ├── Length check (min 10 chars) <-- 8c
│   │       ├── Uppercase/lowercase/digit checks <-- password.py:89
│   │       ├── Special character requirement <-- password.py:98
│   │       └── Common password blocklist <-- password.py:101
│   └── is_password_breached() HIBP check <-- 8d
│       ├── SHA-1 hash password <-- 8d
│       ├── HTTP GET to HIBP API <-- 8e
│       └── Compare suffix matches <-- password.py:131
├── Password Storage
│   └── hash_password() <-- 8a
│       └── bcrypt with 12 rounds <-- password.py:32
│           └── passlib CryptContext <-- password.py:29
└── Login/Authentication
    └── verify_password() <-- 8b
        └── Constant-time bcrypt comparison
            └── passlib verify() <-- password.py:43
```

**Location ID: 8a**
- **Title:** Hash with bcrypt
- **Description:** Uses passlib CryptContext with 12 rounds for production-safe hashing
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/password.py:38

**Location ID: 8b**
- **Title:** Constant-time verification
- **Description:** Timing-safe password comparison prevents timing attacks
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/password.py:43

**Location ID: 8c**
- **Title:** Enforce minimum length
- **Description:** Requires 10+ characters for password strength
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/password.py:86

**Location ID: 8d**
- **Title:** Hash for HIBP check
- **Description:** SHA-1 hash for k-anonymity breach checking via Have I Been Pwned API
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/password.py:120

**Location ID: 8e**
- **Title:** Query HIBP API
- **Description:** Sends first 5 chars of hash to HIBP, receives matching suffixes
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/password.py:124

**Location ID: 8f**
- **Title:** Reject breached passwords
- **Description:** Prevents use of passwords found in known data breaches
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/auth_service.py:169

### AI Guide: Password Security: Bcrypt Hashing and Strength Validation

**Motivation:**
The password security system implements defense-in-depth with bcrypt hashing, comprehensive strength validation, and breach checking via Have I Been Pwned (HIBP) API. This ensures passwords are stored securely and users cannot choose weak or compromised passwords.

**Details:**

**Password Hashing**
Password hashing uses passlib with bcrypt algorithm, 12 rounds for production, automatic salt generation, and the format `$2b$12$<salt><hash>` with a work factor of 2^12 = 4,096 iterations [8a]. This provides slow, salted hashing that is resistant to brute force attacks.

**Password Verification**
Password verification uses the passlib context to verify passwords against stored hashes with constant-time comparison to prevent timing attacks [8b]. This ensures that password verification cannot be used to extract password information through timing analysis.

**Password Strength Validation**
Password strength validation enforces minimum 10 characters, uppercase and lowercase letters, at least one digit, special character required, and a common password blocklist [8c]. This ensures users choose strong, complex passwords.

**HIBP Breach Checking**
HIBP breach checking uses the k-anonymity protocol to check if a password appears in known data breaches without revealing the full password to the API [8d][8e]. The k-anonymity protocol hashes the password with SHA-1, sends the first 5 characters (prefix) to the HIBP API, receives all hash suffixes matching that prefix, and checks if the remaining suffix matches. HIBP never sees the full hash, only the prefix, preserving privacy during breach checking.

---

## Code snippets from Codemap files

### File: /home/nkgolol/Dev/Development/Eduboost-V2/app/repositories/auth_repository.py

Lines: 32-36
```python
    async def revoke_jti(self, jti: str, expires_at: datetime, db: AsyncSessi...
        """Mark a JWT JTI as revoked so it can't be reused."""
        await db.execute(
            text(
                "INSERT INTO revoked_tokens (jti, revoked_at, expires_at) "
```

### File: /home/nkgolol/Dev/Development/Eduboost-V2/app/services/auth_service.py

Lines: 167-171
```python

        # Breached password check (§3.2 P1 — fail open on HIBP timeout)
        if await is_password_breached(password):
            raise AuthError(
                "This password has appeared in a known data breach. Please ch...
```

Lines: 266-270
```python
        """
        import hashlib
        hashed = hashlib.sha256(raw_refresh_token.encode()).hexdigest()
        record = await self._tokens.find_refresh_token(hashed)
```

Lines: 407-411
```python
            role=user["role"],
        )
        raw_refresh, hashed_refresh, record = create_refresh_token(family_id)
        record = record.model_copy(update={"user_id": user["user_id"]})
```

### File: /home/nkgolol/Dev/Development/Eduboost-V2/app/core/password.py

Lines: 36-45
```python
def hash_password(plain: str) -> str:
    """Return a bcrypt hash of *plain*."""
    return _pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """Constant-time comparison of *plain* against *hashed*."""
    return _pwd_context.verify(plain, hashed)
```

Lines: 84-88
```python
    errors: list[str] = []

    if len(password) < _MIN_LENGTH:
        errors.append(f"Password must be at least {_MIN_LENGTH} characters.")
```

Lines: 118-126
```python
    hash are sent to the HIBP API. Returns False on network error (fail open).
    """
    sha1 = hashlib.sha1(password.encode("utf-8"), usedforsecurity=False).hexd...
    prefix, suffix = sha1[:5], sha1[5:]
    try:
        async with httpx.AsyncClient(timeout=_HIBP_TIMEOUT) as client:
            resp = await client.get(
                _HIBP_URL.format(prefix=prefix),
                headers={"Add-Padding": "true"},
```

### File: /home/nkgolol/Dev/Development/Eduboost-V2/app/services/auth_lifecycle_impl.py

Lines: 150-158
```python
    email_hash = hash_email(submitted_email)
    guardian = await repo.get_by_email_hash(email_hash)
    if not guardian or not verify_password(body.password, guardian.password_h...
        await audit.auth_event("USER_LOGIN_FAILED", guardian.id if guardian e...
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=...

    refresh = create_refresh_token(guardian.id, guardian.role)
    refresh_payload = decode_token(refresh)
    claims = _canonical_access_claims(
```

Lines: 160-167
```python
        extra={"refresh_jti": refresh_payload.get("jti"), "refresh_family": r...
    )
    access = create_access_token(guardian.id, guardian.role, claims)

    await store_refresh_token(refresh)
    _set_refresh_cookie(response, refresh)
    await audit.auth_event("USER_LOGIN", guardian.id)
```

Lines: 180-184
```python
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=...

    payload = await consume_refresh_token(token)

    repo = auth_runtime.guardian_repo
```

Lines: 187-191
```python
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=...

    new_refresh = create_refresh_token(guardian.id, guardian.role, family_id=...
    new_refresh_payload = decode_token(new_refresh)
    
```

Lines: 199-203
```python
    )
    access = create_access_token(guardian.id, guardian.role, claims)
    await store_refresh_token(new_refresh)
    await FourthEstateService(db).auth_event("USER_TOKEN_REFRESHED", guardian...
    _set_refresh_cookie(response, new_refresh)
```

### File: /home/nkgolol/Dev/Development/Eduboost-V2/app/core/security.py

Lines: 55-63
```python
        "exp": expire,
        "iat": datetime.now(UTC),
        "jti": str(uuid.uuid4()),
        "type": "access",
        **(extra or {}),
    }
    return jwt.encode(payload, current_jwt_signing_key(), algorithm=current_j...
```

Lines: 78-82
```python
def decode_token(token: str) -> dict[str, Any]:
    try:
        return decode_jwt_with_keyring(token)
    except JWTError as exc:
        raise HTTPException(
```

Lines: 98-102
```python
            headers={"WWW-Authenticate": "Bearer"},
        )
    payload = decode_token(credentials.credentials)
    
    # Check if token type is correct
```

Lines: 106-110
```python
    # Check if token has been revoked (by JTI)
    jti = payload.get("jti")
    if jti and await is_token_revoked(jti):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
```

Lines: 115-119
```python
    # Check if user's all tokens have been revoked
    user_id = payload.get("sub")
    if user_id and await is_user_revoked(user_id):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
```

### File: /home/nkgolol/Dev/Development/Eduboost-V2/app/core/token_revocation.py

Lines: 62-66
```python
    key = f"{_REVOKED_JTI_PREFIX}{jti}"
    try:
        await _redis_set_with_ttl(key, ttl_seconds, "1")
    except RedisError:
        logger.warning("Redis unavailable; token revocation skipped", exc_inf...
```

Lines: 73-77
```python
    key = f"{_REVOKED_JTI_PREFIX}{jti}"
    try:
        result = await get_redis().get(key)
    except RedisError:
        logger.warning("Redis unavailable; assuming token is not revoked", ex...
```

Lines: 94-98
```python
    ttl_seconds = int(timedelta(days=30).total_seconds())
    try:
        await _redis_set_with_ttl(key, ttl_seconds, "1")
    except RedisError:
        logger.warning("Redis unavailable; user token revocation skipped", ex...
```

### File: /home/nkgolol/Dev/Development/Eduboost-V2/app/core/refresh_tokens.py

Lines: 76-85
```python
    family_id = str(payload.get("family") or jti)

    if await is_refresh_family_revoked(family_id):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=...

    stored_hash = await cache_get(_refresh_key(jti))
    if stored_hash is None or not hmac.compare_digest(stored_hash, token_hash...
        await revoke_refresh_family(family_id)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
```

Lines: 87-91
```python
        )

    await cache_delete(_refresh_key(jti))
    await cache_delete(_family_key(family_id, jti))
    await cache_delete(_user_session_key(str(payload["sub"]), jti))
```

Lines: 114-118
```python
        return
    ttl = REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600
    await cache_set(_family_revoked_key(family_id), "1", ttl=ttl)
    await cache_delete_pattern(f"{_REFRESH_FAMILY_PREFIX}:{family_id}:*")
```

### File: /home/nkgolol/Dev/Development/Eduboost-V2/app/api_v2.py

Lines: 27-31
```python
from app.services.jwt_keyring import validate_jwt_keyring_environment

validate_jwt_keyring_environment()

configure_logging()
```

### File: /home/nkgolol/Dev/Development/Eduboost-V2/app/api_v2_routers/auth.py

Lines: 113-117
```python
):
    # code_911_950_auth_lifecycle_delegate
    return await auth_service.login(
            request=request,
            body=body,
```

### File: /home/nkgolol/Dev/Development/Eduboost-V2/app/services/jwt_keyring.py

Lines: 150-154
```python
        if not isinstance(parsed, list):
            raise JWTKeyringError("JWT_KEYRING JSON must be a list")
        keys = [_key_from_mapping(item) for item in parsed]
    else:
        keys = []
```

Lines: 176-180
```python
def current_jwt_key(keys: list[JWTKey] | None = None) -> JWTKey:
    keyring = keys or parse_jwt_keyring()
    for key in keyring:
        if key.status == "current":
            return key
```

Lines: 182-186
```python

def current_jwt_signing_key() -> str:
    return current_jwt_key().secret
```

Lines: 192-196
```python

def current_jwt_headers() -> dict[str, str]:
    return {"kid": current_jwt_key().kid}
```

Lines: 202-213
```python
        return True
    # Catch any "CHANGE_ME*" or "PLACEHOLDER*" sentinel defaults from .env
    return normalised.startswith("change_me") or normalised.startswith("place...


def validate_jwt_keyring_environment() -> None:
    """Fail closed when production would use a placeholder JWT secret."""
    keys = parse_jwt_keyring()
    placeholder_kids = [key.kid for key in keys if is_placeholder_secret(key....
    if is_production_environment() and placeholder_kids:
        raise JWTKeyringError(
            "Production environment cannot use placeholder JWT secrets. "
```

Lines: 224-235
```python
def decode_jwt_with_keyring(token: str, *, options: dict[str, Any] | None = N...
    validate_jwt_keyring_environment()
    headers = jwt.get_unverified_header(token)
    kid = headers.get("kid")
    keys = parse_jwt_keyring()
    ordered = sorted(keys, key=lambda key: 0 if key.kid == kid else 1)
    last_error: Exception | None = None
    for key in ordered:
        try:
            return jwt.decode(token, key.secret, algorithms=[key.algorithm], ...
        except Exception as exc:
            last_error = exc
```

### File: /home/nkgolol/Dev/Development/Eduboost-V2/app/core/token_config.py

Lines: 134-142
```python
    The raw token is sent to the client; only the hash is stored.
    """
    raw = secrets.token_urlsafe(64)
    hashed = _hash_token(raw)
    fid = family_id or str(uuid.uuid4())
    now = datetime.now(tz=timezone.utc)
    record = RefreshTokenRecord(
        family_id=fid,
        user_id="",            # caller fills in
```

Lines: 149-153
```python
def _hash_token(raw: str) -> str:
    """SHA-256 hash of a raw token for at-rest storage (§3.3 P0)."""
    return hashlib.sha256(raw.encode()).hexdigest()
```

Lines: 222-226
```python
    now = datetime.now(tz=timezone.utc)
    r = await get_redis()
    await r.set(REVOKE_ALL_EPOCH_KEY, now.isoformat())
    return now
```

Lines: 238-242
```python
    await revoke_jti(jti, ttl)
    # DB fallback — import lazily to honour import-boundary rules
    from app.repositories.revocation_repository import persist_revocation  # ...
    await persist_revocation(jti, expires_at)
```
