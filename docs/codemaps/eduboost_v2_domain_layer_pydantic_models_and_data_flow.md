# EduBoost V2 Domain Layer: Pydantic Models and Data Flow

Maps how domain models in app/domain/ flow through the EduBoost V2 architecture, from API transport schemas to business entities to persistence. Key entry points include API envelope construction [1b], consent state transitions [2c], content factory validation [3c], diagnostic item queries [4b], and role-based authorization [5b].

## Trace ID: 1
**Title:** API Envelope Response Construction

**Description:** Shows how the canonical V2 API envelope wraps responses using domain models from api_v2_models.py, flowing from router through schema validation to envelope helpers

**Motivation:**
EduBoost V2 implements a canonical API envelope pattern to provide consistent response structure across all endpoints. The HTTP POST /learners endpoint receives a LearnerCreate schema for request validation, ensuring type-safe input. The repository creates an ORM model (LearnerProfile entity) which is persisted to the database. Response construction uses model_validate() to convert the ORM model to a domain response schema (LearnerResponse), which extends OrmBase for ORM compatibility via from_attributes. The EnvelopedRoute wrapper invokes the envelope helper, calling ok(data) to wrap the typed response. The ApiSuccessEnvelope[T] generic type builds the envelope with data: LearnerResponse and meta: ApiMeta attached, including API version and request tracking. This pattern ensures consistent API contracts, type safety, and metadata attachment across all endpoints.

**Details:**
- **Execution Flow:** HTTP POST /learners endpoint → Request validation → LearnerCreate schema → Repository creates ORM model → LearnerProfile entity persisted → Response construction → model_validate() converts ORM → Domain Response Schema → LearnerResponse(OrmBase) definition → from_attributes for ORM compat → EnvelopedRoute wrapper → Envelope helper invoked → ok(data) called → ApiSuccessEnvelope[T] built → data: LearnerResponse → meta: ApiMeta attached → JSON response returned to client
- **Concurrency Safety:** Request validation is stateless. ORM model creation is per-request. model_validate() is thread-safe. Envelope construction is stateless. No distributed locks needed
- **Covered Objects:** API envelope pattern, Pydantic schemas, ORM compatibility, type safety, metadata attachment, response validation
- **Timeouts:** Request validation: ~1-5ms. ORM creation: ~10-50ms. model_validate(): ~1-5ms. Envelope construction: ~1-5ms. Total: ~13-65ms
- **Migration Path:** From ad-hoc responses to envelope pattern. Migration requires: 1) Define domain schemas, 2) Add envelope helpers, 3) Update response construction, 4) Add metadata attachment
- **Error Handling:** Validation errors return 422. ORM errors logged. Envelope failures logged. All errors logged with context. Sensitive data not logged
- **Security Considerations:** Validate all inputs. Use type-safe schemas. Filter sensitive data. Attach metadata for tracking. Use ORM compatibility. Validate responses

**Trace text diagram:**
```
API Request Flow: Domain Schema to Envelope
├── HTTP POST /learners endpoint <-- learners.py:24
│   ├── Request validation <-- 1a
│   │   └── LearnerCreate schema <-- schemas.py:56
│   ├── Repository creates ORM model <-- learners.py:31
│   │   └── LearnerProfile entity persisted
│   └── Response construction <-- 1b
│       └── model_validate() converts ORM <-- learners.py:37
├── Domain Response Schema <-- 1c
│   ├── LearnerResponse(OrmBase) definition <-- schemas.py:62
│   └── from_attributes for ORM compat <-- schemas.py:18
└── EnvelopedRoute wrapper <-- learners.py:20
    ├── Envelope helper invoked
    │   └── ok(data) called <-- 1d
    ├── ApiSuccessEnvelope[T] built <-- api_v2_models.py:89
    │   ├── data: LearnerResponse <-- api_v2_models.py:90
    │   └── meta: ApiMeta attached <-- 1e
    └── JSON response returned to client
```

**Location ID: 1a**
- **Title:** Request Schema Import
- **Description:** Router endpoint receives typed request using domain schema
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/api_v2_routers/learners.py:26

**Location ID: 1b**
- **Title:** Response Schema Construction
- **Description:** Converts ORM model to domain response schema for API contract
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/api_v2_routers/learners.py:37

**Location ID: 1c**
- **Title:** Domain Response Model
- **Description:** Pydantic model defining API response structure with ORM compatibility
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/domain/schemas.py:62

