# EduBoost V2 Core Infrastructure: Runtime Primitives & Cross-Cutting Concerns

Maps the foundational layer of EduBoost V2, covering application bootstrap, authentication/authorization, LLM orchestration, health monitoring, POPIA consent enforcement, and error handling. Key entry points: app startup [1b], JWT validation [3c], authorization checks [4c], LLM generation [5d], and consent gates [7c].

## Trace ID: 1
**Title:** Application Bootstrap & Initialization

**Description:** Core infrastructure setup when the FastAPI application starts, loading configuration, initializing logging, registering middleware and exception handlers.

**Motivation:**
EduBoost V2 requires a robust application bootstrap process to initialize all cross-cutting concerns before handling requests. The configuration layer uses Pydantic BaseSettings to load environment variables and .env file settings into a singleton settings object, providing type-safe configuration access. Structured logging with structlog is configured early to ensure all subsequent log entries include context (request_id, app_env, app_version) for distributed tracing. The database layer initializes SQLAlchemy async engine with connection pooling for efficient database access. FastAPI application setup registers global exception handlers for consistent error responses across all endpoints. Middleware stack registration adds RequestIDMiddleware for request tracing, TimingMiddleware for performance monitoring, and StructuredLoggingMiddleware for request lifecycle logging. This bootstrap process ensures all infrastructure components are properly initialized before the application accepts requests.

**Details:**
- **Execution Flow:** Configuration Layer → Settings singleton creation → Pydantic BaseSettings.from_env() → Logging Infrastructure → configure_logging() call → structlog.configure() → JSON renderer (production) → Console renderer (dev) → Contextvars merge processors → Database Layer → SQLAlchemy engine creation → Connection pool setup → Async session factory → FastAPI Application Setup → Exception handler registration → register_exception_handlers() → EduBoostError handler → HTTPException handler → ValidationError handler → Global Exception handler → Middleware stack registration → RequestIDMiddleware → TimingMiddleware → StructuredLoggingMiddleware
- **Concurrency Safety:** Settings singleton is read-only after initialization. Logging configuration is thread-safe. Database engine manages connection pooling. Exception handlers are registered once. Middleware stack is thread-safe. No distributed locks needed
- **Covered Objects:** Pydantic settings, structlog configuration, SQLAlchemy engine, async session factory, exception handlers, middleware stack, request tracing, performance monitoring
- **Timeouts:** Settings loading: ~10-50ms. Logging configuration: ~10-50ms. Engine creation: ~100-500ms. Handler registration: ~10-50ms. Middleware registration: ~10-50ms. Total bootstrap: ~150-700ms
- **Migration Path:** From ad-hoc initialization to structured bootstrap. Migration requires: 1) Create settings class, 2) Configure structlog, 3) Initialize database engine, 4) Register exception handlers, 5) Add middleware stack
- **Error Handling:** Configuration failures fail startup. Logging failures logged but don't block. Database connection failures fail startup. Handler registration failures fail startup. All errors logged with context
- **Security Considerations:** Settings should use environment variables. Secrets should not be hardcoded. Logging should not expose sensitive data. Database credentials should be secure. Middleware should not introduce vulnerabilities

**Trace text diagram:**
```
EduBoost V2 Application Bootstrap
├── Configuration Layer
│   └── Settings singleton creation <-- 1a
│       └── Pydantic BaseSettings.from_env() <-- config.py:58
├── Logging Infrastructure
│   ├── configure_logging() call <-- 1b
│   └── structlog.configure() <-- 1c
│       ├── JSON renderer (production) <-- logging.py:22
│       ├── Console renderer (dev) <-- logging.py:24
│       └── Contextvars merge processors <-- logging.py:27
├── Database Layer
│   └── SQLAlchemy engine creation <-- 1f
│       ├── Connection pool setup <-- database.py:35
│       └── Async session factory <-- database.py:41
├── FastAPI Application Setup
│   ├── Exception handler registration <-- 1d
│   │   └── register_exception_handlers() <-- 1e
│   │       ├── EduBoostError handler <-- exceptions.py:153
│   │       ├── HTTPException handler <-- exceptions.py:163
│   │       ├── ValidationError handler <-- exceptions.py:175
│   │       └── Global Exception handler <-- exceptions.py:215
│   └── Middleware stack registration
│       ├── RequestIDMiddleware <-- middleware.py:22
│       ├── TimingMiddleware <-- middleware.py:42
│       └── StructuredLoggingMiddleware <-- middleware.py:62
```

**Location ID: 1a**
- **Title:** Settings Singleton Creation
- **Description:** Pydantic settings loaded from environment variables and .env file
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/config.py:243

**Location ID: 1b**
- **Title:** Structured Logging Initialization
- **Description:** Sets up structlog with JSON output for production, console for dev
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/api_v2.py:31

**Location ID: 1c**
- **Title:** Structlog Configuration
- **Description:** Configures processors for contextvars, timestamps, and JSON rendering
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/logging.py:46

**Location ID: 1d**
- **Title:** Exception Handler Registration
- **Description:** Registers global exception handlers for consistent error responses
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/api_v2.py:17

**Location ID: 1e**
- **Title:** Exception Handler Setup
- **Description:** Attaches handlers for EduBoostError, HTTPException, ValidationError, etc.
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/exceptions.py:150

**Location ID: 1f**
- **Title:** Database Engine Creation
- **Description:** Creates SQLAlchemy async engine with connection pooling
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/database.py:39

### AI Guide: Application Bootstrap & Initialization

**Overview:** The application bootstrap process initializes all cross-cutting concerns before handling requests. This trace shows how configuration, logging, database, exception handling, and middleware are set up.

**Key Components:**

1. **Settings Singleton Creation (1a):** Pydantic settings from environment. Type-safe configuration. Singleton pattern.

2. **Structured Logging Initialization (1b):** Configures structlog early. JSON for production. Console for dev.

3. **Structlog Configuration (1c):** Processors for context. Timestamps and JSON. Distributed tracing.

4. **Exception Handler Registration (1d):** Global error handling. Consistent responses. Registered once.

5. **Exception Handler Setup (1e):** Handlers for specific errors. EduBoostError, HTTPException, ValidationError.

6. **Database Engine Creation (1f):** SQLAlchemy async engine. Connection pooling. Session factory.

