# EduBoost V2 Modular Architecture: Core Domain Modules

Maps the modular monolith's domain modules including authentication, POPIA consent management, IRT-based diagnostics, AI lesson generation, learner profiling, adaptive practice, and background jobs. Key entry points: guardian registration [1b], consent grant with audit [2c], diagnostic IRT calculation [3d], lesson generation pipeline [4e], archetype classification [5c], and ARQ job execution [8b].

## Trace ID: 1
**Title:** Guardian Registration Flow (Auth Module)

**Description:** Authentication module service layer. Traces guardian account creation with PII encryption, password hashing, and audit logging.

**Motivation:**
EduBoost V2's authentication module implements secure guardian registration with POPIA-compliant PII protection. The AuthService.register_guardian() method creates a deterministic hash_email() for duplicate detection without storing plaintext email. It checks for existing guardians via _guardian_repo.get_by_email_hash() to prevent duplicates. The guardian record is created with email_encrypted=encrypt_pii() for POPIA compliance, password_hash=hash_password() for secure credential storage, full_name_encrypted=encrypt_pii() for name protection, and verification_token=generate_token() for email verification. The write_audit_event() logs AuditAction.USER_REGISTERED for compliance trail. The AuthService.authenticate() method verifies credentials via hash_email(), _guardian_repo.get_by_email_hash(), and verify_password(), updates last_login_at, writes AuditAction.USER_LOGIN, and issues JWT tokens via create_access_token() and create_refresh_token(). This secure flow ensures PII protection, credential security, audit compliance, and session management.

**Details:**
- **Execution Flow:** AuthService.register_guardian() → hash_email(email) → Check for existing guardian → _guardian_repo.get_by_email_hash() → Create guardian record → _guardian_repo.create() → email_encrypted=encrypt_pii() → password_hash=hash_password() → full_name_encrypted=encrypt_pii() → verification_token=generate_token() → write_audit_event() → AuditAction.USER_REGISTERED → AuthService.authenticate() → Verify email/password → hash_email(email) → _guardian_repo.get_by_email_hash() → verify_password() → Update last_login_at → write_audit_event() → AuditAction.USER_LOGIN → create_access_token() → create_refresh_token()
- **Concurrency Safety:** Email hash is deterministic. Duplicate check is atomic. Repository operations use transactions. Audit logging is sequential. No distributed locks needed
- **Covered Objects:** Authentication, PII encryption, password hashing, audit logging, JWT tokens, guardian registration
- **Timeouts:** Hash computation: ~1-5ms. Duplicate check: ~10-50ms. Record creation: ~10-50ms. Audit logging: ~10-50ms. Total: ~31-155ms
- **Migration Path:** From plain storage to encrypted. Migration requires: 1) Add encryption, 2) Hash emails, 3) Add audit logging, 4) Update repository
- **Error Handling:** Duplicate errors raised. Encryption errors logged. Hash errors logged. Audit errors logged. All errors logged with context. Sensitive data not logged
- **Security Considerations:** Encrypt PII at rest. Hash emails for lookup. Use bcrypt for passwords. Audit all actions. Validate inputs. Secure JWT tokens

**Trace text diagram:**
```
Guardian Registration Flow (Auth Module)
├── AuthService.register_guardian() <-- service.py:66
│   ├── hash_email(email) <-- 1a
│   ├── Check for existing guardian <-- service.py:111
│   │   └── _guardian_repo.get_by_email_hash() <-- service.py:111
│   ├── Create guardian record <-- 1b
│   │   └── _guardian_repo.create() <-- service.py:115
│   │       ├── email_encrypted=encrypt_pii() <-- 1c
│   │       ├── password_hash=hash_password() <-- service.py:119
│   │       ├── full_name_encrypted=encrypt_pii() <-- service.py:120
│   │       └── verification_token=generate_token() <-- service.py:124
│   └── write_audit_event() <-- 1d
│       └── AuditAction.USER_REGISTERED <-- service.py:129
│
└── AuthService.authenticate() <-- service.py:136
    ├── Verify email/password
    │   ├── hash_email(email) <-- service.py:169
    │   ├── _guardian_repo.get_by_email_hash() <-- service.py:170
    │   └── verify_password() <-- service.py:172
    ├── Update last_login_at <-- service.py:185
    ├── write_audit_event() <-- service.py:186
    │   └── AuditAction.USER_LOGIN <-- service.py:188
    └── create_access_token() <-- 1e
        └── create_refresh_token() <-- service.py:197
```

**Location ID: 1a**
- **Title:** Hash email for lookup
- **Description:** Create deterministic hash for duplicate detection without storing plaintext
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/modules/auth/service.py:110

**Location ID: 1b**
- **Title:** Create guardian record
- **Description:** Persist encrypted guardian with hashed password and verification token
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/modules/auth/service.py:115

**Location ID: 1c**
- **Title:** Encrypt PII at rest
- **Description:** POPIA-compliant encryption of personally identifiable information
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/modules/auth/service.py:118

**Location ID: 1d**
- **Title:** Record audit event
- **Description:** Log USER_REGISTERED action for compliance trail
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/modules/auth/service.py:127

**Location ID: 1e**
- **Title:** Issue JWT tokens
- **Description:** Generate access and refresh tokens for authenticated session
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/modules/auth/service.py:193

### AI Guide: Guardian Registration Flow

**Overview:** Secure guardian registration with POPIA-compliant PII protection, password hashing, and audit logging. This trace shows encryption, hashing, and audit compliance.

**Key Components:**

1. **Hash email for lookup (1a):** Deterministic hash. Duplicate detection. No plaintext storage.

2. **Create guardian record (1b):** Repository creation. Encrypted fields. Secure persistence.

3. **Encrypt PII at rest (1c):** POPIA compliance. Email and name encryption. Data protection.

4. **Record audit event (1d):** AuditAction.USER_REGISTERED. Compliance trail. Audit logging.

5. **Issue JWT tokens (1e):** Access token. Refresh token. Session management.

**Best Practices:**
- Encrypt PII at rest
- Hash emails for lookup
- Use bcrypt for passwords
- Audit all actions
- Validate inputs
- Secure JWT tokens
- Use transactions

**Common Issues:**
- Duplicate detection: Check hash
- Encryption errors: Check keys
- Hash errors: Check algorithm
- Audit missing: Check logging
- Token errors: Check JWT

## Trace ID: 2
**Title:** Consent Grant Lifecycle (Consent Module)

**Description:** POPIA consent service managing parental consent with audit trail. Coordinates with consent repository and audit services for compliance.