**Location ID: 1d**
- **Title:** Envelope Construction
- **Description:** Generic envelope builder wraps typed data with metadata
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/domain/api_v2_models.py:89

**Location ID: 1e**
- **Title:** Metadata Attachment
- **Description:** Attaches API version and request tracking to every response
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/domain/api_v2_models.py:91

### AI Guide: API Envelope Response Construction

**Overview:** The API envelope pattern provides consistent response structure across all endpoints. This trace shows how domain models flow through validation, ORM conversion, and envelope construction.

**Key Components:**

1. **Request Schema Import (1a):** Typed request validation. LearnerCreate schema. Input safety.

2. **Response Schema Construction (1b):** ORM to domain conversion. model_validate() call. Type safety.

3. **Domain Response Model (1c):** Pydantic schema definition. OrmBase extension. ORM compatibility.

4. **Envelope Construction (1d):** Generic envelope builder. ok() helper. Consistent structure.

5. **Metadata Attachment (1e):** ApiMeta attachment. API version. Request tracking.

**Best Practices:**
- Use typed schemas for validation
- Convert ORM to domain models
- Use envelope for consistency
- Attach metadata for tracking
- Filter sensitive data
- Use ORM compatibility
- Validate responses

**Common Issues:**
- Validation errors: Check schema definitions
- ORM conversion errors: Check from_attributes
- Envelope failures: Check generic types
- Metadata missing: Check attachment logic
- Type errors: Verify model compatibility

## Trace ID: 2
**Title:** POPIA Consent State Transition

**Description:** Traces consent lifecycle from service orchestration through domain entity state machine to repository persistence, demonstrating immutable domain pattern

**Motivation:**
EduBoost V2 implements an immutable domain pattern for POPIA consent management, ensuring data integrity and auditability. The HTTP request flows to the ConsentService.grant() method, which checks for existing consent and calls existing.grant(version) on the domain entity. The ConsentRecord domain model implements a state machine with initial state PENDING. The grant() method invokes _assert_transition() to validate the transition against ALLOWED_TRANSITIONS, ensuring only valid state changes occur. The method returns a new immutable instance via model_copy(update={...}), transitioning state to GRANTED, setting granted_at to now, and expires_at to +365 days. The repository persists the updated domain entity via ConsentRepository.update(), executing an UPDATE statement on the consent_records table. This immutable pattern prevents accidental mutations, ensures auditability, and provides clear state transition rules for compliance.

**Details:**
- **Execution Flow:** HTTP Request → Consent Service → ConsentService.grant() → Check for existing consent → existing.grant(version) call → await repo.update(updated) → Domain Entity State Machine → ConsentRecord domain model → Initial state: PENDING → grant() method invoked → _assert_transition() → Validates ALLOWED_TRANSITIONS → model_copy(update={...}) → state → GRANTED → granted_at → now → expires_at → +365 days → Returns new immutable instance → Persistence Layer → ConsentRepository.update() → UPDATE consent_records SET...
- **Concurrency Safety:** State machine validation is deterministic. Immutable instances prevent races. Repository updates use transactions. No distributed locks needed
- **Covered Objects:** Immutable domain pattern, state machine, POPIA compliance, consent lifecycle, auditability, repository persistence
- **Timeouts:** Service orchestration: ~10-50ms. State transition: ~1-5ms. Repository update: ~10-50ms. Total: ~20-105ms
- **Migration Path:** From mutable to immutable pattern. Migration requires: 1) Define state machine, 2) Implement immutable transitions, 3) Add validation, 4) Update repository
- **Error Handling:** Invalid transitions raise errors. Repository errors logged. All errors logged with context. Sensitive data not logged
- **Security Considerations:** Validate all transitions. Use immutable pattern. Audit state changes. Enforce POPIA compliance. Log consent actions

**Location ID: 2a**
- **Title:** Service Calls Domain Method
- **Description:** Consent service invokes domain entity's grant transition
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/consent_service.py:56

**Location ID: 2b**
- **Title:** Domain Entity Instantiation
- **Description:** Creates immutable ConsentRecord with initial PENDING state
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/domain/consent.py:59

**Location ID: 2c**
- **Title:** Immutable State Transition
- **Description:** Returns new ConsentRecord instance with GRANTED state and expiry
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/domain/consent.py:72

**Location ID: 2d**
- **Title:** State Machine Validation
- **Description:** Enforces allowed transitions defined in ALLOWED_TRANSITIONS dict
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/domain/consent.py:70