**Best Practices:**
- Use Pydantic for configuration
- Configure logging early
- Initialize database before routes
- Register exception handlers globally
- Add middleware for cross-cutting concerns
- Use environment variables for secrets
- Keep bootstrap fast and reliable

**Common Issues:**
- Configuration errors: Check environment variables
- Logging not working: Verify structlog setup
- Database connection failures: Check connection string
- Exception handlers not firing: Check registration order
- Middleware not executing: Check registration order

## Trace ID: 2
**Title:** JWT Token Creation & Storage (Login Flow)

**Description:** Authentication flow from login request through password verification to JWT token generation and secure storage in Redis.

**Motivation:**
EduBoost V2 implements JWT-based authentication with secure token storage in Redis for session management. The login flow begins with password verification using bcrypt.checkpw() for constant-time comparison, preventing timing attacks. Access tokens are JWT-encoded with claims (sub, role, jti, exp) and signed using the current JWT signing key from the keyring, enabling key rotation without invalidating all tokens. Refresh tokens are JWT-encoded with a 7-day expiration and family_id for token rotation detection, allowing secure token refresh while preventing replay attacks. Tokens are stored in Redis as SHA-256 hashes to prevent token leakage if Redis is compromised. The refresh token is stored with a TTL matching its expiration, and user session tracking maps users to their refresh token families. This system provides secure, scalable authentication with token revocation support and key rotation capabilities.

**Details:**
- **Execution Flow:** User Login Request → Password Verification → bcrypt.checkpw() → constant-time comparison → Access Token Generation → JWT encoding with claims → build payload (sub, role, jti, exp) → jwt.encode() with keyring → signs with current_jwt_signing_key() → Refresh Token Generation → JWT encoding for refresh → build payload (family_id, 7-day exp) → jwt.encode() with keyring → signs with current_jwt_signing_key() → Token Persistence in Redis → Hash refresh token (SHA-256) → Store hashed token → cache_set(_refresh_key(jti), hashed) → Track user session → cache_set(_user_session_key(), family_id)
- **Concurrency Safety:** Password verification is constant-time. JWT encoding is stateless. Redis operations are atomic. Token storage uses hash for security. No distributed locks needed
- **Covered Objects:** bcrypt password verification, JWT encoding, keyring signing, token claims, refresh tokens, Redis storage, SHA-256 hashing, session tracking, TTL management
- **Timeouts:** Password verification: ~100-300ms. JWT encoding: ~10-50ms. Redis storage: ~10-50ms. Total login: ~120-400ms
- **Migration Path:** From session-based to JWT authentication. Migration requires: 1) Implement password hashing, 2) Add JWT encoding, 3) Set up keyring, 4) Add Redis storage, 5) Implement token refresh
- **Error Handling:** Password failures return 401. JWT encoding failures logged. Redis failures fail login. All errors logged with context. Sensitive data not logged
- **Security Considerations:** Use bcrypt for passwords. Constant-time comparison. Hash tokens in Redis. Use keyring for signing. Implement key rotation. Set appropriate TTLs. Never log tokens

**Trace text diagram:**
```
Login/Authentication Flow
├── User Login Request
│   └── Password Verification
│       └── bcrypt.checkpw() <-- 2a
│           └── constant-time comparison
├── Access Token Generation
│   └── JWT encoding with claims
│       ├── build payload (sub, role, jti, exp) <-- security.py:52
│       └── jwt.encode() with keyring <-- 2b
│           └── signs with current_jwt_signing_key()
├── Refresh Token Generation
│   └── JWT encoding for refresh
│       ├── build payload (family_id, 7-day exp) <-- security.py:66
│       └── jwt.encode() with keyring <-- 2c
│           └── signs with current_jwt_signing_key()
└── Token Persistence in Redis
    ├── Hash refresh token (SHA-256) <-- refresh_tokens.py:25
    ├── Store hashed token <-- 2d
    │   └── cache_set(_refresh_key(jti), hashed)
    └── Track user session <-- 2e
        └── cache_set(_user_session_key(), family_id)
```

**Location ID: 2a**
- **Title:** Password Verification
- **Description:** Constant-time bcrypt comparison of plaintext against stored hash
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/security.py:37

**Location ID: 2b**
- **Title:** Access Token Creation
- **Description:** Encodes JWT with user_id, role, jti, expiration using keyring
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/security.py:61

**Location ID: 2c**
- **Title:** Refresh Token Creation
- **Description:** Creates refresh token with 7-day expiration and family_id for rotation
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/security.py:75

**Location ID: 2d**
- **Title:** Refresh Token Storage
- **Description:** Stores hashed refresh token in Redis with TTL for rotation tracking
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/refresh_tokens.py:68

**Location ID: 2e**
- **Title:** User Session Tracking
- **Description:** Maps user to refresh token family for session management
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/refresh_tokens.py:70

### AI Guide: JWT Token Creation & Storage (Login Flow)

**Overview:** The login flow creates JWT tokens with secure storage in Redis. This trace shows password verification, token generation, and secure token storage.

**Key Components:**

1. **Password Verification (2a):** bcrypt constant-time comparison. Prevents timing attacks. Secure password check.

2. **Access Token Creation (2b):** JWT with user claims. Signed with keyring. Short expiration.

3. **Refresh Token Creation (2c):** JWT with family_id. 7-day expiration. Enables rotation.

4. **Refresh Token Storage (2d):** Hashed in Redis. TTL for expiration. Secure storage.

5. **User Session Tracking (2e):** Maps user to family. Session management. Rotation detection.

**Best Practices:**
- Use bcrypt for passwords
- Constant-time comparison
- Hash tokens in storage
- Use keyring for signing
- Implement key rotation
- Set appropriate TTLs
- Never log tokens

**Common Issues:**
- Password failures: Check bcrypt hashing
- Token encoding errors: Verify keyring
- Redis failures: Check connection
- Token leaks: Verify hashing
- Rotation issues: Check family_id

## Trace ID: 3
**Title:** JWT Validation & Revocation Check (Protected Route)

**Description:** Request authentication flow: token extraction, JWT decoding with keyring, revocation check in Redis, and user payload resolution.

