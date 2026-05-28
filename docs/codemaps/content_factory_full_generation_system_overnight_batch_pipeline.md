# Content Factory Full Generation System: Overnight Batch Pipeline

End-to-end overnight batch generation pipeline that orchestrates content creation from planning through review submission. The system starts with gap analysis [1b], creates generation tasks [2d], executes them via providers [3c], validates artifacts [5b], verifies staging readiness [6c], seeds to staging [7c], and produces comprehensive reports [8b]. Human review gates prevent automatic approval [5e].

## Trace ID: 1
**Title:** Overnight Run Orchestration: Entry Point to Task Planning

**Description:** Main orchestration flow in run_full_generation.py that acquires locks, creates runs, and invokes the planner to identify missing content

**Motivation:**
EduBoost V2 implements an overnight batch generation pipeline to automate content creation at scale without disrupting daytime operations. The system uses distributed locks to prevent concurrent runs, ensuring only one generation process runs at a time. This approach allows for efficient resource utilization during off-peak hours while maintaining data integrity. The orchestration flow coordinates multiple phases: lock acquisition, run tracking, gap analysis, task execution, optional staging operations, and report generation. This centralized orchestration ensures reproducibility, auditability, and error handling across the entire generation pipeline.

**Details:**
- **Execution Flow:** CLI entry point main() called → asyncio.run(run_full_generation()) → Environment check (CONTENT_FACTORY_GENERATION_ENABLED) → Lock acquisition (ContentGenerationRunLock.acquire()) → Run record creation (ContentGenerationRun) → Planning phase (planner.plan_missing_for_run()) → Execution loop (for each task_id in plan_result) → Task execution and status update → Optional: seed_approved_to_staging → Optional: verify_staging → Optional: write_report → finally: lock.release()
- **Concurrency Safety:** Distributed lock with TTL prevents concurrent overnight runs. Lock acquisition uses holder identifier (hostname:pid) for tracking. Lock release in finally block ensures cleanup even on failure. Task execution is sequential within a run. No distributed locks needed within single run as operations are ordered
- **Covered Objects:** ContentGenerationRunLock, ContentGenerationRun record, ContentGenerationPlanner, ContentGenerationTask records, ContentSeedPromotionService, ContentStagingReadinessService, ContentGenerationReporter, Database session, CLI arguments
- **Timeouts:** Lock acquisition: ~1-5s. Run creation: ~10-50ms. Planning phase: ~1-5min. Task execution: varies by task count (5-30min per task). Staging operations: ~1-5min. Report generation: ~10-30s. Total overnight run: ~30min to several hours depending on task count
- **Migration Path:** From manual content generation to automated overnight pipeline. Migration requires: 1) Implement distributed lock mechanism, 2) Create run tracking system, 3) Integrate planner and executor services, 4) Add optional staging and reporting phases, 5) Configure cron/scheduler for overnight execution
- **Error Handling:** Environment check fails if CONTENT_FACTORY_GENERATION_ENABLED is false. Lock acquisition fails if lock already held (returns error). Planning failures logged and may fail run. Task execution failures logged but don't stop entire run. Lock release in finally ensures cleanup. All errors logged to stdout and error log
- **Security Considerations:** Lock holder identifier includes hostname and pid for tracking. Run records track who initiated generation. Environment variable controls enablement. Database credentials from environment. No secrets in CLI arguments. Report generation may include sensitive metadata

**Trace text diagram:**
```
Overnight Batch Run Entry Point
├── CLI Entry: main() <-- 1a
│   └── asyncio.run(run_full_generation()) <-- run_full_generation.py:201
│       ├── Environment check <-- run_full_generation.py:48
│       │   └── CONTENT_FACTORY_GENERATION_ENABLED
│       ├── Lock acquisition <-- 1b
│       │   └── ContentGenerationRunLock.acquire()
│       ├── Run record creation <-- 1c
│       │   └── ContentGenerationRun(run_id, status)
│       ├── Planning phase <-- 1d
│       │   └── planner.plan_missing_for_run()
│       ├── Execution loop <-- run_full_generation.py:110
│       │   ├── for task_id in plan_result
│       │   └── task.status = "completed" <-- run_full_generation.py:127
│       ├── Optional: seed_approved_to_staging <-- run_full_generation.py:142
│       ├── Optional: verify_staging <-- run_full_generation.py:148
│       ├── Optional: write_report <-- run_full_generation.py:154
│       └── finally: lock.release() <-- 1e
```

**Location ID: 1a**
- **Title:** Entry Point: Main Function
- **Description:** Async entry point that kicks off the full generation pipeline with parsed CLI arguments
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/scripts/content_factory/run_full_generation.py:201

**Location ID: 1b**
- **Title:** Lock Acquisition
- **Description:** Prevents concurrent overnight runs by acquiring a distributed lock with TTL
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/scripts/content_factory/run_full_generation.py:57

**Location ID: 1c**
- **Title:** Run Record Creation
- **Description:** Creates database record tracking this generation run with metadata about layers and limits
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/scripts/content_factory/run_full_generation.py:67

**Location ID: 1d**
- **Title:** Invoke Planner
- **Description:** Delegates to ContentGenerationPlanner to analyze gaps and create generation tasks
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/scripts/content_factory/run_full_generation.py:89

**Location ID: 1e**
- **Title:** Lock Release
- **Description:** Ensures lock is released in finally block even if generation fails
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/scripts/content_factory/run_full_generation.py:179

### AI Guide: Overnight Run Orchestration

**Overview:** The overnight run orchestration is the main entry point for the content generation pipeline, coordinating all phases from lock acquisition through report generation. This trace shows how the system ensures safe, non-concurrent execution while providing flexibility for optional staging and reporting phases.

**Key Components:**

1. **Lock Management (1b, 1e):** Distributed lock prevents concurrent runs, ensuring data integrity. Lock includes holder identifier (hostname:pid) for tracking. Finally block ensures lock release even on failure.

2. **Run Tracking (1c):** ContentGenerationRun record tracks metadata, status, and timing for auditability. Enables monitoring and debugging of generation runs.

3. **Planning Phase (1d):** Delegates to ContentGenerationPlanner to analyze coverage gaps and create tasks. Centralizes gap analysis logic.