**Motivation:**
EduBoost V2's consent module implements POPIA-compliant parental consent management with audit trails. The ConsentService.__init__() initializes with self._repo = ConsentRepository(db) and self._audit_repo = AuditRepository(db) for data access. The consent_decision() method calls get_latest_for_learner() and derive_consent_state() to return ConsentPolicyDecision for canonical consent state. The require_active_consent() method recursively calls consent_decision() and if not decision.active, raises ConsentRequiredError to block unauthorized access. The grant() workflow calls _repo.grant() to CREATE parental_consent record with version, IP, and user agent metadata, then _append_audit() calls audit_repo.append() to INSERT audit_log event and FourthEstateService.record() to log consent.granted event. This consent lifecycle ensures POPIA compliance, audit trails, access control, and state management.

**Details:**
- **Execution Flow:** ConsentService.__init__() → self._repo = ConsentRepository(db) → self._audit_repo = AuditRepository(db) → consent_decision() → get_latest_for_learner() → derive_consent_state() → return ConsentPolicyDecision → require_active_consent() → consent_decision() [recursive call] → if not decision.active: → raise ConsentRequiredError → grant() workflow → _repo.grant() → CREATE parental_consent record → _append_audit() → audit_repo.append() → INSERT audit_log event → FourthEstateService.record() → consent.granted event
- **Concurrency Safety:** Consent decision is deterministic. Repository operations use transactions. Audit logging is sequential. No distributed locks needed
- **Covered Objects:** POPIA consent, consent lifecycle, audit trails, access control, state management
- **Timeouts:** Consent decision: ~10-50ms. Repository operations: ~10-50ms. Audit logging: ~10-50ms. Total: ~30-150ms
- **Migration Path:** From simple consent to POPIA compliance. Migration requires: 1) Add audit logging, 2) Implement state machine, 3) Add access control, 4) Update repository
- **Error Handling:** Consent errors raised. Repository errors logged. Audit errors logged. All errors logged with context. Sensitive data not logged
- **Security Considerations:** Enforce POPIA compliance. Audit consent actions. Validate consent state. Block unauthorized access. Protect learner data. Validate guardian access

**Trace text diagram:**
```
POPIA Consent Lifecycle (app/modules/consent/)
├── ConsentService.__init__() <-- service.py:52
│   ├── self._repo = ConsentRepository(db) <-- service.py:82
│   └── self._audit_repo = AuditRepository(db) <-- service.py:84
├── consent_decision() <-- 2a
│   ├── get_latest_for_learner() <-- 2b
│   └── derive_consent_state() <-- service.py:93
│       └── return ConsentPolicyDecision <-- service.py:93
├── require_active_consent() <-- 2e
│   ├── consent_decision() [recursive call] <-- service.py:101
│   └── if not decision.active: <-- service.py:102
│       └── raise ConsentRequiredError <-- 2f
└── grant() workflow <-- service.py:114
    ├── _repo.grant() <-- 2c
    │   └── CREATE parental_consent record
    └── _append_audit() <-- 2d
        ├── audit_repo.append() <-- service.py:317
        │   └── INSERT audit_log event
        └── FourthEstateService.record() <-- service.py:325
            └── consent.granted event
```

**Location ID: 2a**
- **Title:** Derive consent state
- **Description:** Canonical consent decision for learner access control
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/modules/consent/service.py:90

**Location ID: 2b**
- **Title:** Fetch latest consent
- **Description:** Query repository for most recent consent record
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/modules/consent/service.py:92

**Location ID: 2c**
- **Title:** Grant consent record
- **Description:** Create new consent with version, IP, and user agent metadata
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/modules/consent/service.py:148

**Location ID: 2d**
- **Title:** Append audit event
- **Description:** Record consent.granted event with learner and version details
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/modules/consent/service.py:156

**Location ID: 2e**
- **Title:** Enforce active consent
- **Description:** Require active consent gate before learner data access
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/modules/consent/service.py:101

**Location ID: 2f**
- **Title:** Block unauthorized access
- **Description:** Raise exception when consent is missing or expired
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/modules/consent/service.py:111

### AI Guide: Consent Grant Lifecycle

**Overview:** POPIA consent service with audit trail manages parental consent lifecycle. This trace shows consent decision, enforcement, and audit logging.

**Key Components:**

1. **Derive consent state (2a):** Canonical decision. Access control. State derivation.

2. **Fetch latest consent (2b):** Repository query. Latest record. Consent history.

3. **Grant consent record (2c):** Create record. Version tracking. Metadata.

4. **Append audit event (2d):** Audit logging. FourthEstate. Compliance trail.

5. **Enforce active consent (2e):** Access gate. Consent check. Authorization.

6. **Block unauthorized access (2f):** Raise exception. Consent required. Security.

**Best Practices:**
- Enforce POPIA compliance
- Audit consent actions
- Validate consent state
- Block unauthorized access
- Protect learner data
- Validate guardian access
- Use transactions

**Common Issues:**
- Consent errors: Check state
- Audit missing: Check logging
- Access denied: Check consent
- Repository errors: Check DB
- Compliance issues: Verify POPIA

## Trace ID: 3
**Title:** IRT Diagnostic Engine (Diagnostics Module)

**Description:** Item Response Theory 2PL adaptive assessment engine. Calculates learner ability (theta) and selects optimal items using Fisher information.

**Motivation:**
EduBoost V2's diagnostics module implements Item Response Theory (IRT) for adaptive assessment. The IRT Mathematical Functions include p_correct(theta, a, b) which computes 1/(1 + exp(-a*(theta-b))) for the 2PL probability function, and fisher_information(theta, a, b) which measures item's statistical information. The Item Selection Service's select_item_for_learner() method calls repo.get_unexposed_items() to filter by theta window & exposure control, then ranks by Fisher information. The _3pl_probability(theta, a, b, c) function extends IRT with guessing parameter for item selection. This IRT engine provides accurate ability estimation, adaptive item selection, and statistical optimization for diagnostic assessments.

**Details:**
- **Execution Flow:** IRT Mathematical Functions → p_correct(theta, a, b) → 1/(1 + exp(-a*(theta-b))) → fisher_information(theta, a, b) → measures item's statistical info → Item Selection Service → select_item_for_learner() → repo.get_unexposed_items() → filters by theta window & exposure → rank by Fisher information → _3pl_probability(theta, a, b, c) → extended IRT with guessing param
- **Concurrency Safety:** IRT calculations are deterministic. Item selection is per-learner. Repository operations use transactions. No distributed locks needed
- **Covered Objects:** IRT engine, 2PL model, Fisher information, adaptive selection, theta estimation
- **Timeouts:** IRT calculation: ~1-5ms. Item selection: ~10-50ms. Repository query: ~10-50ms. Total: ~21-105ms
- **Migration Path:** From static to adaptive assessments. Migration requires: 1) Implement IRT engine, 2) Add item selection, 3) Calibrate parameters, 4) Update repository
- **Error Handling:** IRT errors logged. Selection errors logged. Repository errors logged. All errors logged with context. Sensitive data not logged
- **Security Considerations:** Validate item parameters. Protect learner data. Audit diagnostic results. Validate theta estimates. Filter sensitive data