**Motivation:**
EduBoost V2 implements comprehensive JWT validation with revocation checks for secure authentication. The FastAPI dependency get_current_user() extracts the Bearer token from the Authorization header and decodes it using decode_jwt_with_keyring(), which delegates to the JWT keyring service for multi-key validation. The keyring service verifies the signature using the current or previous signing key, enabling key rotation without invalidating valid tokens. Revocation checks include is_token_revoked(jti) to check if the specific token has been revoked (stored in Redis under revoked_jti:{jti}) and is_user_revoked(user_id) to check if all tokens for a user have been globally revoked (stored in Redis under revoked_user:{user_id}). On successful validation, the JWT payload with user_id, role, and custom claims is returned. On failure, an HTTPException 401 is raised. This system provides secure authentication with token revocation support and key rotation capabilities.

**Details:**
- **Execution Flow:** FastAPI Request Handler → get_current_user() dependency → Extract Bearer token from header → decode_token(credentials) → decode_jwt_with_keyring() → JWT keyring service → Verify signature with current/prev key → Revocation checks → is_token_revoked(jti) → Redis GET revoked_jti:{jti} → is_user_revoked(user_id) → Redis GET revoked_user:{user_id} → return validated payload → {sub, role, jti, exp, ...} → On failure: HTTPException 401
- **Concurrency Safety:** Token extraction is stateless. JWT decoding is stateless. Redis checks are atomic. Keyring validation is thread-safe. No distributed locks needed
- **Covered Objects:** JWT validation, keyring service, signature verification, revocation checks, Redis lookups, token extraction, payload resolution, error handling
- **Timeouts:** Token extraction: ~1-5ms. JWT decoding: ~10-50ms. Redis checks: ~10-50ms. Total validation: ~20-105ms
- **Migration Path:** From simple JWT to revocation checks. Migration requires: 1) Add keyring service, 2) Implement revocation checks, 3) Add Redis storage, 4) Update validation logic
- **Error Handling:** Invalid tokens return 401. Revoked tokens return 401. Redis failures logged. Keyring failures logged. All errors logged with context
- **Security Considerations:** Verify signature always. Check revocation on every request. Use Redis for fast lookups. Implement key rotation. Never log tokens. Use constant-time comparison

**Trace text diagram:**
```
JWT Validation & Revocation Check Flow
│
├── FastAPI Request Handler
│   └── get_current_user() dependency <-- 3a
│       ├── Extract Bearer token from header <-- security.py:94
│       └── decode_token(credentials) <-- 3a
│           │
│           ├── decode_jwt_with_keyring() <-- 3b
│           │   ├── JWT keyring service
│           │   └── Verify signature with current/prev key <-- security.py:80
│           │
│           └── Revocation checks
│               ├── is_token_revoked(jti) <-- 3c
│               │   └── Redis GET revoked_jti:{jti} <-- 3d
│               │
│               ├── is_user_revoked(user_id) <-- 3e
│               │   └── Redis GET revoked_user:{user_id} <-- token_revocation.py:107
│               │
│               └── return validated payload <-- 3f
│                   └── {sub, role, jti, exp, ...}
│
└── On failure: HTTPException 401 <-- security.py:82
```

**Location ID: 3a**
- **Title:** Token Decoding Entry Point
- **Description:** FastAPI dependency extracts and decodes Bearer token
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/security.py:100

**Location ID: 3b**
- **Title:** Keyring-Based JWT Decode
- **Description:** Delegates to JWT keyring service for multi-key validation
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/security.py:80

**Location ID: 3c**
- **Title:** JTI Revocation Check
- **Description:** Queries Redis blacklist to check if token has been revoked
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/security.py:108

**Location ID: 3d**
- **Title:** Redis Revocation Lookup
- **Description:** Checks if JTI exists in revoked_jti: prefix keys
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/token_revocation.py:75

**Location ID: 3e**
- **Title:** User-Level Revocation Check
- **Description:** Checks if all tokens for user have been globally revoked
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/security.py:117

**Location ID: 3f**
- **Title:** Return Validated Claims
- **Description:** Returns JWT payload with user_id, role, and custom claims
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/security.py:124

### AI Guide: JWT Validation & Revocation Check (Protected Route)

**Overview:** JWT validation with revocation checks ensures secure authentication. This trace shows token extraction, decoding, and revocation verification.

**Key Components:**

1. **Token Decoding Entry Point (3a):** FastAPI dependency. Extracts Bearer token. Entry point for validation.

2. **Keyring-Based JWT Decode (3b):** Delegates to keyring service. Multi-key validation. Enables rotation.

3. **JTI Revocation Check (3c):** Checks token revocation. Redis lookup. Per-token revocation.

4. **Redis Revocation Lookup (3d):** Fast Redis check. revoked_jti prefix. Atomic operation.

5. **User-Level Revocation Check (3e):** Checks user revocation. Global token invalidation. Mass revocation.

6. **Return Validated Claims (3f):** Returns user payload. Contains role and claims. Used by routes.

**Best Practices:**
- Always verify signature
- Check revocation on every request
- Use Redis for fast lookups
- Implement key rotation
- Support per-token revocation
- Support user-level revocation
- Log validation failures

**Common Issues:**
- Invalid tokens: Check signature
- Revocation not working: Check Redis
- Key rotation issues: Verify keyring
- Performance: Cache Redis client
- Token leaks: Never log tokens

## Trace ID: 4
**Title:** Authorization Policy Enforcement (RBAC)

**Description:** Object-level authorization check flow: current user resolution, policy evaluation, and audit logging for privileged access.

**Motivation:**
EduBoost V2 implements role-based access control (RBAC) with object-level authorization checks and audit logging for POPIA compliance. The authorization assertion dependency helper enforces learner access policy before route execution, ensuring only authorized users can access learner data. The policy evaluation entry point determines whether the actor role (ADMIN, GUARDIAN, LEARNER) permits access to the learner resource based on ownership relationships. Privileged access audit logging emits structured log entries with event, actor_id, role, resource_id, and jti for compliance requirements. The structured audit event includes all relevant context for security auditing. When policy checks fail, an HTTP 403 is raised. This system provides fine-grained access control with comprehensive audit trails for regulatory compliance.

