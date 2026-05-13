## Description

<!-- What does this PR change and why? -->

## Type of change

- [ ] Bug fix
- [ ] New feature / bounded context
- [ ] Refactor / cleanup
- [ ] Docs update
- [ ] Infrastructure / CI change

---

## Architecture checklist

> These are required for all PRs that touch `app/`.

### Router thinness (§2.3)
- [ ] **Router contains no business logic.** Route handlers only: validate input, call a service/module, map the response. Any branching or domain decision has been moved to `app/services/`.
- [ ] Route handler cyclomatic complexity ≤ 5 (verified by `make audit-routers`).
- [ ] No repository imports in routers.

### Import boundaries (§2.4)
- [ ] `lint-imports` passes locally (`make lint-imports`).
- [ ] No upward imports (repositories → services, services → routers, etc.).
- [ ] Services do not import `fastapi.Request`.
- [ ] `app/domain/` has no infrastructure imports.

### Business logic location (ADR 0010)
- [ ] New business logic is in `app/services/<context>_service.py`, not in a router or a module-level service.
- [ ] If a new module service file was added to `app/modules/`, it is a self-contained engine (no duplicate of an existing service).

### Metaphor layer (§2.5)
- [ ] No metaphor layer names (`executive`, `judiciary`, `fourth_estate`, `ether`) appear in engineering code, ADRs, or API contracts.

### General
- [ ] Tests cover the new / changed service logic.
- [ ] Any new ADR has been merged (or is included in this PR) before the governed change.

---

## Testing

<!-- Describe how you tested this change. -->

## Linked issues / ADRs

<!-- e.g. Closes #123, Implements ADR 0010 -->
