# Codemaps Documentation

This directory contains codemaps that document the architecture and implementation of EduBoost V2 systems. Codemaps provide detailed traces through codebases, showing execution flows, component relationships, and technical details.

## Codemap Structure

Each codemap file follows a standardized structure to ensure consistency and readability:

### File Format
- **File Extension:** `.md` (Markdown)
- **Naming Convention:** `snake_case_with_underscores.md` (e.g., `jwt_security_implementation_dual_system_architecture.md`)

### Document Structure

#### 1. Title and Overview
```markdown
# [System Name]

[Brief description of the system, key components, and notable entry points]
```

#### 2. Trace Sections
Each codemap contains one or more traces. Each trace represents a specific execution flow or aspect of the system.

##### Trace Header
```markdown
## Trace ID: [number]
**Title:** [Descriptive title]

**Description:** [Concise description of what this trace covers]
```

##### Motivation Section
```markdown
**Motivation:**
[Paragraph explaining the purpose and rationale for this system/component]
```

##### Details Section
```markdown
**Details:**
- **Execution Flow:** [Step-by-step flow of execution]
- **Concurrency Safety:** [Thread safety, locks, race conditions]
- **Covered Objects:** [Objects, files, components covered]
- **Timeouts:** [Timing information for operations]
- **Migration Path:** [Steps to migrate from old to new system]
- **Error Handling:** [How errors are handled]
- **Security Considerations:** [Security-related considerations]
```

##### Trace Text Diagram
```markdown
**Trace text diagram:**
```
[ASCII diagram showing the flow]
```
```

##### Location IDs
```markdown
**Location ID: [letter][number]**
- **Title:** [Descriptive title]
- **Description:** [What this location represents]
- **Path:LineNumber:** [/absolute/path/to/file:line_number]
```

##### AI Guide Section
```markdown
### AI Guide: [Trace Title]

**Overview:** [High-level overview of the trace]

[Additional sections as needed: Flow Components, Security Features, Best Practices, etc.]
```

### Required Sections

Every trace MUST include:
1. **Title** - Descriptive name
2. **Description** - What the trace covers
3. **Motivation** - Why this system/component exists
4. **Details** - Technical details with all subsections
5. **Trace text diagram** - ASCII diagram of the flow
6. **Location IDs** - Code references with paths and line numbers
7. **AI Guide** - Comprehensive guide for understanding the trace

### Optional Sections

The following may be added as needed:
- **Overview** (in AI Guide)
- **Flow Components** (in AI Guide)
- **Security Features** (in AI Guide)
- **Best Practices** (in AI Guide)
- **Common Issues** (in AI Guide)
- **Code Examples** (in AI Guide)

## Existing Codemaps

### 1. Pytest Configuration and Test Suite Structure
- **File:** `pytest_configuration_and_test_suite_structure.md`
- **Description:** Maps pytest configuration from pytest.ini through test discovery, fixture hierarchy, coverage reporting, and CI execution
- **Traces:** 7 traces covering pytest initialization, test categorization, database fixtures, coverage measurement, CI workflows, Playwright E2E configuration, and module-specific fixtures
- **Key Components:** pytest.ini, conftest.py files, pytest-cov, GitHub Actions workflows, Playwright configuration

### 2. JWT Security Implementation: Dual-System Architecture
- **File:** `jwt_security_implementation_dual_system_architecture.md`
- **Description:** Documents JWT security implementation with dual-system architecture (primary system with JWT-based refresh tokens, alternative system with opaque refresh tokens)
- **Traces:** 8 traces covering login flow, access token creation, token verification, refresh token rotation, key rotation, token revocation, opaque refresh tokens, and password security
- **Key Components:** security.py, jwt_keyring.py, token_revocation.py, refresh_tokens.py, token_config.py, password.py, auth_service.py

### 3. Content Factory Full Generation System: Overnight Batch Pipeline
- **File:** `content_factory_full_generation_system_overnight_batch_pipeline.md`
- **Description:** End-to-end overnight batch generation pipeline that orchestrates content creation from planning through review submission
- **Traces:** 8 traces covering overnight run orchestration, content gap planning, task execution, diagnostic item generation, artifact creation and validation, staging readiness verification, staging seed execution, and report generation
- **Key Components:** run_full_generation.py, content_generation_planner.py, content_generation_executor.py, deterministic.py, content_factory.py, content_staging_readiness.py, content_staging_seed_executor.py, content_generation_reporter.py

### 4. Alembic Migration and DDL Management: Startup DDL Repairs, Migration Integrity, and Alembic Workflow
- **File:** `alembic_migration_and_ddl_management_startup_ddl_repairs_migration_integrity_and_alembic_workflow.md`
- **Description:** Database schema management through Alembic migrations and transitional startup DDL repairs with single-head linear migration graph, CI enforcement, and runtime health checks
- **Traces:** 8 traces covering startup DDL repair execution, Alembic migration execution, migration integrity CI validation, runtime migration health check, migration graph static validation, schema integrity ORM validation, migration smoke test workflow, and ADR-002 startup DDL deprecation plan
- **Key Components:** api_v2.py, alembic/env.py, migration_check.yml, health.py, verify_migration_graph.py, validate_schema_integrity.py, smoke_test_migrations.sh, ADR-002

