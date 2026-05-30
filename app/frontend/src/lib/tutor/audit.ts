export async function auditEventStub(event: Record<string, any>) {
  // Placeholder hook: emits to console in server logs for now. No PII.
  try {
    // ensure no PII keys accidentally stored
    const safe = { ...event }
    delete safe.userId
    console.info('[audit] tutor event', JSON.stringify(safe))
  } catch (e) {
    // swallow
  }
}
import type { TutorAuditEvent } from "./types";

const auditEvents: TutorAuditEvent[] = [];

export function recordTutorAuditEvent(event: TutorAuditEvent) {
  auditEvents.push(event);
  // Backend persistence is deferred to later PRs; keep an in-memory audit trail for tests and hooks.
}

export function getTutorAuditEvents(): TutorAuditEvent[] {
  return [...auditEvents];
}

export function clearTutorAuditEvents() {
  auditEvents.length = 0;
}