**Location ID: 2e**
- **Title:** Repository Persistence
- **Description:** Persists updated domain entity to PostgreSQL consent_records table
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/repositories/consent_repository.py:57

### AI Guide: POPIA Consent State Transition

**Overview:** The immutable domain pattern for consent management ensures data integrity and auditability. This trace shows state machine validation and persistence.

**Key Components:**

1. **Service Calls Domain Method (2a):** Service orchestration. Domain method invocation. Business logic.

2. **Domain Entity Instantiation (2b):** Immutable entity creation. Initial PENDING state. Domain model.

3. **Immutable State Transition (2c):** model_copy() for immutability. State transition. New instance.

4. **State Machine Validation (2d):** Transition validation. ALLOWED_TRANSITIONS. State rules.

5. **Repository Persistence (2e):** Repository update. Database persistence. Transaction safety.

**Best Practices:**
- Use immutable domain pattern
- Implement state machine validation
- Audit state changes
- Use model_copy() for transitions
- Validate transitions before execution
- Log consent actions
- Enforce POPIA compliance

**Common Issues:**
- Invalid transitions: Check state machine
- Mutation errors: Use immutable pattern
- Persistence failures: Check repository
- Audit missing: Add logging
- State errors: Validate transitions

## Trace ID: 3
**Title:** Content Factory Artifact Validation

**Description:** Shows content factory domain schemas flowing from admin API through validation service, using content_factory_schemas.py for type-safe artifact lifecycle

**Motivation:**
EduBoost V2 implements type-safe content artifact validation using domain schemas in content_factory_schemas.py. The admin API router at /admin/content-factory endpoint imports validation schemas for request validation. The ContentArtifactValidationRequest schema defines the validation payload with artifact_type field, artifact_json field, and sources: list[ETLSourceCitation] for provenance tracking. The ContentArtifactValidationResponse schema defines the response contract with passed: bool, checks: dict, and errors: list[str] for validation feedback. The ContentArtifactCreate schema provides comprehensive artifact creation with scope_id, content_layer, artifact_json payload, quality_score, safety_status, and sources with provenance. The ContentValidationService.validate() method processes the request and returns the response. This type-safe schema approach ensures validation consistency, provenance tracking, and clear API contracts for content artifact lifecycle management.

**Details:**
- **Execution Flow:** Admin API Router Layer → /admin/content-factory endpoint → Import validation schemas → Domain Schema Layer (app/domain/) → ContentArtifactValidationRequest → artifact_type field → artifact_json field → sources: list[ETLSourceCitation] → ContentArtifactValidationResponse → passed: bool → checks: dict → errors: list[str] → ContentArtifactCreate → scope_id, content_layer → artifact_json payload → quality_score, safety_status → sources with provenance → Service Layer → ContentValidationService → validate() → returns Response
- **Concurrency Safety:** Schema validation is stateless. Service processing is per-request. No shared state. No distributed locks needed
- **Covered Objects:** Content artifact validation, type-safe schemas, provenance tracking, API contracts, validation feedback
- **Timeouts:** Schema validation: ~1-5ms. Service processing: ~50-200ms. Total: ~50-205ms
- **Migration Path:** From ad-hoc validation to schemas. Migration requires: 1) Define validation schemas, 2) Add response schemas, 3) Implement service validation, 4) Update API endpoints
- **Error Handling:** Validation errors return 422. Service errors logged. All errors logged with context. Sensitive data not logged
- **Security Considerations:** Validate all inputs. Track provenance. Use type-safe schemas. Filter sensitive data. Validate artifact content

**Location ID: 3a**
- **Title:** Validation Request Schema Import
- **Description:** Router imports domain schema for artifact validation contract
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/api_v2_routers/content_factory.py:20

**Location ID: 3b**
- **Title:** Validation Schema Definition
- **Description:** Pydantic model defining artifact validation payload structure
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/domain/content_factory_schemas.py:76

**Location ID: 3c**
- **Title:** Validation Response Schema
- **Description:** Response contract with passed flag, checks dict, and errors list
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/domain/content_factory_schemas.py:103

**Location ID: 3d**
- **Title:** Artifact Creation Schema
- **Description:** Comprehensive schema for creating content artifacts with provenance
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/domain/content_factory_schemas.py:53

**Location ID: 3e**
- **Title:** Source Provenance Tracking
- **Description:** Embeds ETL source citations for content lineage and audit trail
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/domain/content_factory_schemas.py:73

### AI Guide: Content Factory Artifact Validation