4. **Execution Loop:** Sequentially executes tasks created during planning. Updates task status as tasks complete. Handles failures gracefully without stopping entire run.

5. **Optional Phases:** Staging seeding and verification are optional based on CLI flags. Report generation is optional for debugging and audit purposes.

**Best Practices:**
- Always acquire lock before starting generation
- Use finally block for lock release
- Track run metadata for auditability
- Handle task failures gracefully
- Use environment variables for configuration
- Log all phases for debugging
- Validate environment before starting

**Common Issues:**
- Lock already held: Another run is in progress, wait or investigate
- Planning failures: Check source data availability and configuration
- Task execution failures: Check provider configuration and source quality
- Staging failures: Verify staging readiness and artifact approval status

## Trace ID: 2
**Title:** Content Gap Planning: Readiness Analysis to Task Creation

**Description:** ContentGenerationPlanner service that identifies coverage gaps via staging readiness verification, validates source context availability, and creates idempotent generation tasks

**Motivation:**
EduBoost V2 uses a gap analysis system to identify missing content before generation, ensuring efficient resource utilization and avoiding duplicate work. The planner analyzes current coverage against targets, validates source availability, and creates generation tasks only for missing content. This approach prevents over-generation, ensures source data is available before attempting generation, and provides idempotency through task deduplication. The system balances comprehensive coverage analysis with performance by batching operations and using efficient database queries.

**Details:**
- **Execution Flow:** ContentGenerationPlanner.plan_missing_for_run() called → Get run and scopes from registry → For each scope: Verify scope readiness via ContentStagingReadinessService.verify_scope() → For each layer in report: Calculate missing count (target - approved) → Build source context via SourceContextService.validate ETL chunks → Check idempotency key (prevent duplicate tasks) → Create task record (ContentGenerationTask) → Persist task to session (session.add) → Update run metadata with plan → Return GenerationPlanResult
- **Concurrency Safety:** Planning is read-only for existing data. Task creation uses idempotency key to prevent duplicates. Database session provides transaction isolation. No distributed locks needed as planning is idempotent. Multiple planners can run concurrently on different runs
- **Covered Objects:** ContentGenerationPlanner, ContentStagingReadinessService, SourceContextService, ContentGenerationTask records, ContentScope records, GenerationPlanResult, Database session, Scope definitions, Layer targets
- **Timeouts:** Scope loading: ~100-500ms per scope. Readiness verification: ~1-5s per scope. Source context validation: ~500ms-2s per scope. Task creation: ~10-50ms per task. Total planning: ~5-30min depending on scope count
- **Migration Path:** From manual task creation to automated gap analysis. Migration requires: 1) Implement readiness verification service, 2) Add source context validation, 3) Implement idempotency key logic, 4) Create task creation with deduplication, 5) Update run tracking with plan metadata
- **Error Handling:** Scope loading failures logged and skip scope. Readiness verification failures logged and skip scope. Source context validation failures skip layer (no task created). Idempotency check prevents duplicate tasks. Database failures fail entire planning phase. All errors logged with context
- **Security Considerations:** Idempotency key prevents duplicate generation. Source context validation ensures approved sources only. Task metadata tracks provenance. No secrets in task records. Scope access controlled by registry

**Trace text diagram:**
```
Content Gap Planning Pipeline
└── ContentGenerationPlanner.plan_missing_for_run() <-- content_generation_planner.py:49
    ├── Get run and scopes from registry <-- content_generation_planner.py:59
    ├── For each scope: <-- content_generation_planner.py:68
    │   ├── Verify scope readiness <-- 2a
    │   │   └── ContentStagingReadinessService
    │   │       └── verify_scope() <-- content_staging_readiness.py:132
    │   ├── For each layer in report: <-- content_generation_planner.py:70
    │   │   ├── Calculate missing count <-- 2b
    │   │   │   └── target - approved
    │   │   ├── Build source context <-- 2c
    │   │   │   └── SourceContextService
    │   │   │       └── validate ETL chunks <-- source_context.py:42
    │   │   ├── Check idempotency key <-- content_generation_planner.py:83
    │   │   └── Create task record <-- 2d
    │   │       └── ContentGenerationTask()
    │   └── Persist task to session <-- 2e
    │       └── session.add(task)
    └── Update run metadata with plan <-- content_generation_planner.py:119
        └── return GenerationPlanResult <-- content_generation_planner.py:121
```

**Location ID: 2a**
- **Title:** Verify Scope Readiness
- **Description:** Analyzes current coverage vs targets to identify missing artifacts per layer
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_generation_planner.py:69

**Location ID: 2b**
- **Title:** Calculate Gap
- **Description:** Computes how many artifacts are needed to reach coverage target
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_generation_planner.py:73

**Location ID: 2c**
- **Title:** Build Source Context
- **Description:** Validates that approved ETL source chunks are available for generation
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_generation_planner.py:77

**Location ID: 2d**
- **Title:** Create Generation Task
- **Description:** Creates task record with idempotency key to prevent duplicate generation
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_generation_planner.py:88

**Location ID: 2e**
- **Title:** Persist Task
- **Description:** Adds task to database session for batch insertion
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_generation_planner.py:112

### AI Guide: Content Gap Planning

**Overview:** The content gap planning system analyzes coverage gaps, validates source availability, and creates generation tasks. This trace shows how the planner ensures efficient resource utilization by only generating missing content while preventing duplicate work through idempotency.

**Key Components:**

1. **Readiness Verification (2a):** ContentStagingReadinessService analyzes current coverage against targets. Identifies which layers need generation. Ensures staging readiness before planning.

2. **Gap Calculation (2b):** Computes missing count as target - approved. Handles edge cases (negative gaps, zero gaps). Skips layers with no missing content.

3. **Source Context Validation (2c):** SourceContextService validates ETL source chunks. Ensures approved sources are available. Validates quality and licensing.

4. **Idempotency Check:** Uses composite key (scope, layer, source chunks) to prevent duplicate tasks. Enables safe re-running of planning phase.

5. **Task Creation (2d, 2e):** Creates ContentGenerationTask with metadata. Batch persists to database for efficiency. Tracks provenance and configuration.