### 5. JWT Security Implementation and Token Management
- **File:** `jwt_security_implementation_and_token_management.md`
- **Description:** JWT authentication system with dual-token architecture: short-lived access tokens (15 min) and single-use refresh tokens with family-based rotation, kid-based key rotation, Redis-backed token storage, multi-layer revocation, and canonical claims building
- **Traces:** 8 traces covering login flow, access token creation with keyring, token verification with revocation, refresh token rotation, building canonical access token claims, refresh token storage, JWT keyring validation, and token revocation
- **Key Components:** auth.py, auth_lifecycle_impl.py, security.py, jwt_keyring.py, refresh_tokens.py, token_revocation.py, auth_token_claims.py

### 6. Coverage Debt Management and Recovery System
- **File:** `coverage_debt_management_and_recovery_system.md`
- **Description:** Coverage debt management system from configuration through measurement, tracking, risk classification, and recovery planning with async-aware coverage, CI threshold enforcement, baseline measurement, module risk classification, quick-win test opportunities, and recovery sprint plan
- **Traces:** 7 traces covering coverage configuration and timeout resolution, CI coverage threshold enforcement, coverage baseline measurement and module breakdown, module risk classification and priority assignment, quick-win test opportunities and coverage impact, recovery sprint plan execution roadmap, and coverage exemptions and quality thresholds
- **Key Components:** .coveragerc, pytest.ini, ci-cd.yml, coverage_baseline_20260527.md, coverage_debt.md, coverage_quality_threshold_contract.md

### 7. EduBoost V2 Service Layer Architecture
- **File:** `eduboost_v2_service_layer_architecture.md`
- **Description:** Service layer implementing business logic across authentication, content generation, diagnostic assessments, POPIA compliance, and LLM orchestration with password verification, lockout checks, token issuance, artifact validation, IRT-based adaptive assessment, data subject rights, provider fallback, and quota control
- **Traces:** 8 traces covering user authentication flow, content artifact creation & validation, diagnostic session lifecycle, POPIA data export request, LLM gateway with fallback, content generation execution, consent lifecycle management, and lesson generation with quota control
- **Key Components:** auth_service.py, content_factory.py, diagnostic_session_service.py, popia_service.py, gateway.py, content_generation_executor.py, consent_service.py, lesson_service_v2.py

### 8. Base Repository Implementation: Generic Async CRUD & Database Interactions
- **File:** `base_repository_implementation_generic_async_crud_database_interactions.md`
- **Description:** Async repository pattern from database engine initialization through generic BaseRepository CRUD operations to concrete domain repositories and FastAPI integration with SQLAlchemy 2.0, asyncpg driver, connection pooling, session factory, declarative base, dependency injection, transaction management, and exception handling
- **Traces:** 8 traces covering database engine & session factory initialization, generic BaseRepository CRUD operations, concrete repository implementation pattern, FastAPI session lifecycle & transaction management, repository usage in API endpoint, ORM model to repository connection, advanced repository pattern (ItemBankRepository), and exception handling & error responses
- **Key Components:** database.py, base.py, repositories.py, auth_repository.py, item_bank_repository.py, exceptions.py, learners.py

### 9. API Documentation Structure: Sphinx & MkDocs Generation Pipeline
- **File:** `api_documentation_structure_sphinx_mkdocs_generation_pipeline.md`
- **Description:** Two parallel documentation systems: Sphinx generates comprehensive HTML API reference from Python docstrings with autodoc, napoleon, and viewcode extensions, while MkDocs builds a Material-themed operational docs site with mkdocstrings plugin for inline API references
- **Traces:** 6 traces covering Sphinx API documentation build flow, MkDocs site generation with mkdocstrings, Python docstring to HTML rendering, documentation inventory generation, CI documentation build pipeline, and navigation structure assembly in Sphinx
- **Key Components:** conf.py, index.rst, mkdocs.yml, docs_inventory.py, ci-cd.yml, Makefile, irt_engine.py

## Creating New Codemaps

When creating a new codemap:

1. **Choose a System:** Identify a system or component that needs documentation
2. **Define Traces:** Break down the system into logical execution flows or aspects
3. **Follow Structure:** Use the standardized structure outlined above
4. **Add Motivation:** Explain why each component exists
5. **Provide Details:** Include all required subsections in the Details section
6. **Create Diagrams:** Use ASCII diagrams to visualize flows
7. **Reference Code:** Include accurate file paths and line numbers
8. **Write AI Guides:** Provide comprehensive guides for each trace

## Codemap Purpose

Codemaps serve as:
- **Architecture Documentation:** Deep technical documentation of system implementation
- **Onboarding Resource:** Help new developers understand complex systems
- **Reference Material:** Quick reference for implementation details
- **Agent Knowledge Base:** Provide structured information for AI agents to understand and work with the codebase
- **Change Tracking:** Document architectural decisions and their rationale

## Maintenance

- Keep codemaps up to date with code changes
- Update line numbers when code is modified
- Add new traces when systems evolve
- Review and improve AI guides based on feedback
- Ensure all paths and references remain accurate

## Related Documentation

- [ADR (Architecture Decision Records)](../adr/) - Architectural decisions and rationale
- [API Reference](../API_REFERENCE.md) - API documentation
- [Development Guide](../DEVELOPMENT.md) - Development guidelines