**Details:**
- **Execution Flow:** Authorization Assertion → Dependency helper enforces learner access policy before route executes → Policy Evaluation Entry → Evaluates whether actor role permits access to learner resource → Privileged Access Audit → Logs admin access to learner data for POPIA compliance → Structured Audit Event → Emits structured log with event, actor_id, role, resource_id, jti → Authorization Failure → Raises HTTP 403 when policy check fails
- **Concurrency Safety:** Policy evaluation is stateless. Audit logging is thread-safe. Role checks are deterministic. No distributed locks needed. Database queries use transactions
- **Covered Objects:** RBAC policy evaluation, role-based access, object-level authorization, audit logging, POPIA compliance, structured logging, error handling
- **Timeouts:** Policy evaluation: ~10-50ms. Audit logging: ~1-5ms. Database queries: ~10-50ms. Total check: ~20-105ms
- **Migration Path:** From simple role checks to RBAC. Migration requires: 1) Define roles, 2) Implement policy evaluation, 3) Add audit logging, 4) Update dependencies
- **Error Handling:** Policy failures raise 403. Audit failures logged. Database errors logged. All errors logged with context. Sensitive data not logged
- **Security Considerations:** Enforce least privilege. Audit all privileged access. Use structured logging. Log all authorization decisions. Implement role hierarchy. Check object ownership

**Location ID: 4a**
- **Title:** Authorization Assertion
- **Description:** Dependency helper enforces learner access policy before route executes
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/dependencies.py:105

**Location ID: 4b**
- **Title:** Policy Evaluation Entry
- **Description:** Evaluates whether actor role permits access to learner resource
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/authorization.py:294

**Location ID: 4c**
- **Title:** Privileged Access Audit
- **Description:** Logs admin access to learner data for POPIA compliance
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/authorization.py:75

**Location ID: 4d**
- **Title:** Structured Audit Event
- **Description:** Emits structured log with event, actor_id, role, resource_id, jti
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/authorization.py:55

**Location ID: 4e**
- **Title:** Authorization Failure
- **Description:** Raises HTTP 403 when policy check fails
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/authorization.py:268

### AI Guide: Authorization Policy Enforcement (RBAC)

**Overview:** RBAC with object-level authorization ensures users can only access resources they're authorized for. This trace shows policy evaluation and audit logging.

**Key Components:**

1. **Authorization Assertion (4a):** Dependency helper. Enforces policy before route. Pre-execution check.

2. **Policy Evaluation Entry (4b):** Evaluates role permissions. Object-level checks. Ownership verification.

3. **Privileged Access Audit (4c):** Logs admin access. POPIA compliance. Security audit trail.

4. **Structured Audit Event (4d):** Structured log entry. Event context. Actor and resource details.

5. **Authorization Failure (4e):** Raises HTTP 403. Access denied. Clear error message.

**Best Practices:**
- Enforce least privilege
- Audit privileged access
- Use structured logging
- Log all decisions
- Implement role hierarchy
- Check object ownership
- Fail securely

**Common Issues:**
- Access denied: Check role assignments
- Audit missing: Verify logging
- Policy errors: Check evaluation logic
- Performance: Cache role checks
- Compliance: Review audit logs

## Trace ID: 5
**Title:** LLM Lesson Generation Pipeline

**Description:** AI content generation flow: quota enforcement, semantic cache lookup, LLM provider call, judiciary validation, and cache storage.

**Motivation:**
EduBoost V2 implements an AI lesson generation pipeline with quota enforcement, semantic caching, and content validation. The pipeline begins with cache key generation using SHA-256 hash of lesson parameters for semantic caching, enabling reuse of previously generated lessons. A semantic cache lookup checks Redis for cached lessons with the same parameters, reducing API costs and improving response time. AI quota enforcement atomically increments daily request counters and checks against limits (20 for free tier), preventing abuse. The LLM provider call uses Google/Groq/Anthropic with automatic fallback and retry for reliability. Judiciary validation validates LLM output against Pydantic schema and content policy, scanning for blocked patterns (violence, explicit content, etc.). Validated lessons are cached in Redis with 7-day TTL. This system provides cost-effective, reliable AI content generation with safety controls.

**Details:**
- **Execution Flow:** Cache Key Generation → Creates SHA-256 hash of lesson parameters for semantic caching → Semantic Cache Lookup → Checks Redis for previously generated lesson with same parameters → AI Quota Enforcement → Atomically increments daily request counter and checks limit → LLM Provider Call → Calls Google/Groq/Anthropic with automatic fallback and retry → Judiciary Validation → Validates LLM output against Pydantic schema and content policy → Content Policy Check → Scans for blocked patterns (violence, explicit content, etc.) → Cache Validated Lesson → Stores validated lesson in Redis with 7-day TTL
- **Concurrency Safety:** Cache key generation is deterministic. Redis operations are atomic. Quota enforcement uses atomic counters. LLM calls are rate-limited. No distributed locks needed
- **Covered Objects:** Semantic caching, quota enforcement, LLM provider abstraction, content validation, judiciary policy, Redis storage, fallback mechanisms
- **Timeouts:** Cache lookup: ~10-50ms. Quota check: ~10-50ms. LLM call: ~1-5s. Validation: ~10-50ms. Cache storage: ~10-50ms. Total: ~1-5.5s
- **Migration Path:** From direct LLM calls to pipeline. Migration requires: 1) Add semantic caching, 2) Implement quota enforcement, 3) Add provider abstraction, 4) Implement judiciary validation
- **Error Handling:** Quota exceeded returns 429. LLM failures trigger fallback. Validation failures logged. Cache failures logged. All errors logged with context
- **Security Considerations:** Enforce quota limits. Validate all outputs. Scan for harmful content. Use fallback providers. Cache securely. Monitor API costs

**Location ID: 5a**
- **Title:** Cache Key Generation
- **Description:** Creates SHA-256 hash of lesson parameters for semantic caching
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/llm_gateway.py:214

**Location ID: 5b**
- **Title:** Semantic Cache Lookup
- **Description:** Checks Redis for previously generated lesson with same parameters
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/llm_gateway.py:215

**Location ID: 5c**
- **Title:** AI Quota Enforcement
- **Description:** Atomically increments daily request counter and checks limit
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/llm_gateway.py:221

**Location ID: 5d**
- **Title:** LLM Provider Call
- **Description:** Calls Google/Groq/Anthropic with automatic fallback and retry
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/llm_gateway.py:252

**Location ID: 5e**
- **Title:** Judiciary Validation
- **Description:** Validates LLM output against Pydantic schema and content policy
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/llm_gateway.py:268

