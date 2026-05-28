# EduBoost V2 Object-Level Authorization System (app/security/*)

The app/security/ module implements a centralized object-level authorization policy engine with role-based access control for learner-scoped resources. The system uses an Actor-based model with ownership scopes (self, guardian, educator, support, admin, system) and canonical permissions (read, write, delete, admin). FastAPI dependency adapters bridge HTTP headers and JWT claims to the policy engine, which routes integrate alongside POPIA consent enforcement for two-layer security. Key flows: core policy evaluation [1c], header-based actor construction [2b], JWT claim adaptation [3c], route enforcement [4d], and combined auth+consent gates [5e].

## Trace ID: 1
**Title:** Core Authorization Policy Evaluation

**Description:** The authorization engine's decision logic in object_authorization.py - evaluates role permissions and ownership scope to allow or deny access.

**Motivation:**
EduBoost needs a centralized, testable way to decide whether an actor can access a learner-scoped resource. The object_authorization module implements a policy engine that separates role-based permission checks from ownership scope evaluation, making authorization logic auditable and reusable across routes.

This matters because learner data access decisions must be consistent: a guardian can read and write their learners, a support user can read any learner but not write, and delete operations require elevated roles. The policy engine encodes these rules in one place rather than scattering them across route handlers.

**Details:**

**Entry Point and Permission Normalization**
can_access_learner() [1a] is the main decision function. It normalizes the requested permission and looks up which roles are permitted to perform that action via _permission_roles() [1b]. If the actor's roles do not intersect with permitted roles, the engine denies immediately.

**Ownership Scope Evaluation**
If the role check passes, _scope_for_learner() [1c] determines why the actor is authorized. It checks in priority order: admin role, system role, self-ownership [1d], guardian relationship [1e], educator relationship, and finally support role fallback. The scope that matches determines the access context.

**Permission-Level Validation**
After computing a scope, the engine validates that the scope is sufficient for the requested permission. Support scope is explicitly denied for write and delete operations [1f], and delete requires admin or system roles. This prevents elevated permissions from being granted through fallback scopes.

**Decision Return**
If all checks pass, the engine returns AuthorizationDecision.allow() with the scope that authorized access [1g]. If any check fails, it returns a denial with a reason. This structured decision format lets routes and tests introspect why access was granted or denied.

**Trace text diagram:**
```text
Core Authorization Policy Evaluation
└── can_access_learner() entry <-- 1a
    ├── normalize_permission() <-- object_authorization.py:160
    ├── _permission_roles() lookup <-- 1b
    │   └── check actor.roles intersection <-- object_authorization.py:214
    │       └── deny if no role match <-- object_authorization.py:215
    ├── _scope_for_learner() evaluation <-- 1c
    │   ├── check admin role <-- object_authorization.py:183
    │   ├── check system role <-- object_authorization.py:186
    │   ├── check self ownership <-- 1d
    │   ├── check guardian relationship <-- 1e
    │   ├── check educator relationship <-- object_authorization.py:195
    │   └── check support role fallback <-- object_authorization.py:198
    ├── validate scope for permission level
    │   ├── deny if scope is None <-- object_authorization.py:225
    │   ├── block support write/delete <-- 1f
    │   └── require admin/system for delete <-- object_authorization.py:240
    └── AuthorizationDecision.allow() <-- 1g
```

**Location ID: 1a**
- **Title:** Entry point for learner access checks
- **Description:** Main authorization function that evaluates if an Actor can access a learner with a given permission
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/security/object_authorization.py:204

**Location ID: 1b**
- **Title:** Determine which roles allow this permission
- **Description:** Maps permission (read/write/delete/admin) to the set of roles that can perform it
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/security/object_authorization.py:213

**Location ID: 1c**
- **Title:** Calculate ownership scope
- **Description:** Determines why the actor is authorized (admin, self, guardian, educator, support, system)
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/security/object_authorization.py:224

**Location ID: 1d**
- **Title:** Check self-ownership
- **Description:** Learner can access their own data via subject_id match or learner_ids membership
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/security/object_authorization.py:189

**Location ID: 1e**
- **Title:** Check guardian relationship
- **Description:** Guardian can access learners in their guardian_learner_ids set
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/security/object_authorization.py:192

**Location ID: 1f**
- **Title:** Support scope is read-only
- **Description:** Support role can read but cannot write or delete learner data
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/security/object_authorization.py:233

**Location ID: 1g**
- **Title:** Grant access with scope
- **Description:** Returns allowed decision with the ownership scope that authorized access
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/security/object_authorization.py:248