**Best Practices:**
- Always validate source availability before creating tasks
- Use idempotency keys to prevent duplicates
- Batch database operations for efficiency
- Log skipped tasks for transparency
- Handle edge cases (zero gaps, negative gaps)
- Validate scope and layer configuration

**Common Issues:**
- No tasks created: Check source availability and configuration
- Duplicate tasks: Verify idempotency key logic
- Planning slow: Optimize database queries, batch operations
- Source validation failures: Check ETL pipeline and source quality

## Trace ID: 3
**Title:** Task Execution: Provider Invocation to Artifact Creation

**Description:** ContentGenerationExecutor service that executes queued tasks by calling generation providers (deterministic or LLM) and creating validated artifacts

**Motivation:**
EduBoost V2 implements a task execution system that coordinates provider invocation with artifact creation and validation. The executor manages task lifecycle (queued → running → succeeded/failed), locks tasks to prevent concurrent execution, and integrates multiple provider types (deterministic and LLM). This abstraction allows for flexible provider implementation while maintaining consistent artifact creation and validation. The system handles provider failures gracefully, supports artifact limits per task, and ensures provenance tracking through source citations.

**Details:**
- **Execution Flow:** ContentGenerationExecutor.execute_task() called → task.status = "running" → Lock task with expiration → Source context validation (source_context_service.build_context()) → Provider invocation (_call_provider(provider, task, chunks)) → Build DiagnosticGenerationRequest → provider.generate_diagnostic_items() → Return validation lambdas → Artifact creation loop (for each payload) → stable_json_hash(artifact_json) → validation_errors() call → content_factory_service.create_artifact() → validate_artifact_payload → ContentGenerationArtifact() → ContentArtifactSource records → Update task metadata (task.output_artifact_ids) → task.status = "succeeded"/"failed" → session.flush()
- **Concurrency Safety:** Task lock with expiration prevents concurrent execution. Lock includes holder identifier and expiration timestamp. Source context validation is stateless. Provider invocation is isolated per task. Artifact creation uses database transactions. No distributed locks needed as task-level locks suffice
- **Covered Objects:** ContentGenerationExecutor, ContentGenerationTask, SourceContextService, Generation providers (deterministic, LLM), ContentFactoryService, ContentGenerationArtifact, ContentArtifactSource, Database session, Validation lambdas, Artifact hashes
- **Timeouts:** Task lock acquisition: ~10-50ms. Source context validation: ~500ms-2s. Provider invocation: ~5-30s per artifact. Artifact creation: ~100-500ms per artifact. Task completion: ~10-60s depending on artifact count
- **Migration Path:** From direct provider calls to executor abstraction. Migration requires: 1) Implement task locking mechanism, 2) Add source context re-validation, 3) Integrate provider abstraction, 4) Add artifact creation loop, 5) Implement task status updates
- **Error Handling:** Task lock failures skip task (already running). Source context validation failures fail task. Provider invocation failures fail task with error details. Artifact creation failures logged but don't stop task. Task status updated based on overall success. All errors logged with context
- **Security Considerations:** Task lock prevents concurrent execution. Source context validation ensures approved sources. Provider credentials from environment. Artifact validation ensures quality. Provenance tracking via source citations. No secrets in task records

**Trace text diagram:**
```
Task Execution Flow (Trace 3)
└── ContentGenerationExecutor.execute_task() <-- content_generation_executor.py:67
    ├── task.status = "running" <-- 3a
    ├── Lock task with expiration <-- content_generation_executor.py:78
    ├── Source context validation
    │   └── source_context_service.build_context() <-- 3b
    ├── Provider invocation
    │   └── _call_provider(provider, task, chunks) <-- 3c
    │       ├── Build DiagnosticGenerationRequest <-- content_generation_executor.py:196
    │       ├── provider.generate_diagnostic_items() <-- deterministic.py:16
    │       └── Return validation lambdas <-- content_generation_executor.py:197
    ├── Artifact creation loop <-- content_generation_executor.py:91
    │   ├── stable_json_hash(artifact_json) <-- content_generation_executor.py:93
    │   ├── validation_errors() call <-- content_generation_executor.py:94
    │   └── content_factory_service.create_artifact() <-- 3d
    │       ├── validate_artifact_payload() <-- content_factory.py:177
    │       ├── ContentGenerationArtifact() <-- content_factory.py:185
    │       └── ContentArtifactSource records <-- content_factory.py:206
    ├── Update task metadata
    │   ├── task.output_artifact_ids <-- content_generation_executor.py:127
    │   └── task.status = "succeeded"/"failed" <-- 3e
    └── session.flush() <-- content_generation_executor.py:136
```

**Location ID: 3a**
- **Title:** Mark Task Running
- **Description:** Updates task status and acquires lock with expiration timestamp
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_generation_executor.py:76

**Location ID: 3b**
- **Title:** Rebuild Source Context
- **Description:** Re-validates source availability at execution time (may have changed since planning)
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_generation_executor.py:82

**Location ID: 3c**
- **Title:** Call Generation Provider
- **Description:** Invokes deterministic or LLM provider to generate content artifacts
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_generation_executor.py:87

**Location ID: 3d**
- **Title:** Create Artifact Record
- **Description:** Persists generated artifact with validation, provenance, and source citations
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_generation_executor.py:97

**Location ID: 3e**
- **Title:** Update Task Status
- **Description:** Marks task as succeeded or failed based on artifact creation results
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_generation_executor.py:133

### AI Guide: Task Execution

**Overview:** The task execution system manages the lifecycle of generation tasks, coordinating provider invocation with artifact creation. This trace shows how the executor ensures safe, isolated task execution while supporting multiple provider types and maintaining comprehensive validation.

**Key Components:**

1. **Task Locking (3a):** Locks task with expiration to prevent concurrent execution. Includes holder identifier for tracking. Expiration prevents stale locks.

2. **Source Context Re-validation (3b):** Re-validates source availability at execution time. Handles changes since planning phase. Ensures sources still approved and available.

3. **Provider Invocation (3c):** Abstracts provider interface (deterministic, LLM). Builds provider-specific requests. Returns validation lambdas for deferred validation.