**Location ID: 5f**
- **Title:** Content Policy Check
- **Description:** Scans for blocked patterns (violence, explicit content, etc.)
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/judiciary.py:45

**Location ID: 5g**
- **Title:** Cache Validated Lesson
- **Description:** Stores validated lesson in Redis with 7-day TTL
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/llm_gateway.py:295

### AI Guide: LLM Lesson Generation Pipeline

**Overview:** The AI lesson generation pipeline provides cost-effective, reliable content generation with safety controls. This trace shows caching, quota enforcement, and validation.

**Key Components:**

1. **Cache Key Generation (5a):** SHA-256 hash of parameters. Semantic caching. Deterministic keys.

2. **Semantic Cache Lookup (5a):** Redis cache check. Reduces API costs. Improves response time.

3. **AI Quota Enforcement (5c):** Atomic counter increment. Daily limit check. Prevents abuse.

4. **LLM Provider Call (5d):** Provider abstraction. Fallback and retry. Reliability.

5. **Judiciary Validation (5e):** Pydantic schema validation. Content policy check. Safety.

6. **Content Policy Check (5f):** Scans for blocked patterns. Harmful content detection. Policy enforcement.

7. **Cache Validated Lesson (5g):** Stores in Redis. 7-day TTL. Reuse validated content.

**Best Practices:**
- Use semantic caching
- Enforce quota limits
- Implement fallback
- Validate all outputs
- Scan for harmful content
- Monitor API costs
- Use atomic operations

**Common Issues:**
- Cache misses: Check key generation
- Quota exceeded: Check limits
- LLM failures: Check fallback
- Validation errors: Check schema
- Policy violations: Check content filters
- Cost overruns: Monitor usage

## Trace ID: 6
**Title:** Deep Health Check Execution

**Description:** Readiness probe flow: checks critical dependencies (Postgres, Redis, migrations, audit) and optional components (LLM, judiciary) with metrics recording.

**Motivation:**
EduBoost V2 implements a comprehensive deep health check system for readiness probes and monitoring. The /ready endpoint handler coordinates gather_deep_health() to check all system components. Critical checks include check_postgres() which executes a simple SELECT 1 query to verify database connection and updates pool metrics, check_redis() which sends a PING command to verify Redis availability, check_migrations() which queries the alembic_version table to verify migrations are applied, and check_audit_repository() which verifies the audit_events table is accessible for POPIA compliance. Optional checks include check_llm_provider() and check_judiciary() for non-critical components. The overall status is determined as "ok", "degraded", or "error" based on critical check results. Prometheus metrics are recorded via _record_readiness_metrics() which updates readiness_component_status gauges for monitoring. This system provides comprehensive health monitoring for deployment orchestration and alerting.

**Details:**
- **Execution Flow:** /ready endpoint handler → gather_deep_health() → Critical Checks → check_postgres() → AsyncSessionLocal() session → SELECT 1 query → update pool metrics → check_redis() → redis.ping() → check_migrations() → SELECT from alembic_version → check_audit_repository() → SELECT 1 FROM audit_events → Optional Checks → check_llm_provider() → check_judiciary() → Determine overall status → "ok" | "degraded" | "error" → _record_readiness_metrics() → readiness_component_status.set() → Prometheus /metrics scrape → exposes readiness gauges
- **Concurrency Safety:** Health checks are independent. Database sessions are isolated. Redis operations are atomic. Metrics recording is thread-safe. No distributed locks needed
- **Covered Objects:** Health checks, readiness probes, database connectivity, Redis connectivity, migration status, audit repository, LLM provider, judiciary, Prometheus metrics
- **Timeouts:** Postgres check: ~10-50ms. Redis check: ~10-50ms. Migration check: ~10-50ms. Audit check: ~10-50ms. Optional checks: ~50-200ms. Total: ~50-400ms
- **Migration Path:** From simple health to deep checks. Migration requires: 1) Add critical checks, 2) Add optional checks, 3. Implement status determination, 4) Add metrics recording
- **Error Handling:** Check failures logged. Status reflects failures. Metrics updated regardless. All errors logged with context. Sensitive data not logged
- **Security Considerations:** Health checks should be authenticated. Limit check frequency. Use appropriate timeouts. Don't expose sensitive data. Monitor check failures

**Trace text diagram:**
```
Deep Health Check System
├── /ready endpoint handler
│   └── gather_deep_health() <-- 6a
│       ├── Critical Checks
│       │   ├── check_postgres() <-- health.py:18
│       │   │   ├── AsyncSessionLocal() session <-- health.py:20
│       │   │   ├── SELECT 1 query <-- 6b
│       │   │   └── update pool metrics <-- health.py:25
│       │   ├── check_redis() <-- health.py:36
│       │   │   └── redis.ping() <-- 6c
│       │   ├── check_migrations() <-- health.py:114
│       │   │   └── SELECT from alembic_version <-- 6d
│       │   └── check_audit_repository() <-- health.py:147
│       │       └── SELECT 1 FROM audit_events <-- 6e
│       ├── Optional Checks
│       │   ├── check_llm_provider() <-- health.py:52
│       │   └── check_judiciary() <-- health.py:161
│       ├── Determine overall status <-- health.py:206
│       │   └── "ok" | "degraded" | "error" <-- health.py:209
│       └── _record_readiness_metrics() <-- 6f
│           └── readiness_component_status.set() <-- health.py:181
└── Prometheus /metrics scrape
    └── exposes readiness gauges
```

**Location ID: 6a**
- **Title:** Health Check Orchestration
- **Description:** Coordinates all health checks and determines overall system status
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/health.py:190

**Location ID: 6b**
- **Title:** Postgres Connectivity Check
- **Description:** Executes simple query to verify database connection
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/health.py:21

**Location ID: 6c**
- **Title:** Redis Connectivity Check
- **Description:** Sends PING command to verify Redis availability
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/health.py:39

**Location ID: 6d**
- **Title:** Migration Status Check
- **Description:** Queries alembic_version table to verify migrations applied
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/health.py:127

**Location ID: 6e**
- **Title:** Audit Repository Check
- **Description:** Verifies audit_events table is accessible for POPIA compliance
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/health.py:155