### AI Guide: Core Authorization Policy Evaluation

**Motivation:**
The policy engine exists to keep authorization logic centralized and auditable. Without it, each route would need to reimplement role checks, relationship lookups, and permission validation, which would create inconsistencies and make security changes difficult.

**Details:**

**Role-Permission Mapping**
_permission_roles() [1b] maps each permission to the roles that can perform it. This mapping is the first line of defense: if the actor's roles don't intersect with the permitted set, access is denied regardless of ownership.

**Scope Priority Order**
_scope_for_learner() [1c] checks scopes in priority order. Admin and system roles bypass relationship checks because they have platform-wide authority. Self, guardian, and educator checks then follow, with support as a read-only fallback. This ordering ensures that higher-privilege scopes are not accidentally shadowed by lower-privilege ones.

**Permission-Level Constraints**
Even if a scope is granted, the engine validates that the scope is sufficient for the requested permission. Support scope is explicitly blocked for write and delete [1f], and delete requires admin or system. This prevents privilege escalation through scope misconfiguration.

## Trace ID: 2
**Title:** Header-Based Actor Construction for FastAPI

**Description:** FastAPI dependency adapter in dependencies.py that builds an Actor from HTTP request headers for testing and header-based auth.

**Motivation:**
EduBoost needs a way to construct authorization actors for testing and for environments that use header-based authentication rather than JWT. The header-based adapter lets tests and integration tools inject actor identity via X-EduBoost-* headers without going through token validation.

This is useful for contract tests, manual API exploration, and environments where authentication is handled by an upstream gateway that injects trusted headers.

**Details:**

**FastAPI Dependency Entry Point**
get_authorization_actor() [2a] is a FastAPI dependency that extracts X-EduBoost-* headers from the request. It delegates to build_actor_from_headers() [2b] to construct the Actor object.

**Header Parsing**
build_actor_from_headers() splits comma-separated header values using _split_header_values() and parses roles using _parse_roles() [2c]. The role parser validates each role string against the Role enum, raising an HTTP exception if an invalid role is provided.

**Actor Construction**
The parsed values are passed to Actor.from_values() [2d], which calls the Actor constructor [2e]. The constructor converts role and relationship lists to frozensets for immutability, ensuring that Actor objects cannot be mutated after creation.

**Security Consideration**
Header-based auth should only be enabled in trusted environments or for testing. In production, JWT-based authentication via get_current_user is preferred because headers can be spoofed if the gateway is not properly secured.

**Trace text diagram:**
```text
Header-Based Authorization Flow
├── FastAPI Route Handler
│   └── actor: Actor = Depends(get_authorization_actor)
│       └── get_authorization_actor() <-- 2a
│           └── Extract X-EduBoost-* headers <-- dependencies.py:75
│               └── build_actor_from_headers() <-- 2b
│                   ├── _split_header_values() <-- dependencies.py:24
│                   ├── _parse_roles() <-- 2c
│                   │   └── Role(raw_role) validation <-- dependencies.py:34
│                   └── Actor.from_values() <-- 2d
│                       └── Actor.__init__() <-- 2e
│                           ├── frozenset(roles) <-- object_authorization.py:67
│                           ├── frozenset(learner_ids) <-- object_authorization.py:68
│                           ├── frozenset(guardian_learner_ids) <-- object_authorization.py:69
│                           └── frozenset(educator_learner_ids) <-- object_authorization.py:70
```

**Location ID: 2a**
- **Title:** FastAPI dependency for authorization actor
- **Description:** Extracts actor identity from X-EduBoost-* headers and constructs Actor object
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/security/dependencies.py:74

**Location ID: 2b**
- **Title:** Delegate to header builder
- **Description:** Calls build_actor_from_headers with extracted header values
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/security/dependencies.py:88

**Location ID: 2c**
- **Title:** Parse comma-separated roles
- **Description:** Converts role header string to tuple of Role enum values
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/security/dependencies.py:58

**Location ID: 2d**
- **Title:** Construct Actor with relationships
- **Description:** Creates Actor with subject_id, roles, and learner relationship sets
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/security/dependencies.py:65

**Location ID: 2e**
- **Title:** Actor factory method
- **Description:** Converts raw values to frozen Actor dataclass with frozensets for immutability
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/security/object_authorization.py:65

### AI Guide: Header-Based Actor Construction

**Motivation:**
The header-based adapter exists to support testing and integration scenarios where JWT validation is unnecessary or where an upstream gateway handles authentication. It provides a lightweight way to inject actor identity for contract tests and manual API calls.

