import { NextResponse } from 'next/server'
import { validateTutorRequest } from '../../../../lib/tutor/safety'
import { callProvider } from '../../../../lib/tutor/client'
import { auditEventStub } from '../../../../lib/tutor/audit'

export async function POST(req: Request) {
  const body = await req.json().catch(() => ({}))

  // Basic contract validation
  const validation = validateTutorRequest(body)
  if (!validation.ok) {
    await auditEventStub({ type: 'tutor.request.rejected', reason: validation.reason, body: { safe: true } })
    return NextResponse.json({ error: 'invalid_request', reason: validation.reason }, { status: 400 })
  }

  // Rate limit / guard would run here (stubbed)

  // Call provider via server-only client
  try {
    const resp = await callProvider(body)
    await auditEventStub({ type: 'tutor.request.accepted', lessonId: body.lessonId })
    return NextResponse.json({ data: resp })
  } catch (err) {
    await auditEventStub({ type: 'tutor.request.error', error: String(err) })
    return NextResponse.json({ error: 'provider_error' }, { status: 502 })
  }
}
import { NextRequest, NextResponse } from "next/server";
import { checkTutorRateLimit, getRateLimitIdentity, RATE_LIMIT_MESSAGE } from "@/lib/tutor/rate-limit";
import { recordTutorAuditEvent } from "@/lib/tutor/audit";
import { createAuditEvent, createTutorRefusalResponse, filterTutorInput, filterTutorOutput, validateTutorRequest } from "@/lib/tutor/safety";
import type { TutorResponse, TutorRequest } from "@/lib/tutor/types";

export const dynamic = "force-dynamic";

function getProviderUrl(): string | undefined {
  return process.env.TUTOR_PROVIDER_API_URL;
}

function getProviderKey(): string | undefined {
  return process.env.TUTOR_PROVIDER_API_KEY;
}

function getProviderHeaders() {
  return new Headers({
    "Content-Type": "application/json",
    Authorization: `Bearer ${getProviderKey() ?? ""}`,
  });
}

function createUnavailableResponse(): TutorResponse {
  return {
    type: "refusal",
    message: "The tutor is temporarily unavailable. Please try again later.",
    safe: true,
  };
}

async function callTutorProvider(request: TutorRequest): Promise<TutorResponse> {
  const providerUrl = getProviderUrl();
  const providerKey = getProviderKey();
  if (!providerUrl || !providerKey) {
    return createUnavailableResponse();
  }

  const response = await fetch(providerUrl, {
    method: "POST",
    headers: getProviderHeaders(),
    body: JSON.stringify({
      lesson_id: request.lesson_id,
      question: request.question,
      lesson_context: request.lesson_context,
      subject_code: request.subject_code,
    }),
  });

  if (!response.ok) {
    return createUnavailableResponse();
  }

  const payload = (await response.json().catch(() => null)) as Record<string, unknown> | null;
  const message = typeof payload?.message === "string" ? payload.message.trim() : "I’m sorry, I can’t answer that right now.";

  return {
    type: "answer",
    message,
    safe: true,
  };
}

export async function POST(request: NextRequest) {
  const identity = getRateLimitIdentity(request);
  const rateLimitResponse = checkTutorRateLimit(identity);
  if (rateLimitResponse) {
    recordTutorAuditEvent(
      createAuditEvent({
        lesson_id: "unknown",
        event_type: "rate_limited",
        safe: true,
        metadata: { identity, message: RATE_LIMIT_MESSAGE },
      })
    );
    return rateLimitResponse;
  }

  const payload = await request.json().catch(() => null);
  const validation = validateTutorRequest(payload);
  if (!validation.ok) {
    return NextResponse.json({ error: { message: validation.error } }, { status: 400 });
  }

  recordTutorAuditEvent(
    createAuditEvent({ lesson_id: validation.request.lesson_id, event_type: "request_received", safe: true })
  );

  const filtered = filterTutorInput(validation.request);
  if (filtered.request.question !== validation.request.question) {
    recordTutorAuditEvent(
      createAuditEvent({
        lesson_id: validation.request.lesson_id,
        event_type: "request_sanitized",
        safe: true,
        metadata: { sanitized: "true" },
      })
    );
  }

  if (filtered.refusalReason) {
    recordTutorAuditEvent(
      createAuditEvent({
        lesson_id: validation.request.lesson_id,
        event_type: "refusal_returned",
        safe: true,
        metadata: { reason: filtered.refusalReason },
      })
    );
    return NextResponse.json(createTutorRefusalResponse(filtered.refusalReason), { status: 200 });
  }

  const providerUrl = getProviderUrl();
  recordTutorAuditEvent(
    createAuditEvent({
      lesson_id: filtered.request.lesson_id,
      event_type: "provider_called",
      safe: true,
      metadata: { provider: providerUrl ?? "none" },
    })
  );

  const providerResponse = await callTutorProvider(filtered.request);
  const safeResponse = filterTutorOutput(providerResponse);

  recordTutorAuditEvent(
    createAuditEvent({
      lesson_id: filtered.request.lesson_id,
      event_type: "response_filtered",
      safe: true,
      metadata: { response_type: safeResponse.type },
    })
  );

  return NextResponse.json(safeResponse, { status: 200 });
}