4. **Artifact Creation Loop (3d):** Iterates through generated payloads. Creates artifacts with validation. Handles duplicate detection via hash. Tracks source citations.

5. **Task Status Updates (3e):** Updates task status based on overall success. Tracks output artifact IDs. Enables monitoring and debugging.

**Best Practices:**
- Always lock tasks before execution
- Re-validate source context at execution time
- Use provider abstraction for flexibility
- Limit artifacts per task to prevent runaway generation
- Handle provider failures gracefully
- Track provenance via source citations
- Update task status accurately

**Common Issues:**
- Task lock failures: Task already running, investigate holder
- Source context failures: Sources changed since planning
- Provider failures: Check provider configuration and credentials
- Artifact creation failures: Check validation rules and data quality
- Task stuck in running state: Check lock expiration

## Trace ID: 4
**Title:** Diagnostic Item Generation: Provider to Validation

**Description:** Layer-specific generation flow showing how diagnostic items are created via DeterministicContentGenerationProvider and validated before artifact creation

**Motivation:**
EduBoost V2 implements layer-specific generation flows to handle different content types appropriately. The diagnostic item generation flow demonstrates how the DeterministicContentGenerationProvider creates structured assessment items with questions, options, answers, and source citations. This provider uses deterministic algorithms rather than LLM generation for consistency and predictability. The flow includes deferred validation via lambdas, allowing validation to occur after generation while maintaining separation of concerns. This approach enables efficient batch generation with comprehensive quality checks.

**Details:**
- **Execution Flow:** ContentGenerationExecutor.execute_task() → _call_provider(provider, task, chunks) → Build DiagnosticGenerationRequest (base dict with scope/chunks/counts) → provider.generate_diagnostic_items() → DeterministicProvider impl → GeneratedDiagnosticItem() (question_text, options, answer, source_chunk_ids) → to_artifact_json() → Return list of payloads (artifact_json, artifact_type, validation_errors lambda) → validation_errors lambda → diagnostic_generator.validate() → Check answer_key exists → Check options count → Check caps_ref match → Check duplicate hash
- **Concurrency Safety:** Provider invocation is stateless and thread-safe. Item generation is independent per item. Validation is independent per item. No shared state between generations. No locks needed as operations are isolated
- **Covered Objects:** DeterministicContentGenerationProvider, DiagnosticGenerationRequest, GeneratedDiagnosticItem, diagnostic_generator, Validation lambdas, Artifact JSON payloads, Source chunk IDs, Answer keys, Options
- **Timeouts:** Request building: ~10-50ms. Item generation: ~100-500ms per item. JSON conversion: ~10-50ms per item. Validation: ~10-50ms per item. Total per item: ~200-1s
- **Migration Path:** From LLM-only generation to hybrid deterministic/LLM. Migration requires: 1) Implement deterministic provider, 2) Add validation lambdas, 3) Integrate with executor, 4) Configure provider selection logic, 5) Test deterministic generation quality
- **Error Handling:** Invalid request parameters fail generation. Item generation failures logged and skip item. Validation failures logged but don't stop generation. Invalid items filtered out during artifact creation. All errors logged with context
- **Security Considerations:** Deterministic generation prevents prompt injection. Source chunk IDs validated before use. Answer keys validated for correctness. Duplicate detection via hash prevents duplicates. No secrets in generated items

**Trace text diagram:**
```
Diagnostic Item Generation Flow
└── ContentGenerationExecutor.execute_task() <-- content_generation_executor.py:67
    └── _call_provider(provider, task, chunks) <-- content_generation_executor.py:175
        ├── Build DiagnosticGenerationRequest <-- content_generation_executor.py:178
        │   └── **base dict with scope/chunks/counts
        ├── provider.generate_diagnostic_items() <-- 4a
        │   └── DeterministicProvider impl <-- deterministic.py:12
        │       └── GeneratedDiagnosticItem() <-- 4b
        │           ├── question_text, options, answer <-- deterministic.py:24
        │           ├── source_chunk_ids from request <-- deterministic.py:32
        │           └── to_artifact_json() <-- 4c
        └── Return list of payloads <-- content_generation_executor.py:197
            └── Each payload contains:
                ├── artifact_json (from 4c) <-- content_generation_executor.py:199
                ├── artifact_type <-- content_generation_executor.py:200
                └── validation_errors lambda <-- 4d
                    └── diagnostic_generator.validate() <-- 4e
                        ├── Check answer_key exists <-- diagnostic_generator.py:10
                        ├── Check options count <-- diagnostic_generator.py:13
                        ├── Check caps_ref match <-- diagnostic_generator.py:19
                        └── Check duplicate hash <-- diagnostic_generator.py:23
```

**Location ID: 4a**
- **Title:** Generate Items via Provider
- **Description:** Calls provider with request containing source chunks, topic info, and counts
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_generation_executor.py:196

**Location ID: 4b**
- **Title:** Create Diagnostic Item
- **Description:** Deterministic provider creates item with question, options, answer, and source citations
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_generation/providers/deterministic.py:23

**Location ID: 4c**
- **Title:** Convert to Artifact JSON
- **Description:** Transforms typed item into JSON payload for artifact storage
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_generation/prompt_payloads.py:60

**Location ID: 4d**
- **Title:** Validation Lambda
- **Description:** Deferred validation that checks answer keys, options, explanations, and duplicates
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_generation_executor.py:204

**Location ID: 4e**
- **Title:** Validate Diagnostic Item
- **Description:** Enforces business rules: answer key required, correct option count, source citations
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_generation/diagnostic_generator.py:8

### AI Guide: Diagnostic Item Generation

**Overview:** The diagnostic item generation flow demonstrates how the DeterministicContentGenerationProvider creates structured assessment items. This trace shows the layer-specific generation approach, deferred validation via lambdas, and quality checks for diagnostic items.

**Key Components:**

1. **Request Building:** DiagnosticGenerationRequest includes scope, chunks, counts, and metadata. Standardizes input for provider. Enables deterministic generation.

2. **Provider Invocation (4a):** Calls deterministic provider with request. Provider implements item generation logic. Returns list of GeneratedDiagnosticItem.