**Details:**

**Header Extraction and Parsing**
get_authorization_actor() [2a] extracts headers and delegates to build_actor_from_headers() [2b]. The parser splits comma-separated values and validates roles against the Role enum [2c], ensuring that only valid roles are accepted.

**Immutable Actor Construction**
Actor.from_values() [2d] constructs an immutable Actor object using frozensets [2e]. This prevents accidental mutation of actor state after construction, which is important for security and predictability.

**Production Use Warning**
Header-based auth should not be used in production unless the application is behind a trusted gateway that strips untrusted headers. JWT-based authentication via get_current_user is the recommended production path because it includes cryptographic validation.

## Trace ID: 3
**Title:** JWT Claims to Authorization Actor Adapter

**Description:** Converts JWT payload (current_user dict) to Actor for routes using get_current_user dependency - production authentication path.

**Motivation:**
EduBoost uses JWT tokens for production authentication. The JWT payload contains role and relationship claims, but the authorization engine expects an Actor object. The adapter bridges this gap by converting JWT claims to the canonical Actor format.

This ensures that routes using get_current_user can seamlessly integrate with the authorization policy engine without duplicating claim-to-actor logic.

**Details:**

**JWT Claims Extraction**
Routes receive a current_user dict from get_current_user(). build_actor_from_current_user_claims() [3a] extracts the subject_id from the "sub" claim and maps the JWT role string to the canonical Role enum using _role_from_current_user() [3b].

**Role Mapping**
The role_map [3d] maps JWT role strings to Role enum values: "parent" → Role.GUARDIAN, "student" → Role.LEARNER, "teacher" → Role.EDUCATOR. This mapping allows JWT tokens to use user-friendly role names while the authorization engine uses canonical enums.

**Actor Construction**
The adapter extracts learner relationship IDs from the JWT payload and calls Actor.from_values() [3c] to construct the Actor. The resulting Actor object can be passed directly to can_access_learner() for policy evaluation.

**Policy Integration**
Once the Actor is constructed, routes can call can_access_learner(actor, learner_id) to evaluate authorization. This keeps the authorization logic in the policy engine while using JWT as the transport for identity and claims.

**Trace text diagram:**
```text
JWT Claims to Authorization Actor Flow
├── Route receives JWT token
│   └── get_current_user() dependency <-- security.py:93
│       └── decode_token() extracts claims <-- security.py:100
│           └── current_user dict payload <-- security.py:124
│
└── Authorization enforcement
    ├── build_actor_from_current_user_claims() <-- 3a
    │   ├── Extract subject_id from claims <-- dependencies.py:241
    │   ├── _role_from_current_user() <-- 3b
    │   │   └── role_map lookup <-- 3d
    │   │       ├── "parent" → Role.GUARDIAN <-- dependencies.py:164
    │   │       ├── "student" → Role.LEARNER <-- dependencies.py:166
    │   │       └── "teacher" → Role.EDUCATOR <-- dependencies.py:168
    │   └── Actor.from_values() <-- 3c
    │       ├── subject_id from "sub" <-- dependencies.py:251
    │       ├── roles tuple <-- dependencies.py:252
    │       ├── learner_ids from claims <-- dependencies.py:253
    │       ├── guardian_learner_ids from claims <-- dependencies.py:254
    │       └── educator_learner_ids from claims <-- dependencies.py:257
    │
    └── Actor object ready for policy checks
        └── can_access_learner(actor, learner_id) <-- object_authorization.py:204
```

**Location ID: 3a**
- **Title:** Build Actor from JWT claims
- **Description:** Adapts JWT payload structure to Actor for production routes using get_current_user
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/security/dependencies.py:239

**Location ID: 3b**
- **Title:** Map JWT role to authorization Role
- **Description:** Converts JWT role string (parent, student, teacher) to canonical Role enum
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/security/dependencies.py:248

**Location ID: 3c**
- **Title:** Extract learner relationships from claims
- **Description:** Pulls learner_ids, guardian_learner_ids, educator_learner_ids from JWT payload
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/security/dependencies.py:250

**Location ID: 3d**
- **Title:** Role mapping table
- **Description:** Maps parent→guardian, student→learner, teacher→educator for JWT compatibility
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/security/dependencies.py:172

### AI Guide: JWT Claims to Authorization Actor Adapter

**Motivation:**
The JWT adapter exists to bridge production authentication (JWT tokens) with the authorization policy engine. It converts JWT claims to the canonical Actor format so that authorization logic remains independent of the authentication mechanism.

**Details:**

