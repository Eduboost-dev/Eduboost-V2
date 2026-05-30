import { useState } from 'react'
import type { TutorResponse } from '../lib/tutor/types'

export function useTutorStream() {
  const [loading, setLoading] = useState(false)
  const [response, setResponse] = useState<TutorResponse | null>(null)

  async function send(request: { lessonId: string; prompt: string }) {
    setLoading(true)
    try {
      const r = await fetch('/api/tutor', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(request) })
      const data = await r.json()
      setResponse(data.data ?? null)
      return data
    } finally {
      setLoading(false)
    }
  }

  return { loading, response, send }
}
"use client";

import { useCallback, useState } from "react";
import { askTutor } from "@/lib/tutor/client";
import type { TutorRequest, TutorResponse } from "@/lib/tutor/types";

export function useTutorStream() {
  const [response, setResponse] = useState<TutorResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const sendTutorRequest = useCallback(async (request: TutorRequest) => {
    setLoading(true);
    setError(null);

    try {
      const result = await askTutor(request);
      setResponse(result);
      return result;
    } catch (caught) {
      const nextError = caught instanceof Error ? caught : new Error("Tutor request failed");
      setError(nextError);
      throw nextError;
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    response,
    loading,
    error,
    sendTutorRequest,
  };
}