3. **Item Creation (4b):** GeneratedDiagnosticItem includes question, options, answer, source citations. Uses deterministic algorithms for consistency. Tracks provenance via source chunk IDs.

4. **JSON Conversion (4c):** to_artifact_json() transforms typed item to JSON. Standardizes artifact format. Enables storage and validation.

5. **Deferred Validation (4d, 4e):** Validation lambda returned with payload. Validates after generation. Checks answer keys, options, duplicates. Enables batch validation.

**Best Practices:**
- Use deterministic generation for consistent items
- Validate after generation for efficiency
- Track source citations for provenance
- Check answer keys and options
- Detect duplicates via hash
- Use validation lambdas for flexibility

**Common Issues:**
- Invalid items: Check validation rules and source quality
- Duplicate items: Verify hash detection logic
- Missing source citations: Check source chunk IDs
- Invalid answer keys: Validate provider logic

## Trace ID: 5
**Title:** Artifact Creation and Validation: Factory Service Flow

**Description:** ContentFactoryService that validates artifact payloads, verifies source provenance, and creates artifact records with pending_review status (never auto-approves)

**Motivation:**
EduBoost V2 implements a comprehensive artifact creation and validation system to ensure content quality before approval. The ContentFactoryService validates artifact payloads (structure, required fields), verifies source provenance (approved status, license compatibility, quality thresholds), and creates artifact records with pending_review status. The system never auto-approves artifacts, requiring human review for quality control. This approach balances automation with human oversight, ensuring generated content meets quality standards while maintaining efficiency through automated validation.

**Details:**
- **Execution Flow:** ContentFactoryService.create_artifact() called → Extract sources from payload → ContentValidationService.validate_artifact_payload() → Check artifact_json not empty → Verify answer_key for diagnostic items → ETLProvenanceService.validate_source_bundle() → Check document status approved → Verify license compatibility → Validate quality thresholds → Compute source_snapshot_hash → Compute artifact_hash from JSON → Create ContentGenerationArtifact → Set status based on validation (PENDING_REVIEW if passed, VALIDATION_FAILED if errors) → session.add(artifact) → For each source chunk: Create ContentArtifactSource → session.add(source) → Create ContentValidationReport → session.add(report) → session.flush()
- **Concurrency Safety:** Artifact creation uses database transactions. Validation is stateless and thread-safe. Hash computation is deterministic. No shared state between creations. No locks needed as database provides isolation
- **Covered Objects:** ContentFactoryService, ContentValidationService, ETLProvenanceService, ContentGenerationArtifact, ContentArtifactSource, ContentValidationReport, Artifact JSON, Source chunks, Artifact hash, Source snapshot hash
- **Timeouts:** Payload validation: ~10-50ms. Provenance validation: ~100-500ms. Hash computation: ~10-50ms. Artifact creation: ~10-50ms. Source citation creation: ~10-50ms per source. Total: ~200ms-2s per artifact
- **Migration Path:** From auto-approval to human review required. Migration requires: 1) Implement validation service, 2) Add provenance validation, 3) Set status to pending_review, 4) Create validation reports, 5) Implement human review workflow
- **Error Handling:** Invalid payload fails validation with errors. Provenance validation fails with specific errors. Database failures fail artifact creation. All errors logged in validation report. Status reflects validation result
- **Security Considerations:** Never auto-approves artifacts (human review required). Validates source provenance and licensing. Tracks source snapshot hash for integrity. No secrets in artifact records. Validation reports track all checks

**Trace text diagram:**
```
Artifact Creation and Validation Flow
└── ContentFactoryService.create_artifact() <-- 5a
    ├── Extract sources from payload <-- content_factory.py:176
    ├── ContentValidationService
    │   └── validate_artifact_payload() <-- 5a
    │       ├── Check artifact_json not empty <-- content_factory.py:137
    │       ├── Verify answer_key for diagnostic items <-- content_factory.py:141
    │       └── ETLProvenanceService
    │           └── validate_source_bundle() <-- 5b
    │               ├── Check document status approved <-- content_factory.py:84
    │               ├── Verify license compatibility <-- content_factory.py:90
    │               ├── Validate quality thresholds <-- content_factory.py:98
    │               └── Compute source_snapshot_hash <-- content_factory.py:115
    ├── Compute artifact_hash from JSON <-- content_factory.py:184
    ├── Create ContentGenerationArtifact <-- 5c
    │   └── Set status based on validation <-- 5d
    │       ├── PENDING_REVIEW if passed <-- content_factory.py:190
    │       └── VALIDATION_FAILED if errors <-- content_factory.py:192
    ├── session.add(artifact) <-- content_factory.py:196
    ├── For each source chunk <-- content_factory.py:199
    │   └── Create ContentArtifactSource <-- 5e
    │       └── session.add(source) <-- content_factory.py:206
    ├── Create ContentValidationReport <-- content_factory.py:231
    │   └── session.add(report) <-- content_factory.py:231
    └── session.flush() <-- content_factory.py:239
```

**Location ID: 5a**
- **Title:** Validate Artifact Payload
- **Description:** Runs validation checks on artifact JSON and source bundle
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_factory.py:177

**Location ID: 5b**
- **Title:** Validate Source Provenance
- **Description:** Verifies ETL sources are approved, licensed correctly, and meet quality thresholds
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_factory.py:145

**Location ID: 5c**
- **Title:** Create Artifact Record
- **Description:** Instantiates artifact with computed hash and source snapshot hash
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_factory.py:185

**Location ID: 5d**
- **Title:** Set Initial Status
- **Description:** Status is pending_review if validation passed, validation_failed otherwise
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_factory.py:189

**Location ID: 5e**
- **Title:** Add Source Citation
- **Description:** Creates ContentArtifactSource records linking artifact to ETL source chunks
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_factory.py:206

### AI Guide: Artifact Creation and Validation

**Overview:** The artifact creation and validation system ensures content quality through comprehensive validation before human review. This trace shows how the ContentFactoryService validates payloads, verifies provenance, and creates artifacts with pending_review status.

**Key Components:**

1. **Payload Validation (5a):** ContentValidationService checks artifact structure. Verifies required fields exist. Validates diagnostic-specific fields (answer_key). Returns validation result with errors.