**Claim Extraction**
build_actor_from_current_user_claims() [3a] extracts subject_id and role from the current_user dict. The role is mapped via _role_from_current_user() [3b] using a lookup table [3d] that translates user-friendly JWT role strings to canonical Role enums.

**Relationship Extraction**
The adapter extracts learner relationship IDs from the JWT payload [3c]. These IDs are passed to Actor.from_values() to construct the Actor with the correct ownership scopes.

**Policy Engine Integration**
Once the Actor is constructed, routes can call can_access_learner() directly. This separation allows the authorization engine to be tested independently of JWT validation and to be reused with other authentication mechanisms.

## Trace ID: 4
**Title:** Route Authorization Enforcement - Learner Profile Read

**Description:** Real-world usage in learners.py router showing how authorization is enforced before data access.

**Motivation:**
The authorization policy engine is only useful if routes actually use it. This trace shows the canonical pattern for enforcing authorization in a learner-data route: load the learner, build an Actor from JWT claims, check authorization, and raise HTTP 403 if denied.

This pattern ensures that every learner-data route has consistent authorization enforcement and that authorization failures return structured error responses.

**Details:**

**Route Entry Point**
The GET /learners/{learner_id} endpoint [4a] loads the learner from the database [4b] before authorization checks. This is necessary because the authorization helper needs the learner object to build the Actor with correct relationship context.

**Authorization Enforcement**
require_learner_read_for_current_user() [4c] is the authorization helper. It calls build_actor_from_current_user_for_learner() [4d] to construct an Actor from JWT claims and the loaded learner, then delegates to require_learner_read() [4e].

**Policy Evaluation**
require_learner_read() calls raise_for_learner_access() [4f], which invokes can_access_learner() to evaluate the policy. If the decision is deny, it raises an HTTPException with status 403 and a structured error detail including the reason.

**Response Return**
If authorization passes, the route returns the LearnerResponse. If authorization fails, the HTTPException propagates and FastAPI returns a 403 response. This pattern keeps authorization logic out of the route handler while ensuring consistent error handling.

**Trace text diagram:**
```text
Learner Profile GET Route Authorization Flow
└── GET /learners/{learner_id} endpoint <-- 4a
    ├── Load learner from database <-- 4b
    ├── Authorization enforcement
    │   ├── require_learner_read_for_current_user() <-- 4c
    │   │   ├── build_actor_from_current_user_for_learner() <-- dependencies.py:180
    │   │   │   ├── Extract JWT claims (sub, role) <-- 4d
    │   │   │   ├── Map role (parent→guardian, etc.) <-- dependencies.py:192
    │   │   │   └── Build Actor with relationships <-- dependencies.py:211
    │   │   └── require_learner_read() <-- 4e
    │   │       └── raise_for_learner_access() <-- 4f
    │   │           ├── can_access_learner() <-- dependencies.py:104
    │   │           │   ├── Check role permissions <-- object_authorization.py:213
    │   │           │   ├── Calculate ownership scope <-- object_authorization.py:224
    │   │           │   └── Return decision <-- object_authorization.py:248
    │   │           └── Raise HTTP 403 if denied <-- dependencies.py:108
    │   └── require_active_consent_for_current_user() <-- learners.py:51
    │       └── ConsentService.require_active_consent() <-- dependencies.py:295
    └── Return LearnerResponse <-- learners.py:52
```

**Location ID: 4a**
- **Title:** Learner profile GET endpoint
- **Description:** Public route for retrieving learner profile data
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/api_v2_routers/learners.py:40

**Location ID: 4b**
- **Title:** Load learner from database
- **Description:** Fetch learner record before authorization check
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/api_v2_routers/learners.py:47

**Location ID: 4c**
- **Title:** Enforce read authorization
- **Description:** Calls authorization helper that builds Actor from JWT and checks read permission
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/api_v2_routers/learners.py:50

**Location ID: 4d**
- **Title:** Build Actor from current_user and learner
- **Description:** Constructs Actor with role and learner relationships from JWT payload
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/security/dependencies.py:225

**Location ID: 4e**
- **Title:** Delegate to core policy check
- **Description:** Calls require_learner_read which invokes can_access_learner and raises on denial
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/security/dependencies.py:226

**Location ID: 4f**
- **Title:** Enforce or raise HTTP 403
- **Description:** Evaluates authorization decision and raises HTTPException if denied
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/security/dependencies.py:122

### AI Guide: Route Authorization Enforcement