**Trace text diagram:**
```
IRT Diagnostic Engine (Trace 3)
├── IRT Mathematical Functions
│   ├── p_correct(theta, a, b) <-- 3a
│   │   └── 1/(1 + exp(-a*(theta-b))) <-- 3b
│   └── fisher_information(theta, a, b) <-- 3c
│       └── measures item's statistical info <-- irt_engine.py:88
└── Item Selection Service <-- item_bank_service.py:46
    ├── select_item_for_learner() <-- item_bank_service.py:65
    │   ├── repo.get_unexposed_items() <-- 3d
    │   │   └── filters by theta window & exposure <-- item_bank_service.py:81
    │   └── rank by Fisher information
    └── _3pl_probability(theta, a, b, c) <-- 3e
        └── extended IRT with guessing param <-- item_bank_service.py:31
```

**Location ID: 3a**
- **Title:** 2PL probability function
- **Description:** Item Characteristic Curve: P(correct | theta, a, b)
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/modules/diagnostics/irt_engine.py:52

**Location ID: 3b**
- **Title:** Compute IRT probability
- **Description:** Logistic function with discrimination and difficulty parameters
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/modules/diagnostics/irt_engine.py:82

**Location ID: 3c**
- **Title:** Fisher information metric
- **Description:** Measures statistical information item provides about ability
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/modules/diagnostics/irt_engine.py:85

**Location ID: 3d**
- **Title:** Fetch candidate items
- **Description:** Query items in ability neighbourhood with exposure control
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/modules/diagnostics/item_bank_service.py:78

**Location ID: 3e**
- **Title:** 3PL probability variant
- **Description:** Extended IRT model with guessing parameter for item selection
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/modules/diagnostics/item_bank_service.py:30

### AI Guide: IRT Diagnostic Engine

**Overview:** Item Response Theory 2PL adaptive assessment engine calculates learner ability and selects optimal items using Fisher information. This trace shows IRT functions and item selection.

**Key Components:**

1. **2PL probability function (3a):** Item Characteristic Curve. P(correct | theta, a, b). Logistic function.

2. **Compute IRT probability (3b):** Discrimination parameter. Difficulty parameter. Logistic computation.

3. **Fisher information metric (3c):** Statistical information. Ability estimation. Item quality.

4. **Fetch candidate items (3d):** Theta window. Exposure control. Repository query.

5. **3PL probability variant (3e):** Guessing parameter. Extended IRT. Item selection.

**Best Practices:**
- Use IRT for accuracy
- Calibrate parameters
- Control exposure
- Rank by information
- Validate theta estimates
- Protect learner data
- Audit results

**Common Issues:**
- IRT errors: Check parameters
- Selection errors: Check theta
- Repository errors: Check DB
- Calibration issues: Recalibrate
- Exposure issues: Check control

## Trace ID: 4
**Title:** AI Lesson Generation Pipeline (Lessons Module)

**Description:** End-to-end lesson generation with CAPS validation, LLM gateway, PII redaction, schema validation, answer-key verification, and quality scoring.

**Motivation:**
EduBoost V2's lessons module implements end-to-end AI lesson generation with multiple validation phases. The LessonGenerator.generate pipeline starts with CAPS Validation Phase calling get_topic_context(caps_ref) to validate and fetch topic metadata. The Prompt Construction Phase calls _render_generation_prompt() with Jinja2 template.render() to build structured prompt. The LLM Invocation Phase calls _call_llm_with_error_handling() which invokes self._gateway.generate() with Groq primary / Anthropic fallback. The Safety & Parsing Phase calls redact_pii_text(llm_response) and _parse_and_validate_schema() with LessonCreate.model_validate(). The Quality Validation Phase calls self._validator.validate() executing 8 validation rules. The Answer Key Verification Phase calls _verify_answer_key() with second independent LLM call to compare derived vs original. The Quality Scoring Phase calls _compute_quality_score() with weighted correctness + CAPS. The Persistence Phase calls self._repo.create_lesson() with database commit. This comprehensive pipeline ensures CAPS alignment, LLM reliability, PII safety, schema compliance, quality validation, and answer accuracy.

**Details:**
- **Execution Flow:** LessonGenerator.generate → CAPS Validation Phase → get_topic_context(caps_ref) → Prompt Construction Phase → _render_generation_prompt() → Jinja2 template.render() → LLM Invocation Phase → _call_llm_with_error_handling() → self._gateway.generate() → Safety & Parsing Phase → redact_pii_text(llm_response) → _parse_and_validate_schema() → LessonCreate.model_validate() → Quality Validation Phase → self._validator.validate() → 8 validation rules executed → Answer Key Verification Phase → _verify_answer_key() → Second independent LLM call → Compare derived vs original → Quality Scoring Phase → _compute_quality_score() → Weighted: correctness + CAPS → Persistence Phase → self._repo.create_lesson() → Database commit
- **Concurrency Safety:** Generation is per-lesson. LLM calls are sequential. Validation is stateless. Repository operations use transactions. No distributed locks needed
- **Covered Objects:** AI lesson generation, CAPS validation, LLM gateway, PII redaction, schema validation, answer verification, quality scoring
- **Timeouts:** CAPS validation: ~10-50ms. Prompt rendering: ~1-5ms. LLM invocation: ~1-5s. PII redaction: ~10-50ms. Schema validation: ~10-50ms. Quality validation: ~50-200ms. Answer verification: ~1-3s. Quality scoring: ~1-5ms. Persistence: ~10-50ms. Total: ~2.5-8.5s
- **Migration Path:** From simple to comprehensive pipeline. Migration requires: 1) Add CAPS validation, 2) Implement LLM gateway, 3) Add PII redaction, 4) Add validation phases
- **Error Handling:** CAPS errors raised. LLM errors retried. Validation errors logged. Answer verification logged. All errors logged with context. Sensitive data not logged
- **Security Considerations:** Validate CAPS alignment. Redact PII from output. Validate schema. Verify answer keys. Score quality. Protect learner data