2. **Provenance Validation (5b):** ETLProvenanceService validates source bundle. Checks document approval status. Verifies license compatibility. Validates quality thresholds. Computes source snapshot hash.

3. **Artifact Creation (5c):** ContentGenerationArtifact created with hashes. Artifact hash for deduplication. Source snapshot hash for provenance tracking. Status set based on validation.

4. **Status Setting (5d):** PENDING_REVIEW if validation passed. VALIDATION_FAILED if errors. Never auto-approves (human review required). Enables quality control.

5. **Source Citations (5e):** ContentArtifactSource records link artifact to sources. Tracks provenance. Enables source tracking and attribution.

**Best Practices:**
- Always validate before creating artifacts
- Never auto-approve (human review required)
- Track source provenance and licensing
- Compute hashes for deduplication
- Create validation reports for audit
- Link artifacts to sources

**Common Issues:**
- Validation failures: Check payload structure and source quality
- Provenance failures: Verify source approval and licensing
- Status errors: Ensure validation logic correct
- Missing source citations: Check source extraction logic

## Trace ID: 6
**Title:** Staging Readiness Verification: Coverage Analysis

**Description:** ContentStagingReadinessService that analyzes scope coverage by loading artifacts, checking provenance/license/quality, and identifying blockers

**Motivation:**
EduBoost V2 implements a staging readiness verification system to determine which artifacts are ready for staging. The ContentStagingReadinessService analyzes scope coverage by loading artifacts, checking provenance (approved status), license compatibility, and quality thresholds. This analysis identifies blockers (insufficient coverage, quality issues) and calculates stageable counts (approved artifacts minus those with issues). The system enables informed decisions about staging while ensuring only high-quality content is promoted to staging environments.

**Details:**
- **Execution Flow:** ContentStagingReadinessService.verify_scope(scope_id, session) called → Load Data Phase: _load_scope_artifacts() → _load_source_index() → Analysis Phase: for each target in scope → filter matching artifacts → _layer_summary() → count by status → filter approved artifacts → _has_valid_provenance() → _has_invalid_license() → _has_low_source_quality() → calculate stageable → _layer_blockers() → Return ScopeStagingVerificationReport (status, can_seed_staging flag, blockers list, layers summaries)
- **Concurrency Safety:** Artifact loading is read-only. Analysis is stateless and thread-safe. No shared state between verifications. No locks needed as operations are read-only. Multiple verifications can run concurrently
- **Covered Objects:** ContentStagingReadinessService, ScopeStagingVerificationReport, LayerReadinessSummary, ScopeBlocker, ContentGenerationArtifact, ContentArtifactSource, Source index, Layer targets, Coverage counts
- **Timeouts:** Artifact loading: ~100-500ms. Source index building: ~50-200ms. Layer analysis: ~100-500ms per layer. Blocker identification: ~50-200ms per layer. Total verification: ~1-5s per scope
- **Migration Path:** From manual staging decisions to automated verification. Migration requires: 1) Implement artifact loading, 2) Add source index building, 3) Implement layer analysis, 4) Add blocker identification, 5) Create verification report structure
- **Error Handling:** Artifact loading failures logged and skip scope. Analysis failures logged with context. Missing targets logged as not configured. All errors included in verification report
- **Security Considerations:** Only approved artifacts considered for staging. Validates license compatibility. Checks quality thresholds. Identifies security blockers. No secrets in verification reports

**Trace text diagram:**
```
Staging Readiness Verification Flow
└── ContentStagingReadinessService <-- content_staging_readiness.py:104
    └── verify_scope(scope_id, session) <-- content_staging_readiness.py:132
        ├── Load Data Phase
        │   ├── _load_scope_artifacts() <-- 6a
        │   └── _load_source_index() <-- 6b
        ├── Analysis Phase
        │   └── for each target in scope <-- content_staging_readiness.py:157
        │       ├── filter matching artifacts <-- content_staging_readiness.py:163
        │       ├── _layer_summary() <-- 6c
        │       │   ├── count by status <-- content_staging_readiness.py:296
        │       │   ├── filter approved artifacts <-- content_staging_readiness.py:299
        │       │   ├── _has_valid_provenance() <-- content_staging_readiness.py:398
        │       │   ├── _has_invalid_license() <-- content_staging_readiness.py:405
        │       │   ├── _has_low_source_quality() <-- content_staging_readiness.py:409
        │       │   └── calculate stageable <-- 6d
        │       └── _layer_blockers() <-- 6e
        └── Return ScopeStagingVerificationReport <-- content_staging_readiness.py:180
            ├── status (ready/blocked/partial) <-- content_staging_readiness.py:182
            ├── can_seed_staging flag <-- content_staging_readiness.py:183
            ├── blockers list <-- content_staging_readiness.py:185
            └── layers summaries <-- content_staging_readiness.py:186
```

**Location ID: 6a**
- **Title:** Load Scope Artifacts
- **Description:** Fetches all artifacts for the scope from content_generation_artifacts table
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_staging_readiness.py:152

**Location ID: 6b**
- **Title:** Load Source Index
- **Description:** Builds map of artifact_id to source citations for provenance checks
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_staging_readiness.py:153

**Location ID: 6c**
- **Title:** Compute Layer Summary
- **Description:** Analyzes approved vs target counts, identifies invalid provenance/license/quality
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_staging_readiness.py:168

**Location ID: 6d**
- **Title:** Calculate Stageable Count
- **Description:** Subtracts artifacts with provenance/license/quality issues from approved count
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_staging_readiness.py:303

**Location ID: 6e**
- **Title:** Identify Blockers
- **Description:** Generates blocker records for insufficient coverage or quality issues
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_staging_readiness.py:170

### AI Guide: Staging Readiness Verification

**Overview:** The staging readiness verification system analyzes scope coverage to determine which artifacts are ready for staging. This trace shows how the ContentStagingReadinessService checks provenance, licensing, and quality to identify blockers and calculate stageable counts.

**Key Components:**

1. **Data Loading (6a, 6b):** Loads all artifacts for scope. Builds source index for provenance checks. Efficient batch loading for performance.

