export type TutorRequest = {
  lessonId: string
  userId?: string
  prompt: string
}

export type TutorResponse = {
  text: string
  safe: boolean
}
export interface TutorRequest {
  lesson_id: string;
  question: string;
  lesson_context?: string;
  subject_code?: string;
}

export type TutorResponseType = "answer" | "refusal";

export interface TutorResponse {
  type: TutorResponseType;
  message: string;
  safe?: boolean;
}

export interface TutorAuditEvent {
  lesson_id: string;
  event_type: "request_received" | "request_sanitized" | "rate_limited" | "provider_called" | "response_filtered" | "refusal_returned";
  timestamp: string;
  safe: boolean;
  metadata?: Record<string, string>;
}
