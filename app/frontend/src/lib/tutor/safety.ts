import type { TutorRequest } from './types'

export function validateTutorRequest(body: any): { ok: boolean; reason?: string } {
  if (!body || typeof body !== 'object') return { ok: false, reason: 'empty_body' }
  if (!body.lessonId || typeof body.lessonId !== 'string') return { ok: false, reason: 'missing_lesson_id' }
  if (!body.prompt || typeof body.prompt !== 'string') return { ok: false, reason: 'missing_prompt' }

  // Disallow free-chat by requiring lesson-scoped prompts only (very conservative)
  if (/\b(chat|tell me about yourself|who are you|free chat)\b/i.test(body.prompt)) {
    return { ok: false, reason: 'free_chat_not_allowed' }
  }

  // PII check (stub): deny if looks like an email or national id
  if (/\b[0-9]{13}\b/.test(body.prompt) || /@/.test(body.prompt)) {
    return { ok: false, reason: 'pii_detected' }
  }

  return { ok: true }
}
import type { TutorRequest, TutorResponse, TutorAuditEvent } from "./types";

const FREE_CHAT_PATTERNS = [
  /\btell me a story\b/i,
  /\bwhat is your opinion\b/i,
  /\bfree chat\b/i,
  /\bjust chat\b/i,
  /\banything\b/i,
  /\btell me about yourself\b/i,
  /\bhow are you\b/i,
  /\bmake up a story\b/i,
  /\bwrite a poem\b/i,
  /\bjoke\b/i,
  /\bsing\b/i,
  /\bchat with you\b/i,
];

const EMAIL_PATTERN = /[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}/gi;
const PHONE_PATTERN = /\+?\d[\d\s-]{6,}\d/g;
const ID_PATTERN = /\b\d{6,}\b/g;

export interface FilteredTutorInput {
  request: TutorRequest;
  refusalReason?: string;
}

export function validateTutorRequest(payload: unknown): { ok: true; request: TutorRequest } | { ok: false; error: string } {
  if (!payload || typeof payload !== "object") {
    return { ok: false, error: "Tutor request must be a JSON object." };
  }

  const request = payload as Record<string, unknown>;

  if (!request.lesson_id || typeof request.lesson_id !== "string" || !request.lesson_id.trim()) {
    return { ok: false, error: "Lesson identifier is required." };
  }

  if (!request.question || typeof request.question !== "string" || !request.question.trim()) {
    return { ok: false, error: "A lesson question is required." };
  }

  return {
    ok: true,
    request: {
      lesson_id: request.lesson_id.trim(),
      question: request.question.trim(),
      lesson_context: typeof request.lesson_context === "string" ? request.lesson_context.trim() : undefined,
      subject_code: typeof request.subject_code === "string" ? request.subject_code.trim() : undefined,
    },
  };
}

export function filterTutorInput(request: TutorRequest): FilteredTutorInput {
  const sanitizedQuestion = sanitizeLearnerPrompt(request.question);
  const requestWithSanitizedQuestion = { ...request, question: sanitizedQuestion };

  if (isBroadFreeChat(sanitizedQuestion)) {
    return {
      request: requestWithSanitizedQuestion,
      refusalReason:
        "This tutor only answers lesson-focused questions. Please ask about the current lesson or exercise.",
    };
  }

  return { request: requestWithSanitizedQuestion };
}

export function createTutorRefusalResponse(reason: string): TutorResponse {
  return {
    type: "refusal",
    message: reason,
    safe: true,
  };
}

export function filterTutorOutput(response: TutorResponse): TutorResponse {
  if (!response || typeof response.message !== "string" || !response.message.trim()) {
    return createTutorRefusalResponse("The tutor is temporarily unavailable. Please try again later.");
  }

  if (response.type !== "answer") {
    return createTutorRefusalResponse(response.message);
  }

  return {
    ...response,
    message: response.message.trim(),
    safe: true,
  };
}

export function createAuditEvent(event: Omit<TutorAuditEvent, "timestamp">): TutorAuditEvent {
  return {
    ...event,
    timestamp: new Date().toISOString(),
  };
}

export function sanitizeLearnerPrompt(prompt: string): string {
  return prompt
    .replace(EMAIL_PATTERN, "[REDACTED]")
    .replace(PHONE_PATTERN, "[REDACTED]")
    .replace(ID_PATTERN, "[REDACTED]")
    .trim();
}

function isBroadFreeChat(question: string): boolean {
  return FREE_CHAT_PATTERNS.some((pattern) => pattern.test(question));
}