2. **Layer Analysis (6c):** _layer_summary() analyzes each layer. Counts artifacts by status. Filters approved artifacts. Checks provenance, license, quality.

3. **Stageable Calculation (6d):** Calculates stageable count as approved minus issues. Subtracts invalid provenance, invalid license, low quality. Handles edge cases (negative counts).

4. **Blocker Identification (6e):** _layer_blockers() generates blocker records. Identifies insufficient coverage. Identifies quality issues. Enables targeted fixes.

5. **Verification Report:** Returns comprehensive report with status, can_seed_staging flag, blockers, and layer summaries. Enables informed staging decisions.

**Best Practices:**
- Load data efficiently in batches
- Check all quality dimensions (provenance, license, quality)
- Calculate stageable counts accurately
- Identify specific blockers for fixes
- Provide comprehensive verification reports
- Handle edge cases (zero targets, negative counts)

**Common Issues:**
- No artifacts loaded: Check scope configuration and artifact status
- All blocked: Check source quality and licensing
- Stageable count wrong: Verify calculation logic
- Missing blockers: Check blocker identification logic

## Trace ID: 7
**Title:** Staging Seed Execution: Approved Artifacts to Staging Tables

**Description:** ContentStagingSeedExecutor that promotes only approved artifacts to staging tables (lesson_bank, assessment_blueprints, study_plan_templates) for preview

**Motivation:**
EduBoost V2 implements a staging seed execution system to promote approved artifacts to staging tables for preview and testing. The ContentStagingSeedExecutor identifies seedable artifacts (approved with valid provenance), creates seed run records for tracking, and promotes artifacts to staging tables (lesson_bank, assessment_blueprints, study_plan_templates). This system enables content preview in staging environments before production deployment, ensuring quality and correctness. The executor supports partial seeding (skip artifacts with issues) and tracks all operations for auditability.

**Details:**
- **Execution Flow:** ContentSeedPromotionService.seed_staging() called → _seed_gate() validation (Check stageable_approved count) → seed_executor.seed_staging() → _plan_seed() identify artifacts → ContentSeedRun() creation → session.add(run) → For each seedable artifact: ContentStagingArtifact() creation → session.add(staging_artifact) → artifact.status update (APPROVED → SEEDED_STAGING) → session.flush() persist changes
- **Concurrency Safety:** Seed gate validation prevents concurrent seeding. Seed run tracking provides auditability. Artifact status update uses database transactions. No distributed locks needed as database provides isolation. Multiple seed operations can run on different scopes
- **Covered Objects:** ContentSeedPromotionService, ContentStagingSeedExecutor, ContentSeedRun, ContentStagingArtifact, ContentGenerationArtifact, Staging tables (lesson_bank, assessment_blueprints, study_plan_templates), Database session
- **Timeouts:** Seed gate validation: ~10-50ms. Seed planning: ~100-500ms. Seed run creation: ~10-50ms. Artifact promotion: ~50-200ms per artifact. Session flush: ~100-500ms. Total seeding: ~1-5min depending on artifact count
- **Migration Path:** From manual staging to automated seeding. Migration requires: 1) Implement seed gate validation, 2) Add seed run tracking, 3) Implement artifact promotion logic, 4) Create staging tables, 5) Add status transition logic
- **Error Handling:** Seed gate failures prevent seeding. Planning failures logged and skip seeding. Artifact promotion failures logged but don't stop seeding. Status update failures logged. All errors tracked in seed run record
- **Security Considerations:** Only approved artifacts seeded. Seed gate validation prevents unauthorized seeding. Seed run tracking provides auditability. Staging tables isolated from production. No secrets in staging artifacts

**Trace text diagram:**
```
Staging Seed Execution Pipeline
├── ContentSeedPromotionService.seed_staging() <-- content_seed_promotion.py:51
│   ├── _seed_gate() validation <-- 7a
│   │   └── Check stageable_approved count <-- content_seed_promotion.py:61
│   └── seed_executor.seed_staging() <-- 7b
│       ├── _plan_seed() identify artifacts <-- content_staging_seed_executor.py:98
│       ├── ContentSeedRun() creation <-- 7c
│       ├── session.add(run) <-- content_seed_promotion.py:87
│       └── For each seedable artifact: <-- content_staging_seed_executor.py:94
│           ├── ContentStagingArtifact() creation <-- content_factory.py:453
│           ├── session.add(staging_artifact) <-- content_staging_seed_executor.py:92
│           └── artifact.status update <-- 7d
│               └── APPROVED → SEEDED_STAGING <-- content_factory.py:47
└── session.flush() persist changes <-- content_seed_promotion.py:88
```

**Location ID: 7a**
- **Title:** Plan Seed Operation
- **Description:** Identifies which approved artifacts are seedable vs skipped
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_staging_seed_executor.py:98

**Location ID: 7b**
- **Title:** Execute Staging Seed
- **Description:** Delegates to executor to perform actual seeding with allow_partial flag
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_seed_promotion.py:66

**Location ID: 7c**
- **Title:** Create Seed Run Record
- **Description:** Tracks this seeding operation with status and summary metadata
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_staging_seed_executor.py:75

**Location ID: 7d**
- **Title:** Update Artifact Status
- **Description:** Transitions artifact from approved to seeded_staging after successful seed
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_factory.py:296

### AI Guide: Staging Seed Execution

**Overview:** The staging seed execution system promotes approved artifacts to staging tables for preview. This trace shows how the ContentStagingSeedExecutor identifies seedable artifacts, tracks seed operations, and updates artifact status.

**Key Components:**

1. **Seed Gate Validation (7a):** _seed_gate() validates stageable count. Prevents seeding if no artifacts ready. Ensures meaningful seeding operations.

2. **Seed Planning:** _plan_seed() identifies seedable artifacts. Distinguishes seedable vs skipped artifacts. Supports partial seeding (skip issues).

3. **Seed Run Tracking (7c):** ContentSeedRun tracks operation. Records status and metadata. Enables auditability and debugging.

4. **Artifact Promotion:** Creates ContentStagingArtifact records. Promotes to staging tables. Links to original artifact.

5. **Status Update (7d):** Transitions artifact status (APPROVED → SEEDED_STAGING). Tracks seeding history. Prevents re-seeding.

