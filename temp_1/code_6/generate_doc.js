const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, Footer, AlignmentType, HeadingLevel, BorderStyle, WidthType,
  ShadingType, VerticalAlign, PageNumber, LevelFormat, TableOfContents,
  PageBreak
} = require('docx');
const fs = require('fs');

const blue = "1F4E79";
const lightBlue = "D6E4F0";
const medBlue = "2E75B6";
const accentBlue = "BDD7EE";
const white = "FFFFFF";
const darkGray = "404040";
const borderColor = "AAAAAA";

const border = { style: BorderStyle.SINGLE, size: 1, color: borderColor };
const borders = { top: border, bottom: border, left: border, right: border };
const noBorder = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
const noBorders = { top: noBorder, bottom: noBorder, left: noBorder, right: noBorder };

function hdr(text, level) {
  return new Paragraph({
    heading: level,
    children: [new TextRun({ text, font: "Arial" })],
    spacing: { before: 240, after: 120 }
  });
}

function para(text, opts = {}) {
  return new Paragraph({
    children: [new TextRun({ text, font: "Arial", size: 22, color: darkGray, ...opts })],
    spacing: { before: 60, after: 60 }
  });
}

function bullet(text) {
  return new Paragraph({
    numbering: { reference: "bullets", level: 0 },
    children: [new TextRun({ text, font: "Arial", size: 22, color: darkGray })],
    spacing: { before: 40, after: 40 }
  });
}

function makeTable(headers, rows, colWidths) {
  const totalWidth = colWidths.reduce((a, b) => a + b, 0);
  return new Table({
    width: { size: totalWidth, type: WidthType.DXA },
    columnWidths: colWidths,
    rows: [
      new TableRow({
        tableHeader: true,
        children: headers.map((h, i) => new TableCell({
          borders,
          width: { size: colWidths[i], type: WidthType.DXA },
          shading: { fill: medBlue, type: ShadingType.CLEAR },
          margins: { top: 80, bottom: 80, left: 120, right: 120 },
          children: [new Paragraph({ children: [new TextRun({ text: h, bold: true, color: white, font: "Arial", size: 20 })] })]
        }))
      }),
      ...rows.map((row, ri) => new TableRow({
        children: row.map((cell, i) => new TableCell({
          borders,
          width: { size: colWidths[i], type: WidthType.DXA },
          shading: { fill: ri % 2 === 0 ? "F5F9FC" : white, type: ShadingType.CLEAR },
          margins: { top: 60, bottom: 60, left: 120, right: 120 },
          children: [new Paragraph({ children: [new TextRun({ text: cell, font: "Arial", size: 20, color: darkGray })] })]
        }))
      }))
    ]
  });
}

function spacer() {
  return new Paragraph({ children: [new TextRun("")], spacing: { before: 80, after: 80 } });
}

function divider() {
  return new Paragraph({
    border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: medBlue, space: 1 } },
    children: [new TextRun("")],
    spacing: { before: 120, after: 120 }
  });
}

function codeBlock(lines) {
  return lines.map(line => new Paragraph({
    children: [new TextRun({ text: line, font: "Courier New", size: 18, color: "2F4F4F" })],
    spacing: { before: 20, after: 20 },
    shading: { fill: "F0F4F8", type: ShadingType.CLEAR }
  }));
}

// ────────── CONTENT ────────────────────────────────────────────