**Overview:** Type-safe content artifact validation ensures consistency and provenance tracking. This trace shows schema validation and service processing.

**Key Components:**

1. **Validation Request Schema Import (3a):** Router imports schemas. Validation contract. Type safety.

2. **Validation Schema Definition (3b):** Pydantic model definition. Artifact validation. Payload structure.

3. **Validation Response Schema (3c):** Response contract. Validation feedback. Error details.

4. **Artifact Creation Schema (3d):** Comprehensive creation schema. Provenance tracking. Quality metrics.

5. **Source Provenance Tracking (3e):** ETL source citations. Content lineage. Audit trail.

**Best Practices:**
- Use type-safe schemas
- Track provenance
- Validate all inputs
- Provide clear feedback
- Use Pydantic for validation
- Filter sensitive data
- Audit content lifecycle

**Common Issues:**
- Validation errors: Check schema definitions
- Provenance missing: Check sources
- Feedback unclear: Check response schema
- Type errors: Verify schema compatibility
- Service errors: Check validation logic

## Trace ID: 4
**Title:** Diagnostic Item Repository Query with Domain Schema

**Description:** Traces how item_schema.py domain models are used by repositories to filter and return diagnostic items, bridging domain and ORM layers

**Motivation:**
EduBoost V2 bridges domain and ORM layers using shared enum definitions for type-safe repository queries. The repository layer's list_by_caps_ref() method accepts a ReviewStatus parameter from the domain schema, extracting the enum value for SQLAlchemy query compatibility. The method builds a SQLAlchemy query filtering by status_val. The domain schema layer defines the ReviewStatus enum with states DRAFT, AI_GENERATED, APPROVED, etc., shared across domain and ORM. The ItemCreate schema provides full item validation contract for creation and seed file I/O. The ORM model layer defines the DiagnosticItem table mapping with ReviewStatusEnum mirroring the domain enum for database persistence. This shared enum approach ensures type safety, prevents mismatches between domain and database layers, and provides clear state definitions across the application.

**Details:**
- **Execution Flow:** Repository Layer → list_by_caps_ref() method → Accept ReviewStatus param → Extract enum value → Build SQLAlchemy query → Filter by status_val → Return DiagnosticItem ORM models → Domain Schema Layer (app/domain) → ReviewStatus enum definition → DRAFT, AI_GENERATED, APPROVED... → ItemCreate schema → Full item validation contract → ORM Model Layer (app/models) → DiagnosticItem table mapping → ReviewStatusEnum mirror → Maps to database column
- **Concurrency Safety:** Enum extraction is deterministic. Query building is stateless. ORM queries use transactions. No distributed locks needed
- **Covered Objects:** Domain enums, ORM enums, repository queries, type safety, layer bridging, state definitions
- **Timeouts:** Enum extraction: ~1-5ms. Query building: ~1-5ms. Query execution: ~10-50ms. Total: ~12-60ms
- **Migration Path:** From ad-hoc enums to shared enums. Migration requires: 1) Define domain enums, 2. Mirror in ORM, 3) Update repository queries, 4) Ensure consistency
- **Error Handling:** Enum mismatches raise errors. Query errors logged. All errors logged with context. Sensitive data not logged
- **Security Considerations:** Use shared enums for consistency. Validate enum values. Prevent injection. Use type-safe queries. Filter sensitive data

**Location ID: 4a**
- **Title:** Domain Enum Parameter
- **Description:** Repository method accepts domain ReviewStatus enum for filtering
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/repositories/item_bank_repository.py:44

**Location ID: 4b**
- **Title:** Domain to ORM Conversion
- **Description:** Extracts enum value for SQLAlchemy query compatibility
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/repositories/item_bank_repository.py:58

**Location ID: 4c**
- **Title:** Domain Enum Definition
- **Description:** Canonical review status states shared across domain and ORM
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/domain/item_schema.py:33

**Location ID: 4d**
- **Title:** Item Creation Schema
- **Description:** Full diagnostic item schema for validation and seed file I/O
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/domain/item_schema.py:80

**Location ID: 4e**
- **Title:** ORM Enum Mirror
- **Description:** SQLAlchemy enum mirroring domain schema for database persistence
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/models/diagnostic_item.py:84

### AI Guide: Diagnostic Item Repository Query with Domain Schema

**Overview:** Shared enum definitions bridge domain and ORM layers for type-safe repository queries. This trace shows enum usage and query building.

**Key Components:**

1. **Domain Enum Parameter (4a):** Repository accepts domain enum. Type-safe filtering. Domain layer.