**Trace text diagram:**
```
Lesson Generation Pipeline (LessonGenerator.generate) <-- lesson_generator.py:118
├── CAPS Validation Phase
│   └── get_topic_context(caps_ref) <-- 4a
├── Prompt Construction Phase
│   └── _render_generation_prompt() <-- 4b
│       └── Jinja2 template.render() <-- lesson_generator.py:283
├── LLM Invocation Phase
│   └── _call_llm_with_error_handling() <-- 4c
│       └── self._gateway.generate() <-- lesson_generator.py:311
├── Safety & Parsing Phase
│   ├── redact_pii_text(llm_response) <-- 4d
│   └── _parse_and_validate_schema() <-- lesson_generator.py:184
│       └── LessonCreate.model_validate() <-- lesson_generator.py:369
├── Quality Validation Phase
│   └── self._validator.validate() <-- 4e
│       └── 8 validation rules executed
├── Answer Key Verification Phase
│   └── _verify_answer_key() <-- 4f
│       ├── Second independent LLM call <-- lesson_generator.py:417
│       └── Compare derived vs original <-- lesson_generator.py:459
├── Quality Scoring Phase
│   └── _compute_quality_score() <-- lesson_generator.py:217
│       └── Weighted: correctness + CAPS <-- lesson_generator.py:537
└── Persistence Phase
    └── self._repo.create_lesson() <-- 4g
        └── Database commit <-- lesson_generator.py:252
```

**Location ID: 4a**
- **Title:** Resolve CAPS reference
- **Description:** Validate and fetch topic metadata from canonical CAPS map
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/modules/lessons/lesson_generator.py:150

**Location ID: 4b**
- **Title:** Render Jinja2 prompt
- **Description:** Build structured prompt with topic, difficulty, misconceptions
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/modules/lessons/lesson_generator.py:166

**Location ID: 4c**
- **Title:** Call LLM gateway
- **Description:** Invoke Groq primary / Anthropic fallback with retry logic
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/modules/lessons/lesson_generator.py:174

**Location ID: 4d**
- **Title:** Redact PII from output
- **Description:** Safety layer removes personally identifiable information
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/modules/lessons/lesson_generator.py:181

**Location ID: 4e**
- **Title:** Run validation rules
- **Description:** Execute all 8 quality and safety validators
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/modules/lessons/lesson_generator.py:191

**Location ID: 4f**
- **Title:** Verify answer key
- **Description:** Independent second LLM call to validate practice question answers
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/modules/lessons/lesson_generator.py:205

**Location ID: 4g**
- **Title:** Persist lesson
- **Description:** Save validated lesson with metadata to database
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/modules/lessons/lesson_generator.py:251

### AI Guide: AI Lesson Generation Pipeline

**Overview:** End-to-end lesson generation with CAPS validation, LLM gateway, PII redaction, schema validation, answer-key verification, and quality scoring. This trace shows the comprehensive pipeline.

**Key Components:**

1. **Resolve CAPS reference (4a):** Validate topic. Fetch metadata. CAPS alignment.

2. **Render Jinja2 prompt (4b):** Structured prompt. Topic, difficulty. Template rendering.

3. **Call LLM gateway (4c):** Groq primary. Anthropic fallback. Retry logic.

4. **Redact PII from output (4d):** Safety layer. PII removal. Content sanitization.

5. **Run validation rules (4e):** 8 validators. Quality check. Safety check.

6. **Verify answer key (4f):** Second LLM call. Independent verification. Answer accuracy.

7. **Persist lesson (4g):** Database commit. Metadata storage. Lesson record.

**Best Practices:**
- Validate CAPS alignment
- Use LLM fallback
- Redact PII from output
- Validate schema
- Verify answer keys
- Score quality
- Use transactions

**Common Issues:**
- CAPS errors: Check validation
- LLM failures: Check gateway
- PII leakage: Check redaction
- Schema errors: Check validation
- Answer errors: Check verification
- Quality issues: Check scoring

## Trace ID: 5
**Title:** Learner Archetype Profiling (Learners Module)

**Description:** Ether service for psychological archetype classification using Kabbalistic model. Eliminates cold-start lag with 5-question micro-diagnostic.

**Motivation:**
EduBoost V2's learners module implements the Ether service for psychological archetype classification using a Kabbalistic model to eliminate cold-start lag. The cold-start onboarding flow uses a five-question micro-diagnostic covering learning preference, activity type, reward preference, learning style, and self-description. The archetype classification engine uses a scoring matrix lookup mapping (question_id, answer) to scores, and likelihood weights for ten archetypes: Keter (Crown) - reflective, Chokmah (Wisdom) - inquisitive, Binah (Understanding) - analytical, Chesed (Kindness) - collaborative, Gevurah (Strength) - competitive, Tiferet (Beauty) - creative, Netzach (Victory) - visual, Hod (Splendor) - structured, Yesod (Foundation) - hands-on, and Malkuth (Kingdom) - practical. The engine aggregates scores across answers and uses LLM prompt tone modifiers to personalize lesson content by archetype. This psychological profiling enables personalized learning experiences from the first session.

**Details:**
- **Execution Flow:** Cold-start onboarding flow → Five-question micro-diagnostic → Question 1: Learning preference → Question 2: Activity type → Question 3: Reward preference → Question 4: Learning style → Question 5: Self-description → Answer collection → [(q_id, answer), ...] → Archetype classification engine → Scoring matrix lookup → (question_id, answer) → scores → Likelihood weights → Keter (Crown) - reflective → Chokmah (Wisdom) - inquisitive → Binah (Understanding) - analytical → Chesed (Kindness) - collaborative → Gevurah (Strength) - competitive → Tiferet (Beauty) - creative → Netzach (Victory) - visual → Hod (Splendor) - structured → Yesod (Foundation) - hands-on → Malkuth (Kingdom) - practical → Aggregate scores across answers → LLM prompt tone modifiers → Personalize lesson content by archetype
- **Concurrency Safety:** Classification is per-learner. Scoring is deterministic. Aggregation is stateless. No distributed locks needed
- **Covered Objects:** Learner profiling, archetype classification, Kabbalistic model, cold-start elimination, personalization
- **Timeouts:** Diagnostic collection: ~10-50ms. Scoring: ~1-5ms. Aggregation: ~1-5ms. Total: ~12-60ms
- **Migration Path:** From generic to personalized. Migration requires: 1) Implement diagnostic, 2) Add scoring matrix, 3) Add archetype weights, 4) Update LLM prompts
- **Error Handling:** Diagnostic errors logged. Scoring errors logged. Aggregation errors logged. All errors logged with context. Sensitive data not logged
- **Security Considerations:** Validate diagnostic answers. Protect learner data. Audit classification results. Validate archetype assignment. Filter sensitive data

