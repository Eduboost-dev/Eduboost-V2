# Architecture Decisions Index

All significant architectural decisions for EduBoost SA V2 are recorded as
Architecture Decision Records (ADRs) under `docs/adr/`.

New ADRs must be proposed via PR, reviewed by at least one senior engineer,
and merged before the change they govern lands in `master`.

---

## Index

| ADR | Title | Status |
|---|---|---|
| [0010](adr/0010-business-logic-location.md) | Business Logic Location: `app/services` vs `app/modules` | Accepted |

---

## Template

Copy `docs/adr/0000-template.md` when creating a new ADR. Increment the
four-digit prefix sequentially.

```
# ADR XXXX — <Title>

**Status:** Proposed | Accepted | Deprecated | Superseded by XXXX
**Date:** YYYY-MM
**Deciders:** <names or team>

## Context
## Decision
## Consequences
## Alternatives Considered
```