2. **Domain to ORM Conversion (4b):** Extracts enum value. SQLAlchemy compatibility. Layer bridging.

3. **Domain Enum Definition (4c):** Canonical enum definition. Shared across layers. State definitions.

4. **Item Creation Schema (4d):** Full validation contract. Seed file I/O. Type safety.

5. **ORM Enum Mirror (4e):** SQLAlchemy enum mirror. Database persistence. Consistency.

**Best Practices:**
- Use shared enums
- Define in domain layer
- Mirror in ORM layer
- Extract values for queries
- Ensure consistency
- Validate enum values
- Prevent mismatches

**Common Issues:**
- Enum mismatches: Check definitions
- Query errors: Verify extraction
- Type errors: Check compatibility
- ORM errors: Verify mirror
- Consistency issues: Sync enums

## Trace ID: 5
**Title:** Role-Based Authorization Policy Check

**Description:** Shows how roles.py domain enums drive authorization decisions in core/authorization.py, enforcing RBAC across the application

**Motivation:**
EduBoost V2 implements role-based access control (RBAC) using domain enums from roles.py to drive authorization decisions. The API request with JWT flows through get_current_user dependency, which returns a CurrentUser dataclass containing a role: Role field from the domain layer. The authorization policy check can_view_learner(actor, learner_id) uses pattern matching on actor.role with match actor.role, handling Role.ADMIN, Role.GUARDIAN (checking linked_learner_ids), and Role.TEACHER (checking assigned_learner_ids). The domain layer defines the Role enum with LEARNER, GUARDIAN, ADMIN, and four more roles. The role_has_permission(role, permission) function maps the Role enum to permission sets via ROLE_PERMISSIONS.get(role) for fine-grained access control. This domain-driven RBAC ensures consistent role definitions, centralized permission management, and type-safe authorization checks across the application.

**Details:**
- **Execution Flow:** API Request with JWT → get_current_user dependency → CurrentUser dataclass → role: Role field → Authorization Policy Check → can_view_learner(actor, learner_id) → match actor.role → case Role.ADMIN → case Role.GUARDIAN → check linked_learner_ids → case Role.TEACHER → check assigned_learner_ids → Domain Layer (app/domain/roles.py) → class Role(str, Enum) → LEARNER = "learner" → GUARDIAN = "guardian" → ADMIN = "admin" → [4 more roles...] → role_has_permission(role, permission) → ROLE_PERMISSIONS.get(role)
- **Concurrency Safety:** Role checks are deterministic. Permission lookups are stateless. No shared state. No distributed locks needed
- **Covered Objects:** RBAC, domain enums, authorization policies, permission matrices, pattern matching, type safety
- **Timeouts:** User resolution: ~10-50ms. Authorization check: ~1-5ms. Permission lookup: ~1-5ms. Total: ~12-60ms
- **Migration Path:** From ad-hoc checks to RBAC. Migration requires: 1) Define role enums, 2) Implement permission matrix, 3) Add authorization checks, 4) Update dependencies
- **Error Handling:** Authorization failures raise 403. Permission errors logged. All errors logged with context. Sensitive data not logged
- **Security Considerations:** Enforce least privilege. Use domain enums. Centralize permissions. Audit authorization. Use pattern matching. Validate roles

**Location ID: 5a**
- **Title:** CurrentUser Role Field
- **Description:** User dataclass contains Role enum from domain layer
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/authorization.py:39

**Location ID: 5b**
- **Title:** Role Pattern Matching
- **Description:** Authorization logic switches on domain Role enum values
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/authorization.py:73

**Location ID: 5c**
- **Title:** Admin Role Check
- **Description:** Uses Role.ADMIN from domain to grant full access
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/authorization.py:74

**Location ID: 5d**
- **Title:** Role Enum Definition
- **Description:** Canonical role definitions for all seven platform roles
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/domain/roles.py:19

**Location ID: 5e**
- **Title:** Permission Matrix Lookup
- **Description:** Maps Role enum to permission set for fine-grained access control
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/domain/roles.py:92

### AI Guide: Role-Based Authorization Policy Check

**Overview:** Domain enums drive RBAC authorization decisions across the application. This trace shows role definitions and permission checks.

**Key Components:**

1. **CurrentUser Role Field (5a):** User dataclass. Role enum from domain. Type safety.

2. **Role Pattern Matching (5b):** Authorization logic. Pattern matching on role. Role-based decisions.