**Location ID: 6f**
- **Title:** Prometheus Metrics Recording
- **Description:** Updates readiness_component_status gauge for monitoring
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/health.py:218

### AI Guide: Deep Health Check Execution

**Overview:** Deep health checks provide comprehensive system monitoring for readiness probes. This trace shows critical and optional health checks with metrics recording.

**Key Components:**

1. **Health Check Orchestration (6a):** Coordinates all checks. Determines overall status. Orchestrates execution.

2. **Postgres Connectivity Check (6b):** SELECT 1 query. Verifies connection. Updates pool metrics.

3. **Redis Connectivity Check (6c):** PING command. Verifies availability. Updates metrics.

4. **Migration Status Check (6d):** Queries alembic_version. Verifies migrations. Compliance check.

5. **Audit Repository Check (6e):** Queries audit_events. POPIA compliance. Accessibility check.

6. **Prometheus Metrics Recording (6f):** Updates gauges. Monitoring integration. Status tracking.

**Best Practices:**
- Check critical dependencies
- Add optional checks
- Use appropriate timeouts
- Record metrics
- Determine overall status
- Monitor check failures
- Limit check frequency

**Common Issues:**
- Database failures: Check connection
- Redis failures: Check connectivity
- Migration issues: Check alembic
- Audit failures: Check table access
- Metrics not updating: Check Prometheus

## Trace ID: 7
**Title:** POPIA Consent Gate Enforcement

**Description:** Consent enforcement flow: learner_id extraction, consent record lookup, policy evaluation, and access blocking for expired/missing consent.

**Motivation:**
EduBoost V2 implements POPIA (Protection of Personal Information Act) consent enforcement to ensure parental consent is obtained before accessing learner data. The consent gate invocation is a FastAPI dependency that enforces consent before learner data access, ensuring consistent enforcement across all routes. The consent record lookup queries the database for an active parental consent record. The consent policy evaluation determines the consent state (granted, expired, withdrawn, renewal_required) based on the record and current time. The expiration check compares the consent expiration timestamp against the current time. Metrics recording increments a Prometheus counter for consent gate blocks to monitor enforcement. Access denial raises an HTTP 403 when active consent is missing. This system ensures compliance with POPIA requirements for processing personal information of minors.

**Details:**
- **Execution Flow:** Consent Gate Invocation → FastAPI dependency enforces consent before learner data access → Consent Record Lookup → Queries database for active parental consent record → Consent Policy Evaluation → Determines consent state (granted/expired/withdrawn/renewal_required) → Expiration Check → Compares consent expiration timestamp against current time → Metrics Recording → Increments Prometheus counter for consent gate blocks → Access Denial → Raises HTTP 403 when active consent is missing
- **Concurrency Safety:** Consent lookup is stateless. Policy evaluation is deterministic. Metrics recording is thread-safe. Database queries use transactions. No distributed locks needed
- **Covered Objects:** POPIA compliance, consent enforcement, policy evaluation, expiration checks, metrics recording, access control, error handling
- **Timeouts:** Consent lookup: ~10-50ms. Policy evaluation: ~1-5ms. Expiration check: ~1-5ms. Metrics recording: ~1-5ms. Total: ~13-65ms
- **Migration Path:** From manual checks to consent gates. Migration requires: 1) Define consent policy, 2) Implement consent lookup, 3) Add dependency enforcement, 4) Add metrics recording
- **Error Handling:** Missing consent raises 403. Database errors logged. Policy errors logged. All errors logged with context. Sensitive data not logged
- **Security Considerations:** Enforce consent before access. Log all consent checks. Monitor consent blocks. Use appropriate error messages. Comply with POPIA. Audit consent decisions

**Location ID: 7a**
- **Title:** Consent Gate Invocation
- **Description:** FastAPI dependency enforces consent before learner data access
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/dependencies.py:106

**Location ID: 7b**
- **Title:** Consent Record Lookup
- **Description:** Queries database for active parental consent record
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/dependencies.py:80

**Location ID: 7c**
- **Title:** Consent Policy Evaluation
- **Description:** Determines consent state (granted/expired/withdrawn/renewal_required)
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/consent_policy.py:58

**Location ID: 7d**
- **Title:** Expiration Check
- **Description:** Compares consent expiration timestamp against current time
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/consent_policy.py:104

**Location ID: 7e**
- **Title:** Metrics Recording
- **Description:** Increments Prometheus counter for consent gate blocks
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/dependencies.py:83

**Location ID: 7f**
- **Title:** Access Denial
- **Description:** Raises HTTP 403 when active consent is missing
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/dependencies.py:84

### AI Guide: POPIA Consent Gate Enforcement

**Overview:** POPIA consent enforcement ensures parental consent before accessing learner data. This trace shows consent lookup, policy evaluation, and access blocking.

**Key Components:**

1. **Consent Gate Invocation (7a):** FastAPI dependency. Enforces before access. Consistent enforcement.

2. **Consent Record Lookup (7b):** Database query. Active consent record. Learner-specific.

3. **Consent Policy Evaluation (7c):** Determines consent state. Policy logic. State machine.

4. **Expiration Check (7d):** Timestamp comparison. Current time check. Expiration detection.

5. **Metrics Recording (7e):** Prometheus counter. Block tracking. Monitoring.

6. **Access Denial (7f):** HTTP 403 response. Clear error message. Access blocked.

**Best Practices:**
- Enforce consent before access
- Log all consent checks
- Monitor consent blocks
- Use appropriate error messages
- Comply with POPIA
- Audit consent decisions
- Keep policy simple

**Common Issues:**
- Access denied: Check consent status
- Consent not found: Check database
- Expiration errors: Check timestamps
- Metrics not recording: Check Prometheus
- Policy errors: Check evaluation logic

## Trace ID: 8
**Title:** Exception to Standardized API Response

**Description:** Error handling flow: exception raised in route, caught by global handler, wrapped in ApiEnvelope format with field errors and request_id.

**Motivation:**
EduBoost V2 implements standardized error handling to ensure consistent API responses across all endpoints. The domain error handler catches EduBoostError subclasses (NotFoundError, ConsentRequiredError, etc.) and converts them to standardized responses. The validation error handler transforms Pydantic validation errors into field-level error messages, extracting field path, message, and error code. Field error construction extracts relevant information from Pydantic errors for client consumption. The error envelope creation wraps errors in ApiEnvelope format with code, message, field_errors, and remediation information. The JSON response return returns standardized error responses with appropriate HTTP status codes. This system provides consistent error responses with actionable information for clients, improving developer experience and debugging.