**Trace text diagram:**
```
Learner Archetype Profiling (Ether Service)
├── Cold-start onboarding flow
│   ├── Five-question micro-diagnostic <-- 5a
│   │   ├── Question 1: Learning preference <-- ether_service.py:37
│   │   ├── Question 2: Activity type <-- ether_service.py:47
│   │   ├── Question 3: Reward preference <-- ether_service.py:57
│   │   ├── Question 4: Learning style <-- ether_service.py:67
│   │   └── Question 5: Self-description <-- ether_service.py:77
│   └── Answer collection
│       └── [(q_id, answer), ...]
├── Archetype classification engine
│   ├── Scoring matrix lookup <-- 5b
│   │   └── (question_id, answer) → scores
│   ├── Likelihood weights <-- 5c
│   │   ├── Keter (Crown) - reflective <-- ether_service.py:94
│   │   ├── Chokmah (Wisdom) - inquisitive <-- ether_service.py:95
│   │   ├── Binah (Understanding) - analytical <-- ether_service.py:98
│   │   ├── Chesed (Kindness) - collaborative <-- ether_service.py:95
│   │   ├── Gevurah (Strength) - competitive <-- ether_service.py:97
│   │   ├── Tiferet (Beauty) - creative <-- ether_service.py:100
│   │   ├── Netzach (Victory) - visual <-- ether_service.py:96
│   │   ├── Hod (Splendor) - structured <-- ether_service.py:96
│   │   ├── Yesod (Foundation) - hands-on <-- ether_service.py:97
│   │   └── Malkuth (Kingdom) - practical <-- ether_service.py:99
│   └── Aggregate scores across answers
└── LLM prompt tone modifiers
    └── Personalize lesson content by archetype
```

**Location ID: 5a**
- **Title:** Onboarding questions
- **Description:** Five-question micro-diagnostic for first-session classification
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/modules/learners/ether_service.py:34

**Location ID: 5b**
- **Title:** Scoring matrix
- **Description:** Maps (question_id, answer) to archetype likelihood scores
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/modules/learners/ether_service.py:93

**Location ID: 5c**
- **Title:** Archetype weights
- **Description:** Likelihood scores for Kabbalistic archetype classification
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/modules/learners/ether_service.py:94

### AI Guide: Learner Archetype Profiling

**Overview:** Ether service for psychological archetype classification using Kabbalistic model eliminates cold-start lag with 5-question micro-diagnostic. This trace shows classification and personalization.

**Key Components:**

1. **Onboarding questions (5a):** Five-question diagnostic. Learning preference. Activity type.

2. **Scoring matrix (5b):** Answer mapping. Likelihood scores. Classification logic.

3. **Archetype weights (5c):** Kabbalistic model. Ten archetypes. Likelihood scores.

**Best Practices:**
- Use micro-diagnostic
- Score answers accurately
- Aggregate scores properly
- Personalize content
- Validate classification
- Protect learner data
- Audit results

**Common Issues:**
- Diagnostic errors: Check questions
- Scoring errors: Check matrix
- Classification errors: Check weights
- Personalization issues: Check prompts
- Data errors: Validate inputs

## Trace ID: 6
**Title:** Adaptive Practice Selection (Practice Module)

**Description:** Practice generator selecting items based on diagnostic gaps, IRT ability, and exposure control for spaced repetition.

**Motivation:**
EduBoost V2's practice module implements adaptive practice selection with spaced repetition. The PracticeGenerator.select_items() method initializes served_ids set and for each gap_topic in gap_topics, filters candidates by criteria: match caps_ref to gap, exclude served_ids, check theta window (±0.5), and verify review_status == "approved". It sorts by difficulty match and selects top per_gap items. The SpacedRepetitionScheduler.update_schedule() implements SM-2 variant: if incorrect, interval=1 and reduce EF; if first review, interval=1; if second review, interval=3 and boost EF; else, interval *= EF and cap EF at 3.0. This adaptive approach provides gap-targeted practice, difficulty matching, exposure control, and spaced repetition for optimal learning.

**Details:**
- **Execution Flow:** PracticeGenerator.select_items() → Initialize served_ids set → For each gap_topic in gap_topics → Filter candidates by criteria → Match caps_ref to gap → Exclude served_ids → Check theta window (±0.5) → Verify review_status == "approved" → Sort by difficulty match → Select top per_gap items → Return selected items list → SpacedRepetitionScheduler → update_schedule() → If incorrect: interval=1, reduce EF → If first review: interval=1 → If second review: interval=3, boost EF → Else: interval *= EF, cap EF at 3.0
- **Concurrency Safety:** Selection is per-learner. Scheduling is per-item. Repository operations use transactions. No distributed locks needed
- **Covered Objects:** Adaptive practice, gap targeting, IRT matching, exposure control, spaced repetition
- **Timeouts:** Item selection: ~10-50ms. Filtering: ~10-50ms. Sorting: ~1-5ms. Scheduling: ~1-5ms. Total: ~22-110ms
- **Migration Path:** From static to adaptive practice. Migration requires: 1) Implement gap targeting, 2) Add IRT matching, 3) Add exposure control, 4) Implement spaced repetition
- **Error Handling:** Selection errors logged. Filtering errors logged. Scheduling errors logged. All errors logged with context. Sensitive data not logged
- **Security Considerations:** Validate gap data. Protect learner data. Audit practice results. Validate theta estimates. Filter sensitive data

**Trace text diagram:**
```
Adaptive Practice Selection Pipeline
├── PracticeGenerator.select_items() <-- 6a
│   ├── Initialize served_ids set <-- practice_generator.py:18
│   ├── For each gap_topic in gap_topics <-- practice_generator.py:20
│   │   ├── Filter candidates by criteria <-- 6b
│   │   │   ├── Match caps_ref to gap <-- practice_generator.py:23
│   │   │   ├── Exclude served_ids <-- practice_generator.py:24
│   │   │   ├── Check theta window (±0.5) <-- practice_generator.py:25
│   │   │   └── Verify review_status == "approved" <-- practice_generator.py:26
│   │   ├── Sort by difficulty match <-- 6c
│   │   └── Select top per_gap items <-- practice_generator.py:29
│   └── Return selected items list <-- practice_generator.py:30
│
└── SpacedRepetitionScheduler
    └── update_schedule() <-- 6d
        ├── If incorrect: interval=1, reduce EF <-- spaced_repetition_scheduler.py:18
        ├── If first review: interval=1 <-- spaced_repetition_scheduler.py:21
        ├── If second review: interval=3, boost EF <-- spaced_repetition_scheduler.py:24
        └── Else: interval *= EF, cap EF at 3.0 <-- spaced_repetition_scheduler.py:27
```

**Location ID: 6a**
- **Title:** Select practice items
- **Description:** Adaptive selection from gaps with theta-based difficulty matching
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/modules/practice/practice_generator.py:9

**Location ID: 6b**
- **Title:** Filter candidates
- **Description:** Match items to gap topics, theta window, and approval status
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/modules/practice/practice_generator.py:21