const children = [

  // Cover-style title block
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 480, after: 120 },
    children: [new TextRun({ text: "EduBoost SA", bold: true, size: 64, font: "Arial", color: blue })]
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 60, after: 60 },
    children: [new TextRun({ text: "Comprehensive Technical Report", size: 36, font: "Arial", color: medBlue })]
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 60, after: 480 },
    children: [new TextRun({ text: "Version 2.0  |  7 May 2026  |  Status: v0.1.0-beta → Active V2 Migration", size: 22, font: "Arial", color: "666666" })]
  }),

  divider(),
  spacer(),

  // Section 1
  hdr("1. Executive Summary", HeadingLevel.HEADING_1),
  para("EduBoost SA is an AI-powered adaptive learning platform built for South African primary school learners spanning Grade R through Grade 7. The platform combines Item Response Theory (IRT)-based diagnostic assessment with LLM-generated, CAPS-aligned lesson content, parental consent management under South Africa's POPIA legislation, and multilingual support across English, isiZulu, Afrikaans, and isiXhosa."),
  spacer(),
  para("As of May 2026, the project has reached the v0.1.0-beta tagged milestone and is mid-way through a complete architectural pivot: the original five-pillar monolith has been entirely retired, replaced by a strict modular monolith (V2) built on FastAPI + async SQLAlchemy + PostgreSQL, with a Next.js 14 App Router frontend. The V2 architectural migration was declared structurally complete on 2 May 2026, with all V1 code deleted and all core infrastructure consolidated under app/core/."),
  spacer(),
  para("The platform targets deployment on Azure Container Apps (ACA) in the South Africa North region, backed by managed PostgreSQL, managed Redis, and Azure Key Vault for secrets management. Observability is provided by a Prometheus + Grafana + Loki stack."),
  spacer(),
  new Paragraph({ children: [new TextRun({ text: "Key Facts at a Glance", bold: true, size: 24, font: "Arial", color: blue })], spacing: { before: 120, after: 80 } }),
  makeTable(
    ["Attribute", "Value"],
    [
      ["Language distribution", "Python 79.1%, TypeScript 13.4%, PLpgSQL 4.9%, Shell 1.7%, Bicep 0.7%, Other 0.1%"],
      ["Python version", "3.11+"],
      ["Node.js version", "20 LTS"],
      ["Current release tag", "v0.1.0-beta (2026-04-30)"],
      ["Active branch", "master"],
      ["Commit count", "110 (nkgolo-lebelo fork)"],
      ["Backend entrypoint", "app/api_v2.py"],
      ["Frontend framework", "Next.js 14 (App Router)"],
      ["Primary LLM provider", "Groq"],
      ["Fallback LLM provider", "Anthropic Claude"],
      ["Target cloud", "Azure Container Apps, South Africa North"],
      ["POPIA status", "Tracked; compliance workflows implemented"],
      ["CAPS alignment", "Implemented; full coverage validation pending"],
    ],
    [3500, 5860]
  ),

  spacer(),
  divider(),

  // Section 2
  hdr("2. Project Overview", HeadingLevel.HEADING_1),
  hdr("Mission", HeadingLevel.HEADING_2),
  para("EduBoost SA's stated mission is to give every South African primary learner access to personalised, quality education through consent-safe adaptive diagnostics, AI-assisted remediation, and parent-visible progress reporting. The platform is built with a 'Ubuntu' philosophy: community-centred design that acknowledges the social and economic constraints of South African households, including low-bandwidth connectivity, multilingual home environments, and limited access to tutoring."),

  hdr("Target Users", HeadingLevel.HEADING_2),
  bullet("Learners: Grade R to Grade 7 (approximately 6–13 years old)"),
  bullet("Guardians/Parents: Responsible for parental consent, progress review, and account management"),
  bullet("Teachers (future): Classroom-level diagnostic and intervention tools"),
  bullet("Administrators: Platform management, compliance oversight"),

  hdr("Core Feature Set (Implemented)", HeadingLevel.HEADING_2),
  bullet("IRT-based adaptive diagnostic engine for measuring per-learner knowledge gaps"),
  bullet("AI lesson generation with South African cultural context, pseudonymous PII isolation, and multi-provider redundancy"),
  bullet("CAPS-aligned study plans with weekly scheduling"),
  bullet("Gamification: XP, badges, and streaks for Grade R–3; discovery-based engagement for Grade 4–7"),
  bullet("POPIA-grade parental consent management with grant, renewal, withdrawal, and right-to-erasure workflows"),
  bullet("Parent portal with AI-generated progress reports and consent controls"),
  bullet("Multilingual lesson generation in English, isiZulu, Afrikaans, and isiXhosa"),
  bullet("Offline-ready PWA with service worker and manifest"),
  bullet("RLHF feedback pipeline for continuous AI quality improvement"),
  bullet("Prometheus/Grafana/Loki observability stack with business SLO dashboards"),

  spacer(),
  divider(),

  // Section 3
  hdr("3. Architecture Overview", HeadingLevel.HEADING_1),
  hdr("Design Philosophy", HeadingLevel.HEADING_2),
  para("EduBoost V2 is a modular monolith: all bounded contexts (auth, diagnostics, lessons, consent, learners, study plans, gamification, parent portal, RLHF) are co-deployed in a single process but are organised as independent modules with enforced import boundaries. This avoids premature microservice complexity while retaining the organisational clarity of bounded-context design."),
  para("The original V1 'Five Pillars' metaphor (Executive, Judiciary, Fourth Estate, Ether, Profiler) has been fully retired. Domain terminology now governs the codebase."),

  hdr("Bounded Modules", HeadingLevel.HEADING_2),
  makeTable(
    ["Module", "Path", "Responsibility"],
    [
      ["Auth", "app/modules/auth/", "JWT issuance, refresh, revocation, session management"],
      ["Learners", "app/modules/learners/", "Learner profile CRUD, pseudonym management"],
      ["Diagnostics", "app/modules/diagnostics/", "IRT engine, session lifecycle, ability estimation"],
      ["Lessons", "app/modules/lessons/", "LLM gateway, lesson generation, RLHF"],
      ["Consent", "app/modules/consent/", "POPIA consent: grant, renew, withdraw, erasure"],
      ["Study Plans", "app/modules/study_plans/", "CAPS-aligned weekly scheduling"],
      ["Gamification", "app/modules/gamification/", "XP, badges, streaks"],
      ["Parent Portal", "app/modules/parent_portal/", "Progress reports, consent management"],
      ["RLHF", "app/modules/rlhf/", "Feedback capture, preference dataset export"],
    ],
    [1600, 2500, 5260]
  ),

  spacer(),
  divider(),

  // Section 4
  hdr("4. V2 Migration Status", HeadingLevel.HEADING_1),
  hdr("Migration Timeline", HeadingLevel.HEADING_2),
  makeTable(
    ["Date", "Event"],
    [
      ["2026-04-30", "v0.1.0-beta — foundational architecture tagged"],
      ["2026-05-01", "v0.2.0-rc1 — inference microservice, multilingual, RLHF, PWA"],
      ["2026-05-02", "V2 architectural migration declared structurally complete; all V1 code deleted"],
    ],
    [2000, 7360]
  ),
  spacer(),
  hdr("Completed Migration Items", HeadingLevel.HEADING_2),
  bullet("All V1 API layer (app/api/) fully removed; compatibility shim only at app/api/main.py"),
  bullet("RabbitMQ removed; audit trail migrated to append-only PostgreSQL repository"),
  bullet("Celery + Flower removed; replaced by arq (async Redis queue)"),
  bullet("Five-pillar metaphor (Executive, Judiciary, Fourth Estate, Ether) retired from code"),
  bullet("Core infrastructure consolidated under app/core/ (database, config, security, audit, metrics, middleware, exceptions, dependencies, base repository)"),
  bullet("SQLAlchemy ORM models centralised under app/models/__init__.py (Alembic-managed)"),
  bullet("Routers migrated to app/api_v2_routers/"),
  bullet("Domain modules structured as bounded contexts under app/modules/"),
  bullet("CI/CD pipeline moved to .github/workflows/ci-cd.yml"),
  bullet("Test suite reorganised by domain under tests/"),
  bullet("Legacy compose files, scratch directories, and temporary artifacts removed"),
  bullet("Python package structure enforced (__init__.py for all modules)"),

  hdr("Remaining V2 Migration Items (Active Backlog)", HeadingLevel.HEADING_2),
  bullet("Complete migration from Celery background job handlers to arq"),
  bullet("Achieve 80% unit test coverage across all domain modules"),
  bullet("Complete the POPIA compliance test suite end-to-end"),
  bullet("Deploy to ACA staging environment via updated CI pipeline"),
  bullet("Set up Grafana Cloud dashboards for production observability"),
  bullet("Complete security penetration test checklist"),

  spacer(),
  divider(),

  // Section 5
  hdr("5. Technology Stack", HeadingLevel.HEADING_1),
  hdr("Backend", HeadingLevel.HEADING_2),
  makeTable(
    ["Component", "Technology", "Version"],
    [
      ["Language", "Python", "3.11+"],
      ["Web framework", "FastAPI", "Latest stable"],
      ["ORM", "SQLAlchemy (async)", "Latest stable"],
      ["DB migrations", "Alembic", "Latest stable"],
      ["Background jobs", "arq (async Redis queue)", "Latest stable"],
      ["IRT engine", "scikit-learn, numpy, scipy", "As per requirements-ml.txt"],
      ["LLM integration", "Groq (primary), Anthropic (fallback)", "API"],
      ["Validation", "Pydantic v2", "Latest stable"],
      ["Testing", "pytest", "Latest stable"],
      ["E2E testing", "Playwright", "Latest stable"],
      ["Linting", "pre-commit, Bandit, gitleaks", "As per .pre-commit-config.yaml"],
      ["Secrets", "Azure Key Vault + Pydantic config", "—"],
      ["PII scrubbing", "popia_sweep.py (custom)", "—"],
    ],
    [2500, 3500, 3360]
  ),
  spacer(),
  hdr("Frontend", HeadingLevel.HEADING_2),
  makeTable(
    ["Component", "Technology", "Version"],
    [
      ["Framework", "Next.js (App Router)", "14"],
      ["Language", "TypeScript", "Latest"],
      ["Testing", "Jest / React Testing Library", "Latest"],
      ["E2E", "Playwright", "Latest"],
      ["PWA", "Service Worker + manifest.json", "—"],
    ],
    [2500, 3500, 3360]
  ),
  spacer(),
  hdr("Infrastructure", HeadingLevel.HEADING_2),
  makeTable(
    ["Component", "Technology", "Notes"],
    [
      ["Container runtime", "Docker + Docker Compose", "Multi-stage builds"],
      ["Orchestration", "Azure Container Apps (ACA)", "Single node, auto-scale to zero"],
      ["Database", "Azure Database for PostgreSQL Flexible", "SA North, POPIA-compliant region"],
      ["Cache / Queue", "Azure Cache for Redis", "Managed, used by arq"],
      ["Inference", "ACA sidecar container", "Isolated torch/transformers"],
      ["Secrets", "Azure Key Vault", "Centralised, audited"],
      ["CDN / WAF", "Azure Front Door", "SSL termination, SA PoP"],
      ["IaC", "Bicep", "bicep/ directory"],
      ["Metrics", "Prometheus + Alertmanager", "Self-hosted"],
      ["Dashboards", "Grafana Cloud (free tier)", "Managed Prometheus + Loki"],
      ["Logs", "Grafana Loki + Promtail", "Centralised aggregation"],
      ["CI/CD", "GitHub Actions", ".github/workflows/ci-cd.yml"],
    ],
    [2500, 3500, 3360]
  ),
  spacer(),
  hdr("Key Environment Variables", HeadingLevel.HEADING_2),
  makeTable(
    ["Variable", "Purpose"],
    [
      ["DATABASE_URL", "Async SQLAlchemy PostgreSQL connection"],
      ["REDIS_URL", "Redis connection (cache, token revocation, arq jobs)"],
      ["GROQ_API_KEY", "Primary LLM inference"],
      ["ANTHROPIC_API_KEY", "Secondary/fallback LLM"],
      ["JWT_SECRET", "JWT signing secret"],
      ["ENCRYPTION_KEY", "AES-256 key for PII at rest"],
    ],
    [3000, 6360]
  ),

  spacer(),
  divider(),

  // Section 6
  hdr("6. Repository Structure", HeadingLevel.HEADING_1),
  para("The repository follows a clear modular layout organised by concern:"),
  spacer(),
  ...codeBlock([
    "Eduboost-V2/",
    "├── .github/workflows/ci-cd.yml     # GitHub Actions CI/CD pipeline",
    "├── alembic/                        # Database migration scripts",
    "├── app/",
    "│   ├── api_v2.py                   # ★ ACTIVE FastAPI V2 entrypoint",
    "│   ├── api_v2_routers/             # HTTP route handlers (V2)",
    "│   ├── api/main.py                 # Legacy compatibility shim only",
    "│   ├── core/                       # Shared runtime kernel",
    "│   │   ├── database.py             # Async SQLAlchemy session management",
    "│   │   ├── config.py               # Pydantic config + Azure Key Vault",
    "│   │   ├── security.py             # JWT + AES-256 encryption utilities",
    "│   │   ├── audit.py                # PostgreSQL append-only audit writes",
    "│   │   ├── metrics.py              # Prometheus metric definitions",
    "│   │   ├── middleware.py           # Rate limiting, request ID, timing",
    "│   │   ├── exceptions.py           # Global exception handlers",
    "│   │   ├── dependencies.py         # FastAPI DI helpers + consent gate",
    "│   │   └── base.py                 # Generic base repository pattern",
    "│   ├── models/__init__.py          # Centralised SQLAlchemy ORM models",
    "│   └── modules/                    # Bounded context modules",
    "│       ├── auth/",
    "│       ├── diagnostics/irt_engine.py",
    "│       ├── lessons/llm_gateway.py",
    "│       ├── consent/",
    "│       ├── learners/",
    "│       ├── study_plans/",
    "│       ├── gamification/",
    "│       ├── parent_portal/",
    "│       └── rlhf/",
    "├── bicep/                          # Azure IaC (Container Apps)",
    "├── grafana/                        # Grafana dashboards + provisioning",
    "├── prometheus/                     # Prometheus scrape configs",
    "├── requirements/",
    "│   ├── base.txt                    # Runtime dependencies",
    "│   ├── dev.txt                     # Test, lint, type checking",
    "│   └── ml.txt                      # Optional ML extras (torch, HF)",
    "├── tests/",
    "│   ├── popia/                      # POPIA compliance test suite",
    "│   ├── smoke/                      # V2 smoke tests",
    "│   └── unit/modules/              # Domain unit tests",
    "└── docker-compose.yml              # Default local V2 stack",
  ]),

  spacer(),
  divider(),

  // Section 7
  hdr("7. Backend — FastAPI V2", HeadingLevel.HEADING_1),
  hdr("Core Infrastructure (app/core/)", HeadingLevel.HEADING_2),
  para("The shared runtime kernel provides the following components:"),
  bullet("database.py — Async SQLAlchemy session management. All database access uses async sessions to avoid blocking the FastAPI event loop."),
  bullet("config.py — Pydantic Settings with Azure Key Vault integration (local .env fallback for development). Validates all required environment variables at startup, failing fast on missing production secrets."),
  bullet("security.py — JWT issuance and validation. Access tokens default to 15-minute TTL; refresh tokens to 7 days. AES-256 encryption for PII at rest. Redis-backed JWT revocation."),
  bullet("audit.py — Async, non-blocking writes to an append-only PostgreSQL audit repository. All sensitive actions produce immutable audit records."),
  bullet("metrics.py — Prometheus metric registration for request count, latency histograms, error rates, LLM call tracking, and business SLO counters."),
  bullet("middleware.py — FastAPI middleware for rate limiting, request ID injection, and request timing."),
  bullet("exceptions.py — Unified global exception handlers with structured error format."),
  bullet("dependencies.py — FastAPI dependency injection helpers including POPIA consent gate (declarative, impossible to bypass for learner-data routes)."),
  bullet("base.py — Generic base repository pattern with standardised method names."),

  hdr("Key API Surface (V2 Routers)", HeadingLevel.HEADING_2),
  makeTable(
    ["Domain", "Routes"],
    [
      ["Auth", "Register, login, token refresh, logout, email verify, password reset"],
      ["Learners", "CRUD for learner profiles, pseudonym management"],
      ["Guardians", "Account management, learner linking"],
      ["Consent", "Grant, renew, withdraw, status check"],
      ["Diagnostics", "Session creation, question serving, answer submission, result retrieval"],
      ["Lessons", "Generation, retrieval, RLHF feedback"],
      ["Study Plans", "CAPS-aligned plan creation, weekly view"],
      ["Gamification", "XP, badge, streak endpoints"],
      ["Parent Portal", "Progress reports, consent history, data export"],
      ["POPIA", "Right-to-erasure initiation, export download"],
    ],
    [2000, 7360]
  ),

  spacer(),
  divider(),

  // Section 8
  hdr("8. Frontend — Next.js", HeadingLevel.HEADING_1),
  hdr("Technology", HeadingLevel.HEADING_2),
  bullet("Framework: Next.js 14 with the App Router"),
  bullet("Language: TypeScript"),
  bullet("Testing: Jest + React Testing Library + Playwright for E2E"),
  bullet("PWA: Service worker + manifest.json for offline resilience and installability"),

  hdr("Local Development Ports", HeadingLevel.HEADING_2),
  makeTable(
    ["Service", "URL"],
    [
      ["Frontend", "http://localhost:3050"],
      ["API", "http://localhost:8000"],
      ["API Docs", "http://localhost:8000/docs"],
      ["MkDocs", "http://localhost:8001"],
      ["Prometheus", "http://localhost:9090"],
      ["Alertmanager", "http://localhost:9093"],
    ],
    [3000, 6360]
  ),
  spacer(),
  para("The frontend includes a registered service worker and manifest.json enabling installation as a Progressive Web App. Offline resilience is provided through an app shell cache, enabling continued learner access on intermittent South African mobile networks."),

  spacer(),
  divider(),

  // Section 9
  hdr("9. Infrastructure & DevOps", HeadingLevel.HEADING_1),
  hdr("Docker Compose Files", HeadingLevel.HEADING_2),
  makeTable(
    ["File", "Purpose"],
    [
      ["docker-compose.yml", "Default local V2 stack (use for all development)"],
      ["docker-compose.v2.yml", "Explicit V2-focused variant"],
      ["docker-compose.aca.yml", "Azure Container Apps-oriented staging stack"],
      ["docker-compose.prod.yml", "Production-like validation stack"],
    ],
    [3000, 6360]
  ),
  spacer(),
  hdr("CI/CD Pipeline", HeadingLevel.HEADING_2),
  para("GitHub Actions at .github/workflows/ci-cd.yml. The pipeline enforces:"),
  bullet("Backend lint and type check"),
  bullet("Backend unit tests and integration tests"),
  bullet("Alembic schema drift check (alembic check)"),
  bullet("POPIA compliance tests"),
  bullet("Frontend tests, type check, and build"),
  bullet("Playwright E2E tests"),
  bullet("Docker image scan (Trivy)"),
  bullet("Dependency audit (pip-audit, npm audit)"),
  bullet("Secret scan (gitleaks)"),
  bullet("Staging smoke tests"),

  hdr("Azure Production Architecture", HeadingLevel.HEADING_2),
  makeTable(
    ["Component", "Azure Service", "Notes"],
    [
      ["Backend", "Azure Container Apps", "Single node, scale-to-zero"],
      ["Frontend", "Azure Static Web Apps or ACA", "Managed, no ops overhead"],
      ["Database", "Azure DB for PostgreSQL Flexible", "South Africa North, POPIA region"],
      ["Cache / Queue", "Azure Cache for Redis", "Managed, arq background jobs"],
      ["Inference", "ACA sidecar", "Internal network only, isolated torch"],
      ["Secrets", "Azure Key Vault", "Centralised, audited access"],
      ["CDN / WAF", "Azure Front Door", "SSL termination, SA PoP"],
      ["Observability", "Grafana Cloud (free tier)", "Managed Prometheus + Loki"],
    ],
    [2000, 3500, 3860]
  ),

  spacer(),
  divider(),

  // Section 10
  hdr("10. Data Layer", HeadingLevel.HEADING_1),
  hdr("Alembic Revision History", HeadingLevel.HEADING_2),
  makeTable(
    ["Revision", "Description"],
    [
      ["0001", "Baseline schema: guardians, learners, parental_consents, diagnostic_sessions, study_plans, audit_log"],
      ["0002–0003", "Schema extensions (auth tokens, gamification)"],
      ["0004", "lesson_feedback and rlhf_exports tables"],
    ],
    [1500, 7860]
  ),
  spacer(),
  hdr("Key Schema Entities", HeadingLevel.HEADING_2),
  makeTable(
    ["Entity", "Key Fields", "Notes"],
    [
      ["guardians", "id, email_hash, email_ciphertext, created_at", "Email stored as SHA-256 hash + pgcrypto ciphertext"],
      ["learners", "id, pseudonym_id, grade, guardian_id, soft_deleted_at", "pseudonym_id used for all LLM calls"],
      ["parental_consents", "id, learner_id, guardian_id, granted_at, expires_at, is_active", "Annual renewal enforced via expires_at"],
      ["diagnostic_sessions", "id, learner_id, subject, grade, ability_estimate, completed_at", "IRT-based estimation"],
      ["study_plans", "id, learner_id, caps_week, term, subject, plan_json", "CAPS-aligned"],
      ["audit_log", "id, event_type, actor_id, learner_id, timestamp, event_hash", "Append-only, POPIA compliant"],
      ["lesson_feedback", "id, lesson_id, learner_id, rating, comment_scrubbed", "PII-scrubbed comments"],
      ["rlhf_exports", "id, created_at, format, export_path", "OpenAI/Anthropic preference format"],
    ],
    [1800, 3200, 4360]
  ),

  spacer(),
  divider(),

  // Section 11
  hdr("11. AI & LLM Integration", HeadingLevel.HEADING_1),
  hdr("LLM Gateway", HeadingLevel.HEADING_2),
  para("A provider-agnostic interface at app/modules/lessons/llm_gateway.py abstracts all LLM provider calls. The gateway supports:"),
  bullet("Primary provider: Groq (low latency, cost-effective)"),
  bullet("Fallback provider: Anthropic Claude"),
  bullet("Provider selection, timeout, retry, and circuit breaker logic"),
  bullet("Token usage and latency logging (without sensitive prompt content)"),
  bullet("Prompt template versioning (planned)"),

  hdr("IRT Diagnostic Engine", HeadingLevel.HEADING_2),
  para("Item Response Theory (3-parameter logistic model) powers the adaptive diagnostic. The engine estimates learner ability (theta) from a sequence of item responses, uses Fisher information to select maximally informative next items, and produces a per-topic ability estimate used to generate CAPS-aligned study plans."),

  hdr("Multilingual Lesson Generation", HeadingLevel.HEADING_2),
  para("As of v0.2.0-rc1, the lesson generation pipeline supports English, isiZulu (zu), Afrikaans (af), and isiXhosa (xh). Each language variant includes localised cultural context. The multilingual roadmap extends to all 11 official South African languages."),

  spacer(),
  divider(),

  // Section 12
  hdr("12. POPIA Compliance & Privacy", HeadingLevel.HEADING_1),
  hdr("Regulatory Context", HeadingLevel.HEADING_2),
  para("POPIA (Protection of Personal Information Act) is South Africa's primary data protection legislation, equivalent in scope to GDPR. EduBoost processes children's personal information, which is subject to heightened protection under POPIA Section 35."),

  hdr("Implemented Compliance Controls", HeadingLevel.HEADING_2),
  bullet("Consent gating: The POPIA consent gate is implemented as a FastAPI dependency in app/core/dependencies.py. It is declarative and injected at the router level — developers cannot accidentally omit consent checks on learner-data routes."),
  bullet("Consent lifecycle: States managed: pending, granted, denied, expired, withdrawn, renewal_required. Annual renewal is enforced via expires_at on every parental_consents record."),
  bullet("Right to erasure: Guardian-initiated deletion workflows atomically revoke consent and soft-delete personal data. Audit records are preserved."),
  bullet("Data export: Guardians can request machine-readable exports of all learner and guardian personal data."),
  bullet("Pseudonymisation: pseudonym_id is substituted for all real learner identifiers in LLM calls. No names, emails, or phone numbers reach external AI providers."),
  bullet("Audit trail: Every sensitive action produces an immutable record in the PostgreSQL audit repository (append-only by database permission)."),
  bullet("PII scrubbing: popia_sweep.py performs automated scanning of LLM prompt paths for potential PII leakage."),

  hdr("Outstanding Compliance Items", HeadingLevel.HEADING_2),
  makeTable(
    ["Item", "Priority"],
    [
      ["Consent withdrawal notification and downstream deletion jobs", "Critical"],
      ["Tamper-evident audit chain (event hash chain)", "High"],
      ["POPIA data retention policy document", "Medium"],
      ["Subprocessor register", "Medium"],
      ["Child-friendly privacy notice", "High"],
      ["End-to-end POPIA compliance test suite", "Critical (in progress)"],
      ["DPIA-style privacy impact assessment", "High"],
    ],
    [6500, 2860]
  ),

  spacer(),
  divider(),

  // Section 13
  hdr("13. Observability & Monitoring", HeadingLevel.HEADING_1),
  hdr("Metrics (Prometheus)", HeadingLevel.HEADING_2),
  para("All business-critical and infrastructure metrics are instrumented via app/core/metrics.py:"),
  bullet("API request count, latency (p50/p95/p99), error rate, status codes"),
  bullet("Database connection pool utilisation"),
  bullet("Redis operation counts and latency"),
  bullet("Background job queue depth and completion rate"),
  bullet("LLM provider call count, latency, token usage, fallback rate"),
  bullet("Consent lifecycle events (granted, renewed, withdrawn, expired)"),
  bullet("Diagnostic session starts and completions"),
  bullet("Lesson generation starts, completions, and failures"),

  hdr("Grafana Dashboards", HeadingLevel.HEADING_2),
  makeTable(
    ["Dashboard", "Purpose"],
    [
      ["learner_journey.json", "Learner Journey SLOs: diagnostic completion, lesson efficacy"],
      ["llm_provider_health.json", "LLM provider latency, success rates, fallback frequency"],
      ["Constitutional Health", "(V1 legacy, being replaced) — approval rates, violation trends"],
    ],
    [3000, 6360]
  ),
  spacer(),
  para("Alertmanager is configured for: API process down, readiness probe failure, high 5xx error rate, high P95 latency, database unavailable, Redis unavailable, migration failure, audit write failure, consent enforcement failure, and failed security scans."),

  spacer(),
  divider(),

  // Section 14
  hdr("14. Testing Strategy", HeadingLevel.HEADING_1),
  hdr("Backend", HeadingLevel.HEADING_2),
  makeTable(
    ["Layer", "Framework", "Coverage Target"],
    [
      ["Unit", "pytest", "≥ 80%"],
      ["Integration", "pytest", "All production paths"],
      ["POPIA compliance", "pytest (tests/popia/)", "All consent/erasure/export workflows"],
      ["Smoke", "pytest (tests/smoke/)", "V2 entrypoint, health, readiness"],
      ["E2E", "Playwright", "Full guardian → learner → lesson flow"],
    ],
    [2000, 3000, 4360]
  ),
  spacer(),
  hdr("Frontend", HeadingLevel.HEADING_2),
  makeTable(
    ["Layer", "Framework", "Coverage Target"],
    [
      ["Unit/Component", "Jest + React Testing Library", "≥ 80%"],
      ["E2E", "Playwright", "Core user journeys"],
      ["Visual regression", "Planned", "—"],
      ["Accessibility", "Planned (axe-core)", "WCAG 2.1 AA"],
    ],
    [2000, 3000, 4360]
  ),

  spacer(),
  divider(),

  // Section 15
  hdr("15. Security Posture", HeadingLevel.HEADING_1),
  hdr("Authentication & Tokens", HeadingLevel.HEADING_2),
  bullet("Access tokens: 15 minutes TTL (configurable)"),
  bullet("Refresh tokens: 7 days TTL (configurable)"),
  bullet("JWT revocation backed by Redis"),
  bullet("Refresh token rotation on use; token family reuse detection planned"),
  bullet("Passwords hashed with Argon2id/bcrypt with tuned cost (implementation pending)"),

  hdr("Encryption", HeadingLevel.HEADING_2),
  bullet("PII at rest: AES-256 encryption via ENCRYPTION_KEY"),
  bullet("Guardian emails: SHA-256 hash + pgcrypto-encrypted ciphertext"),
  bullet("Transport: TLS enforced via Azure Front Door (HSTS)"),

  hdr("Security Scanning (CI)", HeadingLevel.HEADING_2),
  makeTable(
    ["Tool", "Scope"],
    [
      ["pip-audit", "Python dependency vulnerability scan"],
      ["npm audit", "Node.js dependency vulnerability scan"],
      ["Trivy", "Docker image layer scan"],
      ["Bandit", "Python static security analysis"],
      ["gitleaks", "Secret leakage detection in git history"],
      ["detect-secrets", "Pre-commit secret detection (.secrets.baseline)"],
      ["import-linter", "Enforce module boundary rules (.importlinter)"],
    ],
    [2000, 7360]
  ),

  spacer(),
  divider(),

  // Section 16
  hdr("16. Release History & Changelog", HeadingLevel.HEADING_1),
  hdr("v0.1.0-beta — 2026-04-30 (First Tagged Release)", HeadingLevel.HEADING_2),
  bullet("FastAPI backend with routers: auth, learners, consent, diagnostic, lessons, study-plans, parent-portal"),
  bullet("Next.js 14 App Router frontend: dashboard, lesson view, diagnostic, parent portal"),
  bullet("Alembic migration 0001: guardians, learners, parental_consents, diagnostic_sessions, study_plans, audit_log"),
  bullet("ConsentService — POPIA parental consent with grant/revoke/erasure"),
  bullet("IRT-based diagnostic engine (scikit-learn, numpy, scipy)"),
  bullet("LLM lesson generation via Anthropic Claude and Groq with pseudonym_id isolation"),
  bullet("Celery + Redis async task queue with Beat scheduler"),
  bullet("Prometheus + Grafana observability stack"),
  bullet("Docker Compose local development stack (9 services)"),
  bullet("GitHub Actions CI skeleton (lint + test)"),
  bullet("Emails stored as SHA-256 hash + pgcrypto ciphertext"),
  bullet("Soft-delete pattern for right-to-erasure (POPIA Section 24)"),
  bullet("Annual consent renewal enforced via expires_at"),

  hdr("v0.2.0-rc1 — 2026-05-01", HeadingLevel.HEADING_2),
  bullet("Inference Microservice: torch/transformers decoupled into standalone ACA sidecar"),
  bullet("API container footprint reduced from ~4 GB to <500 MB"),
  bullet("Grafana Loki + Promtail for centralised structured logging"),
  bullet("Multilingual support: isiZulu, Afrikaans, isiXhosa lesson generation with localised context"),
  bullet("RLHF Pipeline: RLHFService for feedback capture and preference dataset export"),
  bullet("PII scrubbing: regex-based scrubbing in RLHFService for free-text comments"),
  bullet("PWA: manifest.json + service worker for installability and offline resilience"),
  bullet("SLO Instrumentation: Prometheus counters for consent, diagnostic, study plan, lesson volume"),
  bullet("Security Runbook: penetration test checklist in audits/security/pen_test_checklist.md"),
  bullet("Alembic Revision 0004: lesson_feedback and rlhf_exports tables"),

  hdr("Unreleased — 2026-05-02 (V2 Migration Complete)", HeadingLevel.HEADING_2),
  bullet("Modular bounded-context architecture under app/modules/"),
  bullet("New shared kernel app/core/ with all cross-cutting concerns"),
  bullet("ORM models centralised in app/models/__init__.py"),
  bullet("LLM gateway abstraction: provider-agnostic interface"),
  bullet("IRT engine isolated in app/modules/diagnostics/irt_engine.py"),
  bullet("Celery → arq migration (async Redis queue)"),
  bullet("POPIA consent gate as FastAPI dependency"),
  bullet("CI/CD moved to .github/workflows/ci-cd.yml"),
  bullet("All V1 API layer removed; RabbitMQ removed; Five-pillar metaphor retired from code"),

  spacer(),
  divider(),

  // Section 17
  hdr("17. Outstanding Backlog & Risk Register", HeadingLevel.HEADING_1),
  hdr("Critical Priority (Must resolve before production launch)", HeadingLevel.HEADING_2),
  makeTable(
    ["#", "Item", "Domain"],
    [
      ["1", "Automated database backups: encrypted, monitored, restore-tested", "Ops"],
      ["2", "Production CORS/security headers/rate limits verified in staging", "Security"],
      ["3", "Logs, metrics, traces, alerts, and dashboards live before real learner data", "Observability"],
      ["4", "Incident response, data breach handling procedures documented", "Ops"],
      ["5", "POPIA consent, export, erasure, and LLM PII-redaction tested end-to-end", "Compliance"],
      ["6", "Canonical repository governance document", "Governance"],
      ["7", "Object-level authorization tests (learner cannot access other learner)", "Security"],
      ["8", "Consent bypass negative tests for all learner-data routes", "Security"],
      ["9", "Structured lesson output schema + validator", "AI"],
      ["10", "CAPS topic map MVP for launch grade/subject", "Curriculum"],
      ["11", "Production CORS wildcard origin validation", "Security"],
      ["12", "CSRF strategy for cookie-based auth", "Security"],
      ["13", "Secret rotation: confirm no real secrets in git history", "Security"],
      ["14", "Legal documents: ToS, Privacy Policy, Child Notice, Parent Consent Notice", "Legal"],
    ],
    [500, 7100, 1760]
  ),
  spacer(),
  hdr("Risk Register", HeadingLevel.HEADING_2),
  makeTable(
    ["Risk", "Likelihood", "Impact", "Mitigation"],
    [
      ["POPIA enforcement gap: consent bypass possible", "Medium", "Critical", "Declarative dependency injection; negative tests in progress"],
      ["LLM content hallucination serving incorrect answers to learners", "High", "High", "Structured output validation + human review queue (planned)"],
      ["PII leakage to LLM providers", "Low", "Critical", "pseudonym_id isolation; popia_sweep.py automated scanning"],
      ["Lack of canonical repository governance", "Medium", "High", "Document and enforce; currently unresolved"],
      ["No production backup/restore tested", "High", "Critical", "Backup plan exists; restore test not yet run"],
      ["Overclaiming CAPS coverage before validation", "Medium", "High", "Do not claim full coverage until every topic is validated"],
      ["Secret rotation not verified", "Medium", "High", "gitleaks in CI; manual history review needed"],
    ],
    [2500, 1000, 900, 4960]
  ),

  spacer(),
  divider(),

  // Section 18
  hdr("18. Roadmap & Next Milestones", HeadingLevel.HEADING_1),
  hdr("Milestone A — Production Hardening Foundation", HeadingLevel.HEADING_2),
  bullet("Dependency-aware /ready probe"),
  bullet("Protected master branch + release workflow"),
  bullet("docs/environment_variables.md and docs/release_checklist.md"),
  bullet("Database backup + restore test"),
  bullet("Auth/consent/POPIA integration tests"),
  bullet("Security headers + CORS verified; Staging environment online"),

  hdr("Milestone B — Learner MVP", HeadingLevel.HEADING_2),
  bullet("Guardian signup and account management"),
  bullet("Learner profile creation"),
  bullet("Parental consent capture and validation"),
  bullet("Adaptive diagnostic session (end-to-end)"),
  bullet("First validated CAPS-aligned generated lesson"),
  bullet("Learner dashboard with study plan"),
  bullet("Parent progress summary"),
  bullet("Feedback/report content issue workflow"),

  hdr("Milestone C — Trustworthy AI Learning Loop", HeadingLevel.HEADING_2),
  bullet("CAPS topic map (all launch grades and subjects)"),
  bullet("Structured lesson output schema and validator"),
  bullet("Answer-key independent checking"),
  bullet("Prompt versioning system and human content review queue"),
  bullet("Content quality scoring rubric and AI transparency labels on lessons"),

  hdr("Milestone D — Beta Launch", HeadingLevel.HEADING_2),
  bullet("Legal documents (ToS, Privacy Policy, Child Notice)"),
  bullet("Incident response playbooks"),
  bullet("Automated backups with restore test"),
  bullet("Production monitoring and alerting live"),
  bullet("Complete Playwright E2E suite"),
  bullet("First signed release tag"),
  bullet("Limited beta cohort (explicitly consented users)"),

  hdr("Milestone E — Mission Expansion", HeadingLevel.HEADING_2),
  bullet("Full multilingual support (11 official SA languages)"),
  bullet("Low-data/offline mode as first-class feature"),
  bullet("Parent co-pilot (weekly reports, 'how to help' guide)"),
  bullet("Teacher dashboard and classroom diagnostics"),
  bullet("Sponsored learner model (NGO/community partnerships)"),
  bullet("CAPS learning graph with topic map visualisation"),
  bullet("Offline lesson packs and printable worksheets"),

  spacer(),
  divider(),

  // Section 19
  hdr("19. Conclusion", HeadingLevel.HEADING_1),
  para("EduBoost SA has achieved a significant architectural maturity milestone in May 2026. The complete retirement of the five-pillar V1 architecture and consolidation into a clean modular monolith places the platform on a technically sound foundation for production deployment. The V2 codebase is well-structured, with genuine separation of concerns between bounded modules, a disciplined core infrastructure kernel, POPIA consent controls built as first-class FastAPI dependencies, and a provider-agnostic LLM gateway that insulates the product from single-vendor risk."),
  spacer(),
  para("The work remaining before production launch is substantial but clearly identified. The most consequential gaps are in operational readiness (backup/restore, production alerting, incident response), compliance completeness (end-to-end POPIA test suite, tamper-evident audit chain), and content quality assurance (CAPS topic map, structured lesson output validation, answer-key checking). None of these gaps compromise the architectural decision-making; they are execution tasks that require sustained focus."),
  spacer(),
  para("EduBoost's mission — giving South African primary learners access to consent-safe, CAPS-aligned, adaptive learning — is both technically tractable with the current architecture and genuinely differentiated. Executing the milestones above, with an honest and conservative claims posture on CAPS coverage and AI capability, positions the platform for a trustworthy and impactful public beta."),

  spacer(),
  divider(),
  spacer(),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    children: [new TextRun({ text: "Report generated: 7 May 2026  |  Source: nkgolo-lebelo/Eduboost-V2 @ master (110 commits)  |  Document version: 2.0", font: "Arial", size: 18, color: "888888", italics: true })]
  }),
];