**Details:**
- **Execution Flow:** Exception raised in route → caught by global handler → Domain Error Handler → Catches EduBoostError subclasses (NotFoundError, ConsentRequiredError, etc.) → Validation Error Handler → Transforms Pydantic validation errors into field-level error messages → Field Error Construction → Extracts field path, message, and error code from Pydantic error → Error Envelope Creation → Wraps error in ApiEnvelope with code, message, field_errors, remediation → JSON Response Return → Returns standardized error response with appropriate HTTP status code
- **Concurrency Safety:** Exception handling is synchronous. Error construction is stateless. Response generation is thread-safe. No distributed locks needed
- **Covered Objects:** Exception handling, error responses, Pydantic validation, field errors, ApiEnvelope, HTTP status codes, error codes, remediation
- **Timeouts:** Exception handling: ~1-5ms. Error construction: ~1-5ms. Response generation: ~1-5ms. Total: ~3-15ms
- **Migration Path:** From ad-hoc errors to standardized. Migration requires: 1) Define error classes, 2) Implement handlers, 3. Create envelope format, 4) Update error responses
- **Error Handling:** All exceptions caught. Errors logged with context. Sensitive data filtered. Status codes appropriate. Remediation provided
- **Security Considerations:** Don't expose sensitive data. Use appropriate status codes. Log errors with context. Provide remediation. Filter stack traces. Validate error messages

**Location ID: 8a**
- **Title:** Domain Error Handler
- **Description:** Catches EduBoostError subclasses (NotFoundError, ConsentRequiredError, etc.)
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/exceptions.py:154

**Location ID: 8b**
- **Title:** Validation Error Handler
- **Description:** Transforms Pydantic validation errors into field-level error messages
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/exceptions.py:176

**Location ID: 8c**
- **Title:** Field Error Construction
- **Description:** Extracts field path, message, and error code from Pydantic error
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/exceptions.py:113

**Location ID: 8d**
- **Title:** Error Envelope Creation
- **Description:** Wraps error in ApiEnvelope with code, message, field_errors, remediation
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/exceptions.py:136

**Location ID: 8e**
- **Title:** JSON Response Return
- **Description:** Returns standardized error response with appropriate HTTP status code
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/exceptions.py:134

### AI Guide: Exception to Standardized API Response

**Overview:** Standardized error handling ensures consistent API responses across all endpoints. This trace shows exception catching, error construction, and response generation.

**Key Components:**

1. **Domain Error Handler (8a):** Catches EduBoostError subclasses. Domain-specific errors. Consistent handling.

2. **Validation Error Handler (8b):** Transforms Pydantic errors. Field-level messages. Validation feedback.

3. **Field Error Construction (8c):** Extracts field information. Path and message. Error codes.

4. **Error Envelope Creation (8d):** Wraps in ApiEnvelope. Standardized format. Remediation info.

5. **JSON Response Return (8e):** Returns HTTP response. Appropriate status code. JSON format.

**Best Practices:**
- Use consistent error format
- Provide field-level errors
- Include error codes
- Add remediation info
- Use appropriate status codes
- Log errors with context
- Don't expose sensitive data

**Common Issues:**
- Errors not caught: Check handler registration
- Format inconsistent: Check envelope creation
- Status codes wrong: Check error mapping
- Sensitive data exposed: Filter error messages
- Remediation missing: Add helpful messages

## Trace ID: 9
**Title:** Request Lifecycle Middleware Chain

**Description:** Middleware execution flow: request_id injection, timing measurement, structured logging, and Prometheus metrics recording.

**Motivation:**
EduBoost V2 implements a middleware chain for request lifecycle management, observability, and performance monitoring. Request ID generation creates or extracts a correlation ID from the X-Request-ID header for distributed tracing across services. Context variables binding attaches request_id, app_env, and app_version to all log entries via structlog contextvars. Timing start records a high-precision timestamp before request processing for latency measurement. Request counter increment increments a Prometheus counter with method, endpoint, and status labels for request volume tracking. Latency histogram recording records request duration in a Prometheus histogram for percentile tracking (p50, p95, p99). Structured request log emits a JSON log with request_id, method, path, status, duration_ms, and client_ip for request lifecycle tracing. This middleware chain provides comprehensive observability for debugging, monitoring, and performance analysis.

**Details:**
- **Execution Flow:** Request ID Generation → Creates or extracts correlation ID for request tracing → Context Variables Binding → Attaches request_id, app_env, app_version to all log entries → Timing Start → Records high-precision timestamp before request processing → Request Counter Increment → Increments Prometheus counter with method, endpoint, status labels → Latency Histogram Recording → Records request duration in Prometheus histogram for percentile tracking → Structured Request Log → Emits JSON log with request_id, method, path, status, duration_ms, client_ip
- **Concurrency Safety:** Request ID generation is thread-safe. Context variables are thread-local. Timing is per-request. Metrics recording is thread-safe. No distributed locks needed
- **Covered Objects:** Request tracing, context variables, timing measurement, Prometheus metrics, structured logging, performance monitoring, request lifecycle
- **Timeouts:** Request ID generation: ~1-5ms. Context binding: ~1-5ms. Timing: ~1-5ms. Metrics recording: ~1-5ms. Logging: ~1-5ms. Total: ~5-25ms
- **Migration Path:** From no middleware to full chain. Migration requires: 1) Add request ID middleware, 2) Add timing middleware, 3) Add logging middleware, 4) Add metrics recording
- **Error Handling:** Middleware failures logged. Request ID preserved. Metrics recorded regardless. All errors logged with context. Sensitive data not logged
- **Security Considerations:** Don't log sensitive data. Use request IDs for tracing. Monitor performance. Set appropriate timeouts. Filter headers. Protect metrics endpoint

**Location ID: 9a**
- **Title:** Request ID Generation
- **Description:** Creates or extracts correlation ID for request tracing
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/middleware.py:26

**Location ID: 9b**
- **Title:** Context Variables Binding
- **Description:** Attaches request_id, app_env, app_version to all log entries
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/middleware.py:28