**Best Practices:**
- Validate before seeding (seed gate)
- Track all seed operations for audit
- Support partial seeding (skip issues)
- Update artifact status accurately
- Isolate staging from production
- Log all seeding operations

**Common Issues:**
- Seed gate failures: Check stageable count and readiness
- No artifacts seeded: Check planning logic and artifact status
- Status update failures: Verify status transition logic
- Staging table errors: Check table structure and permissions

## Trace ID: 8
**Title:** Report Generation: Summary and Evidence Export

**Description:** ContentGenerationReporter that writes comprehensive reports with markdown summaries, JSON metadata, and CSV exports for all tasks and artifacts

**Motivation:**
EduBoost V2 implements a comprehensive report generation system to document generation runs for auditability and debugging. The ContentGenerationReporter creates timestamped report directories with markdown summaries (human-readable), JSON metadata (machine-readable), and CSV exports (spreadsheet analysis). The system reports on planned tasks, executed tasks, generated artifacts, pending review items, and errors. This documentation enables tracking of generation runs, analysis of success rates, and debugging of failures. Reports are stored in timestamped directories for historical tracking.

**Details:**
- **Execution Flow:** main() CLI entry point → asyncio.run(run_full_generation()) → Lock acquisition phase → Run creation & planning phase → Task execution loop → Report generation phase → reporter.write_report(report_data) → Create timestamped directory → _write_summary_md() → _write_summary_json() → CSV exports (_write_csv(planned_tasks), _write_csv(executed_tasks), _write_csv(generated_artifacts), _write_csv(pending_review)) → _write_errors_log()
- **Concurrency Safety:** Report generation is stateless and thread-safe. Directory creation uses atomic operations. File writes are independent. No shared state between reports. No locks needed as operations are isolated
- **Covered Objects:** ContentGenerationReporter, Report data (tasks, artifacts, errors), Timestamped directory, Markdown summary, JSON metadata, CSV exports, Error log, File system
- **Timeouts:** Directory creation: ~10-50ms. Summary markdown: ~100-500ms. Summary JSON: ~50-200ms. CSV exports: ~100-500ms per CSV. Error log: ~10-50ms. Total report generation: ~500ms-2s
- **Migration Path:** From no reporting to comprehensive reports. Migration requires: 1) Implement reporter service, 2) Add markdown summary generation, 3) Add JSON metadata export, 4) Add CSV exports, 5) Add error logging
- **Error Handling:** Directory creation failures fail report. File write failures logged but don't stop report. Missing data handled gracefully. All errors logged to stdout
- **Security Considerations:** Reports may contain sensitive metadata. Error logs may contain stack traces. No secrets in reports. Report directories timestamped for organization. File permissions restrict access

**Trace text diagram:**
```
Overnight Run Orchestration (run_full_generation.py)
└── main() CLI entry point <-- run_full_generation.py:183
    └── asyncio.run(run_full_generation()) <-- 8a
        ├── Lock acquisition phase
        │   └── lock.acquire(session, holder) <-- 1b
        ├── Run creation & planning phase
        │   ├── ContentGenerationRun() instantiation <-- run_full_generation.py:67
        │   └── planner.plan_missing_for_run() <-- run_full_generation.py:89
        ├── Task execution loop
        │   └── [tasks executed, artifacts created]
        └── Report generation phase <-- 8a
            └── reporter.write_report(report_data) <-- run_full_generation.py:172
                ├── Create timestamped directory <-- 8b
                ├── _write_summary_md() <-- 8c
                ├── _write_summary_json() <-- content_generation_reporter.py:63
                ├── CSV exports
                │   ├── _write_csv(planned_tasks) <-- 8d
                │   ├── _write_csv(executed_tasks) <-- content_generation_reporter.py:71
                │   ├── _write_csv(generated_artifacts) <-- content_generation_reporter.py:72
                │   └── _write_csv(pending_review) <-- content_generation_reporter.py:73
                └── _write_errors_log() <-- 8e
```

**Location ID: 8a**
- **Title:** Write Report
- **Description:** Invokes reporter to generate timestamped report directory with all artifacts
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/scripts/content_factory/run_full_generation.py:172

**Location ID: 8b**
- **Title:** Create Report Directory
- **Description:** Creates timestamped directory under reports/content_factory/full_generation/
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_generation_reporter.py:56

**Location ID: 8c**
- **Title:** Write Summary Markdown
- **Description:** Generates human-readable summary.md with run status and metrics
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_generation_reporter.py:60

**Location ID: 8d**
- **Title:** Export Task CSVs
- **Description:** Writes CSV files for planned, executed, pending review, and failed artifacts
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_generation_reporter.py:70

**Location ID: 8e**
- **Title:** Write Error Log
- **Description:** Logs all errors encountered during generation for debugging
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_generation_reporter.py:86

### AI Guide: Report Generation

**Overview:** The report generation system creates comprehensive documentation of generation runs. This trace shows how the ContentGenerationReporter produces markdown summaries, JSON metadata, CSV exports, and error logs for auditability and debugging.

**Key Components:**

1. **Directory Creation (8b):** Creates timestamped directory. Organizes reports by time. Prevents overwriting previous reports.

2. **Markdown Summary (8c):** _write_summary_md() generates human-readable summary. Includes run status and metrics. Enables quick human review.

3. **JSON Metadata:** _write_summary_json() exports machine-readable data. Enables programmatic analysis. Includes all run metadata.

4. **CSV Exports (8d):** _write_csv() exports data to spreadsheets. Separate CSVs for tasks, artifacts, pending review. Enables data analysis.

5. **Error Log (8e):** _write_errors_log() logs all errors. Includes stack traces. Enables debugging and troubleshooting.

**Best Practices:**
- Use timestamped directories for organization
- Generate both human and machine-readable formats
- Export all relevant data (tasks, artifacts, errors)
- Include metadata for programmatic analysis
- Log errors with context for debugging
- Handle missing data gracefully

**Common Issues:**
- Directory creation failures: Check permissions and disk space
- File write failures: Check disk space and permissions
- Missing data: Handle gracefully, log warnings
- Large reports: Consider pagination or compression