**Motivation:**
This trace shows the canonical pattern for enforcing authorization in learner-data routes. It demonstrates how to load a learner, build an Actor from JWT claims, evaluate the policy, and raise structured errors on denial.

**Details:**

**Load Before Authorize**
The route loads the learner from the database [4b] before authorization checks. This is necessary because the authorization helper needs the learner object to determine ownership relationships.

**Actor Construction with Context**
build_actor_from_current_user_for_learner() [4d] constructs an Actor with relationship context derived from the loaded learner. This ensures that the Actor reflects the actual database state rather than stale JWT claims.

**Policy Evaluation and Error Handling**
require_learner_read() [4e] delegates to raise_for_learner_access() [4f], which calls can_access_learner() and raises an HTTPException with a structured error detail if authorization is denied. This pattern keeps error handling consistent across routes.

## Trace ID: 5
**Title:** Combined Authorization + Consent Gate

**Description:** Two-layer security check in diagnostics.py showing authorization followed by POPIA consent enforcement.

**Motivation:**
EduBoost processes children's educational data, so learner access requires both authorization (who is allowed to see the data) and POPIA consent (whether the guardian has granted permission). This trace shows how routes enforce both checks in sequence.

The two-layer approach ensures that even if an actor is authorized by role and ownership, they cannot access learner data without active parental consent. This is a critical compliance requirement.

**Details:**

**Route Entry Point**
The GET /diagnostics/items/{learner_id} endpoint [5a] loads the learner from the database [5b] before security checks. This provides the learner context needed for both authorization and consent evaluation.

**Layer 1: Authorization Check**
require_learner_read_for_current_user() [5c] builds an Actor from JWT claims and evaluates the authorization policy. If the actor lacks permission or ownership scope, it raises HTTP 403.

**Layer 2: POPIA Consent Check**
require_active_consent_for_current_user() [5d] calls ConsentService.require_active_consent() [5e]. The service evaluates the consent state via consent_decision() [5f] and derive_consent_state() [5g]. If consent is not active, it raises ConsentRequiredError.

**Sequential Enforcement**
The two checks run sequentially: authorization first, then consent. This order ensures that unauthorized actors are rejected before consent evaluation, which may involve database queries. Both checks must pass for the route to return data.

**Trace text diagram:**
```text
Diagnostic Items Route (Two-Layer Security)
├── GET /diagnostics/items/{learner_id} <-- 5a
│   ├── Load learner from database <-- 5b
│   ├── LAYER 1: Authorization Check
│   │   ├── require_learner_read_for_current_user() <-- 5c
│   │   │   ├── build_actor_from_current_user_claims() <-- dependencies.py:239
│   │   │   │   └── Extract role + learner_ids from JWT <-- dependencies.py:248
│   │   │   └── can_access_learner() <-- object_authorization.py:204
│   │   │       └── Check role + ownership scope <-- object_authorization.py:224
│   │   └── [raises HTTP 403 if denied] <-- dependencies.py:108
│   └── LAYER 2: POPIA Consent Check
│       ├── require_active_consent_for_current_user() <-- 5d
│       │   └── ConsentService.require_active_consent() <-- 5e
│       │       ├── consent_decision() <-- 5f
│       │       │   └── derive_consent_state() <-- consent_policy.py:58
│       │       │       └── Check granted/expired/withdrawn <-- consent_policy.py:100
│       │       └── raise ConsentRequiredError() <-- 5g
│       └── [raises ConsentRequiredError if not active] <-- service.py:102
└── Return diagnostic items (if both gates pass) <-- diagnostics.py:64
```

**Location ID: 5a**
- **Title:** Diagnostic items endpoint
- **Description:** Route that requires both authorization and active consent
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/api_v2_routers/diagnostics.py:44

**Location ID: 5b**
- **Title:** Load learner record
- **Description:** Fetch learner before security checks
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/api_v2_routers/diagnostics.py:51

**Location ID: 5c**
- **Title:** First gate: authorization check
- **Description:** Verify actor has permission to access this learner (role + ownership)
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/api_v2_routers/diagnostics.py:54

**Location ID: 5d**
- **Title:** Second gate: POPIA consent check
- **Description:** Verify guardian has granted active consent for learner data processing
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/api_v2_routers/diagnostics.py:55

**Location ID: 5e**
- **Title:** Delegate to consent service
- **Description:** Calls ConsentService to check consent state and raise if not active
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/security/dependencies.py:295

**Location ID: 5f**
- **Title:** Evaluate consent policy
- **Description:** Derives consent state from database record using consent policy rules
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/modules/consent/service.py:101