**Location ID: 6c**
- **Title:** Sort by difficulty match
- **Description:** Rank items by proximity to learner ability estimate
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/modules/practice/practice_generator.py:28

**Location ID: 6d**
- **Title:** Update review schedule
- **Description:** SM-2 variant for spaced repetition intervals
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/modules/practice/spaced_repetition_scheduler.py:17

### AI Guide: Adaptive Practice Selection

**Overview:** Practice generator selecting items based on diagnostic gaps, IRT ability, and exposure control for spaced repetition. This trace shows adaptive selection and scheduling.

**Key Components:**

1. **Select practice items (6a):** Adaptive selection. Gap targeting. Theta matching.

2. **Filter candidates (6b):** Match caps_ref. Exclude served. Theta window. Approval status.

3. **Sort by difficulty match (6c):** Rank by proximity. Ability estimate. Difficulty matching.

4. **Update review schedule (6d):** SM-2 variant. Spaced repetition. Interval calculation.

**Best Practices:**
- Target diagnostic gaps
- Match IRT ability
- Control exposure
- Use spaced repetition
- Validate theta estimates
- Protect learner data
- Audit practice results

**Common Issues:**
- Selection errors: Check filtering
- Theta errors: Check estimates
- Exposure issues: Check control
- Scheduling errors: Check SM-2
- Gap errors: Validate data

## Trace ID: 7
**Title:** Mastery Model Computation (Progress Module)

**Description:** Progress tracking with IRT-based mastery scoring, learning velocity, and risk signals for intervention.

**Motivation:**
EduBoost V2's progress module implements comprehensive mastery tracking with IRT-based scoring. The IRT Ability → Mastery Conversion uses theta_to_mastery() with erf(theta / sqrt(2)) normalization to transform ability to 0-1 mastery score. The Composite Mastery Score Calculation uses compute_mastery_score() with weighted components: mastery_theta (from IRT), practice_accuracy component, recency_days decay, consistency_ratio component, confidence (from SE), and weighted sum (40/25/15/10/10). The Learning Analytics Service includes Learning Velocity Tracking with compute_velocity() calculating delta_mastery / weeks_elapsed, Risk Signal Classification with compute_risk_signal() classifying as urgent (score<0.4 OR idle>30d), at_risk (score<0.6 OR idle>14d), or on_track (otherwise), and Next Best Activities ranked by priority & mastery score. This comprehensive tracking provides accurate mastery measurement, learning velocity, risk identification, and intervention guidance.

**Details:**
- **Execution Flow:** IRT Ability → Mastery Conversion → theta_to_mastery() → erf(theta / sqrt(2)) normalization → Composite Mastery Score Calculation → compute_mastery_score() → mastery_theta (from IRT) → practice_accuracy component → recency_days decay → consistency_ratio component → confidence (from SE) → weighted sum (40/25/15/10/10) → Learning Analytics Service → Learning Velocity Tracking → compute_velocity() → delta_mastery / weeks_elapsed → Risk Signal Classification → compute_risk_signal() → urgent: score<0.4 OR idle>30d → at_risk: score<0.6 OR idle>14d → on_track: otherwise → Next Best Activities → ranked by priority & mastery score
- **Concurrency Safety:** Mastery calculation is deterministic. Velocity calculation is stateless. Risk classification is deterministic. No distributed locks needed
- **Covered Objects:** Mastery tracking, IRT conversion, learning velocity, risk signals, intervention guidance
- **Timeouts:** Theta conversion: ~1-5ms. Composite score: ~1-5ms. Velocity calculation: ~1-5ms. Risk classification: ~1-5ms. Total: ~4-20ms
- **Migration Path:** From simple to comprehensive tracking. Migration requires: 1) Implement IRT conversion, 2) Add composite scoring, 3) Add velocity tracking, 4) Add risk classification
- **Error Handling:** Conversion errors logged. Scoring errors logged. Velocity errors logged. Risk errors logged. All errors logged with context. Sensitive data not logged
- **Security Considerations:** Validate theta estimates. Protect learner data. Audit mastery results. Validate risk signals. Filter sensitive data

**Trace text diagram:**
```
Progress Tracking & Mastery Model
├── IRT Ability → Mastery Conversion
│   └── theta_to_mastery() <-- 7a
│       └── erf(theta / sqrt(2)) normalization <-- mastery_model.py:16
├── Composite Mastery Score Calculation
│   └── compute_mastery_score() <-- 7b
│       ├── mastery_theta (from IRT) <-- mastery_model.py:38
│       ├── practice_accuracy component <-- mastery_model.py:39
│       ├── recency_days decay <-- mastery_model.py:40
│       ├── consistency_ratio component <-- mastery_model.py:41
│       ├── confidence (from SE) <-- mastery_model.py:42
│       └── weighted sum (40/25/15/10/10) <-- 7c
└── Learning Analytics Service
    ├── Learning Velocity Tracking
    │   └── compute_velocity() <-- 7d
    │       └── delta_mastery / weeks_elapsed <-- learning_velocity_service.py:15
    ├── Risk Signal Classification
    │   └── compute_risk_signal() <-- 7e
    │       ├── urgent: score<0.4 OR idle>30d <-- learning_velocity_service.py:18
    │       ├── at_risk: score<0.6 OR idle>14d <-- learning_velocity_service.py:20
    │       └── on_track: otherwise <-- learning_velocity_service.py:22
    └── Next Best Activities <-- learning_velocity_service.py:24
        └── ranked by priority & mastery score <-- learning_velocity_service.py:42
```

**Location ID: 7a**
- **Title:** Convert theta to mastery
- **Description:** Transform IRT ability to 0-1 mastery score using error function
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/modules/progress/mastery_model.py:15

**Location ID: 7b**
- **Title:** Compute composite score
- **Description:** Weighted combination of theta, practice, recency, consistency
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/modules/progress/mastery_model.py:31

**Location ID: 7c**
- **Title:** Weight mastery dimensions
- **Description:** 40% ability, 25% practice, 15% recency, 10% consistency, 10% confidence
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/modules/progress/mastery_model.py:43

**Location ID: 7d**
- **Title:** Compute learning velocity
- **Description:** Rate of mastery change per week from snapshot history
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/modules/progress/learning_velocity_service.py:8

**Location ID: 7e**
- **Title:** Compute risk signal
- **Description:** Classify learner as urgent, at_risk, or on_track for intervention
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/modules/progress/learning_velocity_service.py:17

### AI Guide: Mastery Model Computation

**Overview:** Progress tracking with IRT-based mastery scoring, learning velocity, and risk signals for intervention. This trace shows mastery conversion, composite scoring, and risk classification.