3. **Admin Role Check (5c):** Admin role handling. Full access grant. Domain enum usage.

4. **Role Enum Definition (5d):** Canonical role definitions. Seven platform roles. Domain layer.

5. **Permission Matrix Lookup (5e):** Permission mapping. Fine-grained control. Centralized management.

**Best Practices:**
- Define roles in domain
- Use pattern matching
- Centralize permissions
- Enforce least privilege
- Audit authorization
- Use type-safe enums
- Validate roles

**Common Issues:**
- Authorization failures: Check role assignments
- Permission errors: Verify matrix
- Type errors: Check enum definitions
- Access denied: Verify role checks
- Consistency issues: Sync roles

## Trace ID: 6
**Title:** Content Coverage Report Generation

**Description:** Demonstrates content_coverage.py domain types flowing through coverage service to produce structured reports with status enums

**Motivation:**
EduBoost V2 implements content coverage reporting using domain types in content_coverage.py for structured, type-safe reports. The ContentCoverageService.get_scope_coverage() orchestrates report generation by getting scope from registry, looping through caps_refs, calling get_caps_ref_coverage() with _layer_counts() per layer, and summarizing caps_refs and layers. The service constructs a ScopeCoverageReport domain model with scope_id, grade fields, summary: ScopeCoverageSummary, layers: dict mapping, and per_caps_ref: list. The domain model defines CoverageLayerCounts with target: int, approved: int, status field, and coverage_ratio: float. The coverage_status() pure function computes RED/AMBER/GREEN status from counts: NOT_CONFIGURED if target <= 0, RED if approved <= 0, AMBER if approved < target, else GREEN. The CoverageLayerStatus enum defines the traffic light status for coverage quality signaling. This domain-driven approach ensures type safety, clear status semantics, and structured report generation.

**Details:**
- **Execution Flow:** ContentCoverageService → get_scope_coverage() orchestration → scope_registry.get_scope() → Loop: for each caps_ref → get_caps_ref_coverage() → _layer_counts() per layer → _summarize_caps_refs() → _summarize_layers() → ScopeCoverageReport() → scope_id, grade fields → summary: ScopeCoverageSummary → layers: dict mapping → per_caps_ref: list → Domain Model Construction → app/domain/content_coverage.py → ScopeCoverageReport → CoverageLayerCounts → target: int → approved: int → status field → coverage_ratio: float → coverage_status() → if target <= 0: NOT_CONFIGURED → if approved <= 0: RED → if approved < target: AMBER → else: GREEN → CoverageLayerStatus enum
- **Concurrency Safety:** Report generation is stateless. Status calculation is deterministic. No shared state. No distributed locks needed
- **Covered Objects:** Content coverage reporting, domain types, status enums, structured reports, traffic light signaling
- **Timeouts:** Scope lookup: ~10-50ms. Layer counts: ~10-50ms per layer. Summarization: ~10-50ms. Status calculation: ~1-5ms. Total: ~50-300ms
- **Migration Path:** From ad-hoc reports to domain types. Migration requires: 1) Define domain models, 2) Implement status calculation, 3) Build report service, 4) Update API endpoints
- **Error Handling:** Calculation errors logged. Report failures logged. All errors logged with context. Sensitive data not logged
- **Security Considerations:** Validate input data. Use type-safe models. Filter sensitive data. Audit report generation. Use pure functions

**Location ID: 6a**
- **Title:** Domain Report Construction
- **Description:** Service builds ScopeCoverageReport domain model from aggregated data
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_coverage_service.py:60

**Location ID: 6b**
- **Title:** Coverage Report Schema
- **Description:** Nested domain model containing summary and per-layer breakdowns
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/domain/content_coverage.py:77

**Location ID: 6c**
- **Title:** Layer Counts Model
- **Description:** Tracks target vs approved counts with computed status and ratio
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/domain/content_coverage.py:39

**Location ID: 6d**
- **Title:** Status Calculation Function
- **Description:** Pure function computing RED/AMBER/GREEN status from counts
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/domain/content_coverage.py:89

**Location ID: 6e**
- **Title:** Status Enum Definition
- **Description:** Traffic light status enum for coverage quality signaling
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/domain/content_coverage.py:32

### AI Guide: Content Coverage Report Generation

**Overview:** Domain types enable structured, type-safe content coverage reporting with status enums. This trace shows report construction and status calculation.

**Key Components:**

1. **Domain Report Construction (6a):** Service builds report. Aggregated data. Domain model.