**Location ID: 5g**
- **Title:** Block if consent not active
- **Description:** Raises exception if consent is pending, denied, expired, or withdrawn
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/modules/consent/service.py:111

### AI Guide: Combined Authorization + Consent Gate

**Motivation:**
The two-layer security pattern exists to satisfy both access control (who can see the data) and compliance (whether consent has been granted). Authorization alone is insufficient for POPIA compliance; consent must also be verified.

**Details:**

**Authorization First**
The route checks authorization first [5c]. This rejects unauthorized actors before performing consent evaluation, which may involve database queries. The authorization check uses the standard Actor construction and policy evaluation pattern.

**Consent Second**
If authorization passes, the route checks POPIA consent [5d]. The consent service evaluates the consent state [5f] and raises ConsentRequiredError if consent is not active [5g]. This ensures that even authorized actors cannot access learner data without guardian consent.

**Sequential Enforcement**
The two checks run sequentially rather than in parallel. This order is intentional: authorization is a lightweight role/ownership check, while consent evaluation may require database queries. Rejecting unauthorized actors early avoids unnecessary consent lookups.

## Trace ID: 6
**Title:** Authorization Denial and HTTP 403 Response

**Description:** Error path showing how authorization failures are converted to structured HTTP 403 responses.

**Motivation:**
Authorization failures must return structured error responses so clients can understand why access was denied and handle errors appropriately. This trace shows the error path from policy denial to HTTP 403 response.

Structured error responses include the denial reason, learner_id, and requested permission, which helps clients debug access issues and provides audit evidence.

**Details:**

**Policy Evaluation**
raise_for_learner_access() [6a] calls can_access_learner() to evaluate the policy. The policy engine checks role permissions [6b] and ownership scope [6c], returning a denial decision if either check fails.

**Decision Handling**
The helper checks if decision.allowed is true [6d]. If false, it raises an HTTPException with status 403 [6e]. The exception detail includes a structured error payload with code, message, reason, learner_id, and permission [6f].

**Structured Error Payload**
The error payload includes:
- code: "object_forbidden" - machine-readable error code
- message: "not authorized" - human-readable message
- reason: decision.reason - why access was denied
- learner_id: the requested learner
- permission: the requested permission

This structure allows clients to programmatically handle authorization errors and provides audit evidence for compliance reviews.

**Trace text diagram:**
```text
Authorization Denial Flow (Trace 6)
├── Route handler calls enforcement
│   └── raise_for_learner_access() <-- 6a
│       ├── Evaluate policy decision
│       │   └── can_access_learner() <-- object_authorization.py:204
│       │       ├── Check role permissions
│       │       │   └── if not permitted roles <-- object_authorization.py:214
│       │       │       └── deny (role lacks) <-- 6b
│       │       └── Check ownership scope
│       │           └── if scope is None <-- object_authorization.py:225
│       │               └── deny (no ownership) <-- 6c
│       └── Handle decision result
│           └── if decision.allowed <-- 6d
│               └── [false branch]
│                   └── raise HTTPException <-- 6e
│                       └── detail={...} <-- 6f
│                           ├── code: "object_forbidden" <-- dependencies.py:111
│                           ├── message: "not authorized" <-- dependencies.py:112
│                           ├── reason: decision.reason <-- dependencies.py:113
│                           ├── learner_id <-- dependencies.py:114
│                           └── permission <-- dependencies.py:115
```

**Location ID: 6a**
- **Title:** Evaluate authorization decision
- **Description:** Calls core policy engine to get allow/deny decision with reason
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/security/dependencies.py:104

**Location ID: 6b**
- **Title:** Deny if role lacks permission
- **Description:** Returns denial when actor's roles don't include required permission level
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/security/object_authorization.py:215

**Location ID: 6c**
- **Title:** Deny if no ownership scope
- **Description:** Returns denial when actor has no relationship to the learner
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/security/object_authorization.py:226

**Location ID: 6d**
- **Title:** Check decision result
- **Description:** Branch on whether authorization was granted or denied
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/security/dependencies.py:105

**Location ID: 6e**
- **Title:** Raise HTTP 403 Forbidden
- **Description:** Converts authorization denial to FastAPI HTTPException with structured detail
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/security/dependencies.py:108

**Location ID: 6f**
- **Title:** Structured error response
- **Description:** Returns code, message, reason, learner_id, and permission in error detail
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/security/dependencies.py:110

### AI Guide: Authorization Denial and HTTP 403 Response

**Motivation:**
Structured error responses are critical for security and compliance. They provide clients with actionable information about why access was denied and create an audit trail for authorization decisions.

