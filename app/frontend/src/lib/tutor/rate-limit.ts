export function checkRateLimit(userId?: string): { ok: boolean; message?: string } {
  // Stubbed fixed-rate policy: allow all for now, but provide a refusal shape
  // In future this will consult Redis or edge-rate-limit middleware.
  return { ok: true }
}
import { NextResponse } from "next/server";

interface RateLimitWindow {
  count: number;
  windowStart: number;
}

const WINDOW_MS = 60_000;
const MAX_REQUESTS_PER_WINDOW = 6;
const rateLimitStore = new Map<string, RateLimitWindow>();

export const RATE_LIMIT_MESSAGE =
  "Let's keep tutor questions focused and lesson-specific. Please wait a moment before asking again.";

export function checkTutorRateLimit(identity: string): NextResponse | null {
  const now = Date.now();
  const state = rateLimitStore.get(identity) ?? { count: 0, windowStart: now };
  const isExpired = now - state.windowStart >= WINDOW_MS;

  if (isExpired) {
    rateLimitStore.set(identity, { count: 1, windowStart: now });
    return null;
  }

  if (state.count >= MAX_REQUESTS_PER_WINDOW) {
    return NextResponse.json({ type: "refusal", message: RATE_LIMIT_MESSAGE, safe: true }, { status: 429 });
  }

  rateLimitStore.set(identity, { count: state.count + 1, windowStart: state.windowStart });
  return null;
}

export function getRateLimitIdentity(request: Request): string {
  const headers = new Headers(request.headers);
  const forwardedHeader = headers.get("x-forwarded-for");
  const firstIp = forwardedHeader ? forwardedHeader.split(",")[0] : "";
  const forwardedIp = firstIp ? firstIp.trim() : "";
  return forwardedIp || headers.get("x-real-ip") || "anonymous";
}

export function clearRateLimitStore() {
  rateLimitStore.clear();
}
