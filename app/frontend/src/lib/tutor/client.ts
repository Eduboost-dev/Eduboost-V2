import type { TutorRequest, TutorResponse } from './types'

// Server-only provider client. Uses env var for provider key (not exposed to client).
const PROVIDER_URL = process.env.TUTOR_PROVIDER_URL || 'https://provider.example.local/v1/chat'

export async function callProvider(req: TutorRequest): Promise<TutorResponse> {
  const key = process.env.TUTOR_PROVIDER_KEY
  if (!key) throw new Error('provider key missing')

  const resp = await fetch(PROVIDER_URL, {
    method: 'POST',
    headers: {
      'content-type': 'application/json',
      'authorization': `Bearer ${key}`,
    },
    body: JSON.stringify({ lessonId: req.lessonId, prompt: req.prompt }),
  })

  if (!resp.ok) throw new Error('provider_error')
  const data = await resp.json()
  return { text: data.text ?? '', safe: data.safe ?? true }
}
import { fetchApi } from "@/lib/api/client";
import type { TutorRequest, TutorResponse } from "./types";

export async function askTutor(request: TutorRequest): Promise<TutorResponse> {
  return fetchApi<TutorResponse>("/api/tutor", {
    method: "POST",
    body: JSON.stringify(request),
  });
}