const doc = new Document({
  numbering: {
    config: [
      {
        reference: "bullets",
        levels: [{
          level: 0,
          format: LevelFormat.BULLET,
          text: "\u2022",
          alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } }
        }]
      }
    ]
  },
  styles: {
    default: {
      document: { run: { font: "Arial", size: 22 } }
    },
    paragraphStyles: [
      {
        id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 36, bold: true, font: "Arial", color: blue },
        paragraph: { spacing: { before: 360, after: 160 }, outlineLevel: 0,
          border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: medBlue, space: 1 } } }
      },
      {
        id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 26, bold: true, font: "Arial", color: medBlue },
        paragraph: { spacing: { before: 240, after: 80 }, outlineLevel: 1 }
      },
    ]
  },
  sections: [{
    properties: {
      page: {
        size: { width: 12240, height: 15840 },
        margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }
      }
    },
    headers: {
      default: new Header({
        children: [
          new Paragraph({
            border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: medBlue, space: 1 } },
            children: [
              new TextRun({ text: "EduBoost SA — Technical Report", font: "Arial", size: 18, color: "666666" }),
              new TextRun({ text: "  |  May 2026", font: "Arial", size: 18, color: "999999" }),
            ],
            spacing: { after: 120 }
          })
        ]
      })
    },
    footers: {
      default: new Footer({
        children: [
          new Paragraph({
            border: { top: { style: BorderStyle.SINGLE, size: 4, color: medBlue, space: 1 } },
            alignment: AlignmentType.CENTER,
            children: [
              new TextRun({ text: "Page ", font: "Arial", size: 18, color: "888888" }),
              new TextRun({ children: [PageNumber.CURRENT], font: "Arial", size: 18, color: "888888" }),
              new TextRun({ text: " of ", font: "Arial", size: 18, color: "888888" }),
              new TextRun({ children: [PageNumber.TOTAL_PAGES], font: "Arial", size: 18, color: "888888" }),
            ],
            spacing: { before: 120 }
          })
        ]
      })
    },
    children
  }]
});

Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync("/mnt/user-data/outputs/EduBoost_SA_Technical_Report_May2026.docx", buffer);
  console.log("Done!");
});
