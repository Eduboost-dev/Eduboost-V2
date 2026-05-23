# Audit Write Runtime Evidence Status

Generated at: `2026-05-23T12:05:02Z`
Commit: `4c8c299c236ebc10d1211e3f0d9898c714365c37`

**Status:** `audit-write-runtime-not-accepted`
**DB URL label:** `AUDIT_WRITE_DATABASE_URL`
**DB checked:** `False`
**audit_events exists:** `False`
**audit_events before:** `None`
**audit_events after:** `None`
**audit_events delta:** `None`
**Trace ID:** `audit-write-4c8c299c236e-20260523120457`
**Trace detected:** `False`
**Flow command:** `curl -fsS https://eduboost-api.onrender.com/api/v2/health/deep`
**Flow return code:** `None`
**Run ID:** ``
**Run URL:** ``
**Workflow:** ``

## Flow output excerpt

```text

```

## Blockers

- database audit-write check failed: OperationalError: connection to server at "db.ezjzbvybbwynqpqnbrdt.supabase.co" (2a05:d018:48a:c900:b75d:cff7:aa83:c96d), port 5432 failed: Network is unreachable
	Is the server running on that host and accepting TCP/IP connections?


## No false-closure rules

- This proof closes AUDIT-WRITE-001 only in AUDIT_WRITE_ACCEPT=1 mode.
- A real flow command must run successfully.
- The audit_events table must contain rows after the flow.
- Either audit_events count must increase or the trace ID must be found in recent audit rows.
- A successful GitHub Actions run matching current commit is required.
- This proof does not close JWT, ARQ, DIAG-SCORE, approvals, frontend runtime, backup/restore/rollback, or beta release.