**Details:**

**Policy Denial Reasons**
The policy engine can deny for two reasons: role lacks permission [6b] or no ownership scope [6c]. The denial decision includes a reason field that explains which check failed.

**Structured Error Payload**
The HTTPException detail includes code, message, reason, learner_id, and permission [6f]. This structure allows clients to programmatically handle authorization errors and provides audit evidence for compliance reviews.

**Client Handling**
Clients should check the error code ("object_forbidden") and inspect the reason field to determine why access was denied. This enables better error handling and user feedback.

## Trace ID: 7
**Title:** Multi-Role Access Pattern - Guardian Write Access

**Description:** Shows how guardian role with assigned learners gets write access through guardian_learner_ids scope.

**Motivation:**
Guardians need write access to their assigned learners for tasks like generating study plans. This trace shows how the guardian role, combined with guardian_learner_ids in the JWT payload, grants write access to specific learners.

The pattern demonstrates how ownership scopes are derived from relationship claims in the JWT, allowing role-based access control to be context-aware.

**Details:**

**Route Entry Point**
The POST /study-plans/{learner_id} endpoint [7a] requires write access to the learner. It calls require_learner_write_for_current_user() to enforce authorization.

**Actor Construction**
build_actor_from_current_user_claims() [7b] extracts the guardian role and guardian_learner_ids from the JWT payload. Actor.from_values() constructs an Actor with these relationships.

**Permission Check**
require_learner_write() [7c] calls raise_for_learner_access(), which invokes can_access_learner(). The policy engine checks that the guardian role is in WRITE_ROLES [7f] and that the learner_id is in guardian_learner_ids [7d].

**Scope Grant**
If the learner_id matches, _scope_for_learner() returns OwnershipScope.GUARDIAN [7e], which allows read and write access. The policy engine then validates that the guardian scope is sufficient for the write permission.

**Trace text diagram:**
```text
Study Plan Generation Route (Guardian Write)
├── POST /study-plans/{learner_id} endpoint <-- study_plans.py:20
│   ├── require_learner_write_for_current_user() <-- 7a
│   │   ├── build_actor_from_current_user_claims() <-- 7b
│   │   │   ├── Extract JWT "sub" and "role" <-- dependencies.py:241
│   │   │   ├── Extract guardian_learner_ids from JWT <-- dependencies.py:254
│   │   │   └── Actor.from_values() creates Actor <-- dependencies.py:250
│   │   └── require_learner_write(actor, id) <-- 7c
│   │       └── raise_for_learner_access() <-- dependencies.py:131
│   │           └── can_access_learner() <-- dependencies.py:104
│   │               ├── Check WRITE_ROLES includes
│   │               │   Guardian <-- 7f
│   │               └── _scope_for_learner() <-- object_authorization.py:224
│   │                   ├── if learner_id in
│   │                   │   guardian_learner_ids <-- 7d
│   │                   └── return
│   │                       OwnershipScope.GUARDIAN <-- 7e
│   └── require_active_consent_for_current_user() <-- study_plans.py:30
└── Background job enqueued for generation <-- study_plans.py:56
```

**Location ID: 7a**
- **Title:** Enforce write permission
- **Description:** Study plan generation requires write access to learner
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/api_v2_routers/study_plans.py:29

**Location ID: 7b**
- **Title:** Build Actor from JWT
- **Description:** Extracts guardian role and guardian_learner_ids from JWT payload
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/security/dependencies.py:268

**Location ID: 7c**
- **Title:** Check write permission
- **Description:** Validates guardian can write to this specific learner_id
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/security/dependencies.py:269

**Location ID: 7d**
- **Title:** Guardian scope check
- **Description:** Matches learner_id against guardian's assigned learner set
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/security/object_authorization.py:192

**Location ID: 7e**
- **Title:** Grant guardian scope
- **Description:** Returns GUARDIAN ownership scope allowing read and write access
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/security/object_authorization.py:193

**Location ID: 7f**
- **Title:** Guardian in WRITE_ROLES
- **Description:** Guardian role is included in the set of roles permitted to write learner data
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/security/object_authorization.py:139

### AI Guide: Multi-Role Access Pattern - Guardian Write Access

**Motivation:**
This trace shows how ownership scopes are derived from relationship claims in the JWT. Guardians can write to their assigned learners because the guardian_learner_ids claim provides the ownership context needed for the guardian scope.

**Details:**

**JWT Relationship Claims**
The JWT payload includes guardian_learner_ids, which lists the learners the guardian is authorized to access. build_actor_from_current_user_claims() [7b] extracts this claim and passes it to Actor.from_values().