**Key Components:**

1. **Convert theta to mastery (7a):** IRT ability. Error function. 0-1 mastery.

2. **Compute composite score (7b):** Weighted combination. Multiple dimensions. Comprehensive scoring.

3. **Weight mastery dimensions (7c):** 40% ability. 25% practice. 15% recency. 10% consistency. 10% confidence.

4. **Compute learning velocity (7d):** Delta mastery. Weeks elapsed. Rate of change.

5. **Compute risk signal (7e):** Urgent classification. At-risk detection. On-track status.

**Best Practices:**
- Use IRT for accuracy
- Weight dimensions appropriately
- Track learning velocity
- Classify risk accurately
- Validate theta estimates
- Protect learner data
- Audit results

**Common Issues:**
- Conversion errors: Check theta
- Scoring errors: Check weights
- Velocity errors: Check snapshots
- Risk errors: Check thresholds
- Data errors: Validate inputs

## Trace ID: 8
**Title:** Background Job Execution (Jobs Module)

**Description:** ARQ async worker for consent reminders, RLHF batch processing, diagnostic session expiry, and database backups with Prometheus metrics.

**Motivation:**
EduBoost V2's jobs module implements ARQ async worker for background job execution. The WorkerSettings Configuration includes functions registry and cron_jobs schedule with Daily 00:00 UTC: run_database_backup, Daily 06:00 UTC: consent reminders, and Hourly: expire_stale_diagnostic_sessions. The Consent Renewal Job (Daily 08:00 SAST) calls send_consent_renewal_reminders() and run_consent_reminder_cycle() which queries expiring consents, decrypts guardian emails, and sends SendGrid notifications. The Diagnostic Session Expiry (Hourly) calls expire_stale_diagnostic_sessions(), calculates 24h cutoff timestamp, UPDATEs DiagnosticSession WHERE..., and increments Prometheus metrics. The Database Backup Job (Daily 00:00 UTC) calls run_database_backup(), prepares environment with encryption key, executes scripts/backup_postgres.sh, and returns status + output tail. This background job system ensures automated maintenance, compliance reminders, session cleanup, and data protection.

**Details:**
- **Execution Flow:** WorkerSettings Configuration → functions registry → cron_jobs schedule → Daily 00:00 UTC: run_database_backup → Daily 06:00 UTC: consent reminders → Hourly: expire_stale_diagnostic_sessions → Consent Renewal Job (Daily 08:00 SAST) → send_consent_renewal_reminders() → run_consent_reminder_cycle() → Query expiring consents → Decrypt guardian emails → Send SendGrid notifications → Diagnostic Session Expiry (Hourly) → expire_stale_diagnostic_sessions() → Calculate 24h cutoff timestamp → UPDATE DiagnosticSession WHERE... → Increment Prometheus metrics → Database Backup Job (Daily 00:00 UTC) → run_database_backup() → Prepare environment with encryption key → Execute scripts/backup_postgres.sh → Return status + output tail
- **Concurrency Safety:** Jobs are scheduled independently. Database operations use transactions. No distributed locks needed
- **Covered Objects:** Background jobs, ARQ worker, consent reminders, session expiry, database backups, Prometheus metrics
- **Timeouts:** Consent reminders: ~1-5min. Session expiry: ~10-50ms. Database backup: ~5-30min. Total: ~6-35min
- **Migration Path:** From manual to automated jobs. Migration requires: 1) Implement ARQ worker, 2) Add cron schedules, 3) Implement job functions, 4) Add metrics
- **Error Handling:** Job failures logged. Decryption errors logged. Email errors logged. Backup errors logged. All errors logged with context. Sensitive data not logged
- **Security Considerations:** Validate job payloads. Encrypt backups. Secure email sending. Audit job execution. Protect sensitive data. Validate cron schedules

**Trace text diagram:**
```
ARQ Background Job System
├── WorkerSettings Configuration <-- jobs.py:263
│   ├── functions registry <-- 8f
│   └── cron_jobs schedule <-- jobs.py:285
│       ├── Daily 00:00 UTC: run_database_backup <-- jobs.py:287
│       ├── Daily 06:00 UTC: consent reminders <-- jobs.py:289
│       └── Hourly: expire_stale_diagnostic_sessions <-- jobs.py:291
│
├── Consent Renewal Job (Daily 08:00 SAST)
│   ├── send_consent_renewal_reminders() <-- 8a
│   └── run_consent_reminder_cycle() <-- 8b
│       ├── Query expiring consents <-- jobs.py:48
│       ├── Decrypt guardian emails <-- jobs.py:226
│       └── Send SendGrid notifications <-- jobs.py:240
│
├── Diagnostic Session Expiry (Hourly)
│   ├── expire_stale_diagnostic_sessions() <-- 8c
│   ├── Calculate 24h cutoff timestamp <-- jobs.py:111
│   ├── UPDATE DiagnosticSession WHERE... <-- 8d
│   └── Increment Prometheus metrics <-- jobs.py:124
│
└── Database Backup Job (Daily 00:00 UTC)
    ├── run_database_backup() <-- 8e
    ├── Prepare environment with encryption key <-- jobs.py:164
    ├── Execute scripts/backup_postgres.sh <-- jobs.py:175
    └── Return status + output tail <-- jobs.py:187
```

**Location ID: 8a**
- **Title:** Consent reminder job
- **Description:** Daily cron at 08:00 SAST for expiring consent notifications
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/modules/jobs.py:46

**Location ID: 8b**
- **Title:** Execute reminder cycle
- **Description:** Process expiring consents and send guardian emails
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/modules/jobs.py:48

**Location ID: 8c**
- **Title:** Expire diagnostic sessions
- **Description:** Hourly job marks incomplete sessions older than 24h as abandoned
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/modules/jobs.py:85

**Location ID: 8d**
- **Title:** Update stale sessions
- **Description:** Bulk update DiagnosticSession records past cutoff timestamp
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/modules/jobs.py:113

**Location ID: 8e**
- **Title:** Database backup job
- **Description:** Daily encrypted PostgreSQL backup at 00:00 UTC
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/modules/jobs.py:134

**Location ID: 8f**
- **Title:** Register worker functions
- **Description:** ARQ WorkerSettings with job registry and cron schedules
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/modules/jobs.py:278

### AI Guide: Background Job Execution

**Overview:** ARQ async worker for consent reminders, RLHF batch processing, diagnostic session expiry, and database backups with Prometheus metrics. This trace shows job configuration and execution.

**Key Components:**

1. **Consent reminder job (8a):** Daily cron. Expiring consents. SendGrid notifications.

2. **Execute reminder cycle (8b):** Query consents. Decrypt emails. Send notifications.