2. **Coverage Report Schema (6b):** Nested domain model. Summary and breakdowns. Structured data.

3. **Layer Counts Model (6c):** Target vs approved. Computed status. Coverage ratio.

4. **Status Calculation Function (6d):** Pure function. RED/AMBER/GREEN logic. Deterministic.

5. **Status Enum Definition (6e):** Traffic light enum. Quality signaling. Clear semantics.

**Best Practices:**
- Use domain models
- Implement pure functions
- Define clear status enums
- Structure reports hierarchically
- Calculate status deterministically
- Validate input data
- Audit report generation

**Common Issues:**
- Calculation errors: Check logic
- Status wrong: Verify thresholds
- Report errors: Check aggregation
- Type errors: Verify models
- Performance: Optimize loops

## Trace ID: 7
**Title:** Data Subject Rights Request Processing

**Description:** Shows how data_subject_rights.py domain models support POPIA compliance workflows for export and erasure requests

**Motivation:**
EduBoost V2 implements POPIA data subject rights using domain models in data_subject_rights.py for compliance workflows. The DataExportRequest entity includes SLA deadline auto-calculation (30 days per POPIA) and is_overdue() business logic for identifying breached SLAs. The ErasureRequest entity includes a legal_hold flag and can_execute() guard method preventing erasure during legal holds. The service layer in data_subject_rights_service.py provides create_export_request() which instantiates DataExportRequest, and process_erasure_request() which checks can_execute(). The API layer in popia.py provides POST /export and POST /erasure endpoints. This domain-driven approach ensures POPIA compliance, automatic SLA tracking, legal hold enforcement, and clear business logic encapsulation for data subject rights.

**Details:**
- **Execution Flow:** Domain Models (app/domain/data_subject_rights.py) → DataExportRequest entity → SLA deadline auto-calculation → is_overdue() business logic → ErasureRequest entity → legal_hold flag → can_execute() guard method → Service Layer (app/services/) → data_subject_rights_service.py → create_export_request() → instantiates DataExportRequest → process_erasure_request() → checks can_execute() → API Layer (app/api_v2_routers/) → popia.py → POST /export endpoint → POST /erasure endpoint
- **Concurrency Safety:** SLA calculation is deterministic. Overdue check is stateless. Legal hold check is atomic. No distributed locks needed
- **Covered Objects:** POPIA compliance, data subject rights, SLA tracking, legal holds, business logic, domain models
- **Timeouts:** SLA calculation: ~1-5ms. Overdue check: ~1-5ms. Legal hold check: ~1-5ms. Total: ~3-15ms
- **Migration Path:** From ad-hoc to domain models. Migration requires: 1) Define domain models, 2) Implement business logic, 3) Add service layer, 4) Update API endpoints
- **Error Handling:** SLA breaches logged. Legal hold violations logged. All errors logged with context. Sensitive data not logged
- **Security Considerations:** Enforce POPIA compliance. Track SLAs. Enforce legal holds. Audit requests. Validate inputs. Filter sensitive data

**Location ID: 7a**
- **Title:** Export Request Model
- **Description:** Domain entity for POPIA data export requests with SLA tracking
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/domain/data_subject_rights.py:31

**Location ID: 7b**
- **Title:** SLA Deadline Calculation
- **Description:** Automatically sets 30-day deadline per POPIA compliance requirements
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/domain/data_subject_rights.py:38

**Location ID: 7c**
- **Title:** Overdue Check Method
- **Description:** Domain logic for identifying breached SLA deadlines
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/domain/data_subject_rights.py:45

**Location ID: 7d**
- **Title:** Erasure Request Model
- **Description:** Domain entity for right-to-be-forgotten with legal hold support
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/domain/data_subject_rights.py:56

**Location ID: 7e**
- **Title:** Execution Guard
- **Description:** Domain business rule preventing erasure during legal hold
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/domain/data_subject_rights.py:70

### AI Guide: Data Subject Rights Request Processing

**Overview:** Domain models support POPIA compliance workflows for export and erasure requests. This trace shows SLA tracking and legal hold enforcement.

**Key Components:**

1. **Export Request Model (7a):** Domain entity. SLA tracking. POPIA compliance.

2. **SLA Deadline Calculation (7b):** Auto-calculation. 30-day deadline. Compliance requirement.

3. **Overdue Check Method (7c):** Business logic. SLA breach detection. Domain method.

4. **Erasure Request Model (7d):** Right-to-be-forgotten. Legal hold support. Domain entity.