**Scope Derivation**
_scope_for_learner() checks if the learner_id is in guardian_learner_ids [7d]. If it matches, the engine returns OwnershipScope.GUARDIAN [7e], which allows read and write access.

**Permission Validation**
The policy engine validates that the guardian role is in WRITE_ROLES [7f] and that the guardian scope is sufficient for the write permission. This two-step check ensures both role and ownership are valid.

## Trace ID: 8
**Title:** Support Role Read-Only Access Pattern

**Description:** Demonstrates how support role gets read access to all learners but write/delete operations are blocked.

**Motivation:**
Support users need read access to all learners for troubleshooting and customer service, but they should not be able to modify or delete learner data. This trace shows how the support role grants read-only access across all learners.

The pattern demonstrates how the policy engine can grant broad access for a specific purpose (read-only support) while preventing privilege escalation to write or delete operations.

**Details:**

**Scope Fallback**
_scope_for_learner() checks admin, system, self, guardian, and educator scopes first. If none match, it checks for the support role [8a] and returns OwnershipScope.SUPPORT [8b]. This fallback gives support users access to any learner without requiring explicit relationship claims.

**Role Permission Check**
The policy engine checks that the support role is in READ_ROLES [8c]. This allows support users to read learner data.

**Permission-Level Constraint**
After granting the support scope, the policy engine validates that the requested permission is compatible with the scope. If the permission is write or delete and the scope is SUPPORT, the engine denies with a "read-only" reason [8d][8e].

**Route Integration**
Routes that call require_learner_write() will fail for support users because the policy engine denies write access to the support scope. This ensures that support users cannot perform write or delete operations even if they have read access.

**Trace text diagram:**
```text
Support Role Read-Only Access Pattern
├── Authorization Policy Engine
│   ├── _scope_for_learner() evaluation <-- object_authorization.py:182
│   │   ├── Check admin role (priority) <-- object_authorization.py:183
│   │   ├── Check system role (priority) <-- object_authorization.py:186
│   │   ├── Check self-ownership <-- object_authorization.py:189
│   │   ├── Check guardian relationship <-- object_authorization.py:192
│   │   ├── Check educator relationship <-- object_authorization.py:195
│   │   └── Check support role fallback <-- 8a
│   │       └── return OwnershipScope.SUPPORT <-- 8b
│   └── can_access_learner() decision logic <-- object_authorization.py:204
│       ├── Check role has permission <-- object_authorization.py:214
│       │   └── Support in READ_ROLES <-- 8c
│       ├── Get ownership scope (calls above) <-- object_authorization.py:224
│       └── Validate scope for permission level <-- object_authorization.py:232
│           └── if scope == SUPPORT & write <-- 8d
│               └── deny: "read-only" <-- 8e
└── Route Integration
    └── require_learner_write() called <-- dependencies.py:129
        └── raise HTTPException(403) <-- dependencies.py:108
```

**Location ID: 8a**
- **Title:** Support role fallback
- **Description:** Support role gets access even without specific learner relationship
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/security/object_authorization.py:198

**Location ID: 8b**
- **Title:** Grant support scope
- **Description:** Returns SUPPORT ownership scope for read-only access
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/security/object_authorization.py:199

**Location ID: 8c**
- **Title:** Support in READ_ROLES
- **Description:** Support role is included in roles that can read learner data
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/security/object_authorization.py:128

**Location ID: 8d**
- **Title:** Block support write access
- **Description:** Special check that denies write/delete/admin for support scope
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/security/object_authorization.py:233

**Location ID: 8e**
- **Title:** Deny with read-only reason
- **Description:** Returns denial explaining support role cannot perform write operations
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/security/object_authorization.py:237

### AI Guide: Support Role Read-Only Access Pattern

**Motivation:**
The support role exists to give customer service and operations teams read access to all learners for troubleshooting. The read-only constraint prevents accidental or malicious modification of learner data.

**Details:**

**Scope Fallback**
The support role is a fallback scope [8a] that grants access when no other ownership relationship matches. This allows support users to access any learner without requiring explicit relationship claims in the JWT.

**Read-Only Constraint**
The policy engine explicitly denies write and delete permissions for the support scope [8d][8e]. This ensures that support users cannot perform destructive operations even if they have broad read access.

**Route Integration**
Routes that require write or delete permissions will fail for support users because the policy engine denies these operations for the support scope. This pattern enforces the principle of least privilege: support users get the access they need (read) but not the access they don't need (write/delete).