3. **Expire diagnostic sessions (8c):** Hourly job. 24h cutoff. Session cleanup.

4. **Update stale sessions (8d):** Bulk update. Cutoff timestamp. Database operation.

5. **Database backup job (8e):** Daily backup. Encryption key. Shell script.

6. **Register worker functions (8f):** ARQ WorkerSettings. Job registry. Cron schedules.

**Best Practices:**
- Use ARQ for scheduling
- Encrypt backups
- Secure email sending
- Audit job execution
- Use Prometheus metrics
- Validate job payloads
- Handle failures gracefully

**Common Issues:**
- Job failures: Check logs
- Decryption errors: Check keys
- Email errors: Check SendGrid
- Backup errors: Check script
- Cron errors: Check schedule

## Trace ID: 9
**Title:** Module Integration with API (Router Registration)

**Description:** FastAPI application integrates modules via routers. Shows how domain modules expose HTTP endpoints through the V2 API.

**Motivation:**
EduBoost V2's modular architecture integrates domain modules with the FastAPI application via routers. The FastAPI Application (api_v2.py) imports module routers from app.modules.practice and app.api_v2_routers including lessons and diagnostics. The Router Registry maps module names to router instances with ("lessons", lessons.router), ("diagnostics", diagnostics.router), and ("practice", practice_router.router). The app.include_router() is called for each module. The Lessons Router imports LessonService, defines POST /lessons/generate endpoint with consent gate check, and calls service.generate_lesson_for_learner() with LessonService dependency injection. The Diagnostics Router imports ItemBankService. The LessonService.__init__() dependencies include ExecutiveService, LessonRepository, and ConsentService(db) for cross-module consent enforcement. This modular integration enables clean separation of concerns, dependency injection, and cross-module collaboration.

**Details:**
- **Execution Flow:** FastAPI Application (api_v2.py) → Module imports → from app.modules.practice import router → from app.api_v2_routers import lessons → from app.api_v2_routers import diagnostics → Router registry → ("lessons", lessons.router) → ("diagnostics", diagnostics.router) → ("practice", practice_router.router) → app.include_router() for each module → Lessons Router (api_v2_routers/lessons.py) → Import LessonService → POST /lessons/generate endpoint → Consent gate check → service.generate_lesson_for_learner() → LessonService dependency injection → Diagnostics Router (api_v2_routers/diagnostics.py) → Import ItemBankService → LessonService (modules/lessons/service.py) → __init__() dependencies → ExecutiveService → LessonRepository → ConsentService(db) → generate_lesson_for_learner() → Cross-module consent enforcement
- **Concurrency Safety:** Router registration is at startup. Dependency injection is per-request. Cross-module calls are synchronous. No distributed locks needed
- **Covered Objects:** Module integration, router registration, dependency injection, cross-module collaboration, consent enforcement
- **Timeouts:** Router registration: ~10-50ms. Dependency injection: ~1-5ms. Cross-module calls: ~10-50ms. Total: ~21-105ms
- **Migration Path:** From monolithic to modular. Migration requires: 1) Extract modules, 2) Create routers, 3) Register routers, 4) Wire dependencies
- **Error Handling:** Registration errors logged. Dependency errors logged. Cross-module errors logged. All errors logged with context. Sensitive data not logged
- **Security Considerations:** Validate router registration. Secure dependency injection. Enforce consent gates. Validate cross-module calls. Protect module boundaries

**Trace text diagram:**
```
FastAPI Application (api_v2.py)
├── Module imports <-- 9a
│   ├── from app.modules.practice import router
│   ├── from app.api_v2_routers import lessons <-- api_v2.py:239
│   └── from app.api_v2_routers import diagnostics <-- api_v2.py:239
├── Router registry <-- 9b
│   ├── ("lessons", lessons.router) <-- api_v2.py:270
│   ├── ("diagnostics", diagnostics.router) <-- api_v2.py:272
│   └── ("practice", practice_router.router) <-- api_v2.py:273
└── app.include_router() for each module

Lessons Router (api_v2_routers/lessons.py)
├── Import LessonService <-- 9c
├── POST /lessons/generate endpoint <-- lessons.py:30
│   ├── Consent gate check <-- lessons.py:42
│   └── service.generate_lesson_for_learner() <-- 9d
└── LessonService dependency injection <-- lessons.py:27

Diagnostics Router (api_v2_routers/diagnostics.py)
└── Import ItemBankService <-- 9e

LessonService (modules/lessons/service.py)
├── __init__() dependencies <-- service.py:67
│   ├── ExecutiveService <-- service.py:79
│   ├── LessonRepository <-- service.py:80
│   └── ConsentService(db) <-- 9f
└── generate_lesson_for_learner() <-- service.py:86
    └── Cross-module consent enforcement
```

**Location ID: 9a**
- **Title:** Import module routers
- **Description:** Load routers from modules and api_v2_routers packages
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/api_v2.py:238

**Location ID: 9b**
- **Title:** Router registry
- **Description:** Central registry mapping module names to router instances
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/api_v2.py:264

**Location ID: 9c**
- **Title:** Import lesson service
- **Description:** Router depends on module service for business logic
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/api_v2_routers/lessons.py:18

**Location ID: 9d**
- **Title:** Invoke service method
- **Description:** Router delegates to LessonService for lesson generation
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/api_v2_routers/lessons.py:45

**Location ID: 9e**
- **Title:** Import diagnostic services
- **Description:** Diagnostics router uses IRT engine and item bank service
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/api_v2_routers/diagnostics.py:21

**Location ID: 9f**
- **Title:** Cross-module dependency
- **Description:** LessonService depends on ConsentService for POPIA gate
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/modules/lessons/service.py:83

### AI Guide: Module Integration with API

**Overview:** FastAPI application integrates modules via routers, showing how domain modules expose HTTP endpoints through the V2 API. This trace shows router registration and dependency injection.

**Key Components:**

1. **Import module routers (9a):** Load routers. Modules package. API routers.

2. **Router registry (9b):** Central registry. Module mapping. Router instances.

3. **Import lesson service (9c):** Service dependency. Business logic. Module integration.

4. **Invoke service method (9d):** Router delegation. Service call. Cross-module.

5. **Import diagnostic services (9e):** IRT engine. Item bank service. Module services.

6. **Cross-module dependency (9f):** ConsentService. POPIA gate. Dependency injection.

**Best Practices:**
- Use router registry
- Inject dependencies
- Enforce consent gates
- Validate module boundaries
- Secure cross-module calls
- Use dependency injection
- Audit router registration

**Common Issues:**
- Registration errors: Check imports
- Dependency errors: Check injection
- Consent errors: Check gates
- Cross-module errors: Check calls
- Boundary violations: Validate modules