**Location ID: 9c**
- **Title:** Timing Start
- **Description:** Records high-precision timestamp before request processing
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/middleware.py:46

**Location ID: 9d**
- **Title:** Request Counter Increment
- **Description:** Increments Prometheus counter with method, endpoint, status labels
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/middleware.py:55

**Location ID: 9e**
- **Title:** Latency Histogram Recording
- **Description:** Records request duration in Prometheus histogram for percentile tracking
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/middleware.py:56

**Location ID: 9f**
- **Title:** Structured Request Log
- **Description:** Emits JSON log with request_id, method, path, status, duration_ms, client_ip
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/middleware.py:71

### AI Guide: Request Lifecycle Middleware Chain

**Overview:** The middleware chain provides request lifecycle management, observability, and performance monitoring. This trace shows request ID injection, timing, and metrics recording.

**Key Components:**

1. **Request ID Generation (9a):** Creates or extracts ID. Distributed tracing. Correlation across services.

2. **Context Variables Binding (9b):** Attaches to logs. request_id, app_env, app_version. Structured context.

3. **Timing Start (9c):** High-precision timestamp. Latency measurement. Performance tracking.

4. **Request Counter Increment (9d):** Prometheus counter. Volume tracking. Method and status labels.

5. **Latency Histogram Recording (9e):** Prometheus histogram. Percentile tracking. p50, p95, p99.

6. **Structured Request Log (9f):** JSON log entry. Request lifecycle. Debugging support.

**Best Practices:**
- Use request IDs for tracing
- Bind context to logs
- Measure latency accurately
- Record comprehensive metrics
- Use structured logging
- Monitor performance
- Filter sensitive data

**Common Issues:**
- Request ID missing: Check header extraction
- Context not bound: Check contextvars
- Timing inaccurate: Check precision
- Metrics not recording: Check Prometheus
- Logs not structured: Check structlog
- Performance degradation: Check middleware overhead

## Trace ID: 10
**Title:** AI Quota Enforcement (Rate Limiting)

**Description:** Daily AI request quota flow: Redis counter increment, limit comparison, and HTTP 429 response with retry-after header.

**Motivation:**
EduBoost V2 implements AI quota enforcement to control API costs and prevent abuse. The quota check entry validates that a user hasn't exceeded their daily AI request limit. Atomic counter increment uses Redis pipeline for atomic INCR + EXPIRE operations, ensuring accurate quota tracking even under concurrent requests. The Redis pipeline creation ensures the increment and expiration happen atomically, preventing race conditions. Limit comparison checks if usage exceeds FREE_DAILY_REQUEST_QUOTA (20 for free tier) against the counter value. When quota is exceeded, an HTTP 429 exception is raised with a Retry-After header set to seconds until tomorrow, providing clear guidance to clients. This system provides cost control and abuse prevention while providing clear feedback to users.

**Details:**
- **Execution Flow:** Quota Check Entry → Validates user hasn't exceeded daily AI request limit → Atomic Counter Increment → Increments Redis counter with 24-hour TTL for daily quota → Redis Pipeline Creation → Creates pipeline for atomic INCR + EXPIRE operations → Limit Comparison → Checks if usage exceeds FREE_DAILY_REQUEST_QUOTA (20 for free tier) → Quota Exceeded Exception → Raises HTTP 429 with Retry-After header set to seconds until tomorrow
- **Concurrency Safety:** Counter increment is atomic. Redis pipeline ensures atomicity. Limit comparison is deterministic. No distributed locks needed. Race conditions prevented
- **Covered Objects:** Quota enforcement, rate limiting, Redis atomic operations, HTTP 429 responses, retry-after headers, cost control, abuse prevention
- **Timeouts:** Quota check: ~10-50ms. Redis operations: ~10-50ms. Total: ~20-100ms
- **Migration Path:** From no limits to quota enforcement. Migration requires: 1) Implement counter increment, 2) Add limit comparison, 3) Add 429 response, 4) Set retry-after header
- **Error Handling:** Quota exceeded returns 429. Redis failures logged. All errors logged with context. Sensitive data not logged
- **Security Considerations:** Enforce quota limits. Use atomic operations. Provide clear feedback. Monitor quota usage. Set appropriate limits. Prevent abuse

**Location ID: 10a**
- **Title:** Quota Check Entry
- **Description:** Validates user hasn't exceeded daily AI request limit
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/rate_limiter.py:37

**Location ID: 10b**
- **Title:** Atomic Counter Increment
- **Description:** Increments Redis counter with 24-hour TTL for daily quota
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/rate_limiter.py:45

**Location ID: 10c**
- **Title:** Redis Pipeline Creation
- **Description:** Creates pipeline for atomic INCR + EXPIRE operations
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/redis.py:51

**Location ID: 10d**
- **Title:** Limit Comparison
- **Description:** Checks if usage exceeds FREE_DAILY_REQUEST_QUOTA (20 for free tier)
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/rate_limiter.py:47

**Location ID: 10e**
- **Title:** Quota Exceeded Exception
- **Description:** Raises HTTP 429 with Retry-After header set to seconds until tomorrow
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/rate_limiter.py:48

### AI Guide: AI Quota Enforcement (Rate Limiting)

**Overview:** AI quota enforcement controls API costs and prevents abuse through daily request limits. This trace shows atomic counter increment, limit comparison, and 429 responses.

**Key Components:**

1. **Quota Check Entry (10a):** Validates quota limit. User-specific check. Daily enforcement.

2. **Atomic Counter Increment (10b):** Redis counter increment. 24-hour TTL. Atomic operation.

3. **Redis Pipeline Creation (10c):** Atomic INCR + EXPIRE. Pipeline execution. Race condition prevention.

4. **Limit Comparison (10d):** Checks against quota. FREE_DAILY_REQUEST_QUOTA. Limit enforcement.

5. **Quota Exceeded Exception (10e):** HTTP 429 response. Retry-After header. Clear feedback.

**Best Practices:**
- Use atomic operations
- Set appropriate TTLs
- Provide clear feedback
- Monitor quota usage
- Set reasonable limits
- Use Redis pipelines
- Prevent race conditions

**Common Issues:**
- Quota not enforced: Check logic
- Race conditions: Use pipelines
- TTL not set: Check expiration
- 429 not returned: Check exception
- Retry-after missing: Check header
- Counter drift: Check atomicity