5. **Execution Guard (7e):** Business rule. Legal hold enforcement. Guard method.

**Best Practices:**
- Use domain models
- Auto-calculate SLAs
- Implement business logic
- Enforce legal holds
- Audit requests
- Validate inputs
- Filter sensitive data

**Common Issues:**
- SLA breaches: Check calculation
- Legal hold violations: Check guards
- Compliance errors: Verify requirements
- Business logic errors: Check methods
- Performance: Optimize checks

## Trace ID: 8
**Title:** API Error Envelope Construction

**Description:** Traces error handling flow using api_v2_models.py fail() helper to produce consistent error responses with field-level validation details

**Motivation:**
EduBoost V2 implements consistent error responses using the fail() helper in api_v2_models.py. The domain layer defines FieldError model for machine-readable validation detail, ApiError model with code, message, field_errors, and remediation field for user guidance. The fail() helper function returns ApiErrorEnvelope with error: ApiError(...), data: None, and meta: ApiMeta(...). The test layer demonstrates fail() usage with code="forbidden", message, remediation, and details. The router layer uses HTTPException handler to convert exceptions to envelope via fail(), returning JSONResponse with error payload. This pattern ensures consistent error responses, field-level validation details, user-friendly remediation guidance, and machine-readable error codes across all endpoints.

**Details:**
- **Execution Flow:** Domain Layer (app/domain/api_v2_models.py) → FieldError model definition → ApiError model definition → remediation field → fail() helper function → return ApiErrorEnvelope() → error: ApiError(...) → data: None → meta: ApiMeta(...) → Test Layer (tests/unit/test_api_v2_envelope.py) → test_fail_builds_error_envelope() → envelope = fail(...) → code="forbidden" → message="..." → remediation="..." → details={...} → Router Layer (usage in API routes) → HTTPException handler → fail() converts to envelope → JSONResponse with error payload
- **Concurrency Safety:** Error construction is stateless. Helper function is thread-safe. No shared state. No distributed locks needed
- **Covered Objects:** Error envelopes, field errors, remediation guidance, consistent responses, validation details
- **Timeouts:** Error construction: ~1-5ms. Envelope building: ~1-5ms. Total: ~2-10ms
- **Migration Path:** From ad-hoc errors to envelopes. Migration requires: 1) Define error models, 2) Implement fail() helper, 3) Update exception handlers, 4) Add remediation
- **Error Handling:** All errors converted to envelope. Validation errors included. Remediation provided. All errors logged with context. Sensitive data not logged
- **Security Considerations:** Don't expose sensitive data. Provide remediation guidance. Use error codes. Filter stack traces. Validate error messages

**Location ID: 8a**
- **Title:** Error Envelope Construction
- **Description:** Fail helper builds typed error envelope with ApiError payload
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/domain/api_v2_models.py:107

**Location ID: 8b**
- **Title:** Error Model Definition
- **Description:** Canonical error structure with code, message, and field errors
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/domain/api_v2_models.py:35

**Location ID: 8c**
- **Title:** Field Error Model
- **Description:** Machine-readable validation detail for individual request fields
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/domain/api_v2_models.py:27

**Location ID: 8d**
- **Title:** Error Envelope Usage
- **Description:** Test demonstrates fail() helper with remediation and details
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/tests/unit/test_api_v2_envelope.py:36

**Location ID: 8e**
- **Title:** Remediation Guidance
- **Description:** Optional user-facing guidance for resolving the error
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/domain/api_v2_models.py:41

### AI Guide: API Error Envelope Construction

**Overview:** The fail() helper produces consistent error responses with field-level validation details and remediation guidance. This trace shows error envelope construction.

**Key Components:**

1. **Error Envelope Construction (8a):** Fail helper builds envelope. Typed error payload. Consistent structure.

2. **Error Model Definition (8b):** Canonical error structure. Code, message, field errors. Standard format.

3. **Field Error Model (8c):** Validation detail. Machine-readable. Field-specific.

4. **Error Envelope Usage (8d):** Test demonstrates usage. Remediation and details. Example.

5. **Remediation Guidance (8e):** User-facing guidance. Error resolution. Helpful messages.

**Best Practices:**
- Use fail() helper
- Provide remediation
- Include field errors
- Use error codes
- Filter sensitive data
- Consistent structure
- Validate error messages

**Common Issues:**
- Inconsistent errors: Use fail() helper
- Missing remediation: Add guidance
- Field errors missing: Check validation
- Sensitive data exposed: Filter messages
- Code errors: Verify error codes
