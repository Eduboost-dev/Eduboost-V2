import { fetchApi } from "./client";

export type ContentScope = {
  scope_id: string;
  grade: number;
  subject_code: string;
  subject: string;
  language: string;
  curriculum: string;
  status: string;
  caps_refs: string[];
};

export type ScopeCoverageReport = {
  scope_id: string;
  summary: Record<string, number>;
  layers: Record<string, { target_total: number; approved_total: number; coverage_ratio: number }>;
};

export type GenerationRun = {
  run_id: string;
  scope_id: string;
  status: string;
  requested_by?: string | null;
  run_metadata: Record<string, unknown>;
};


export type GenerationTask = {
  task_id: string;
  run_id: string;
  scope_id: string;
  caps_ref?: string | null;
  content_layer: string;
  status: string;
  attempt_number: number;
  max_attempts: number;
  output_artifact_ids: string[];
  validation_failures: string[];
};

export type GenerationPlanResponse = {
  run_id: string;
  created_task_ids: string[];
  skipped: Array<Record<string, unknown>>;
  missing: Array<Record<string, unknown>>;
};

export type GenerationExecutionResponse = {
  run_id?: string | null;
  task_id?: string | null;
  status: string;
  artifact_ids: string[];
  errors: string[];
  summary: Record<string, unknown>;
  provider?: string | null;
  mode?: string | null;
};

export type GenerationExecutionReport = {
  run_id: string;
  status: string;
  tasks: number;
  queued: number;
  succeeded: number;
  failed: number;
  skipped: number;
  artifacts: number;
};


export type ReviewQueueItem = {
  artifact_id: string;
  scope_id: string;
  content_layer: string;
  artifact_type: string;
  caps_ref?: string | null;
  status: string;
  risk_level: string;
  risk_reasons: string[];
  validation_status: string;
  provenance_status: string;
  reviewer_id?: string | null;
};

export type ReviewQueuePage = {
  items: ReviewQueueItem[];
  total: number;
  limit: number;
  offset: number;
};

export type ReviewBundle = {
  artifact: Record<string, unknown>;
  validation_report?: Record<string, unknown> | null;
  provenance: Record<string, unknown>;
  sources: Array<Record<string, unknown>>;
  review_risk: { level: string; score: number; reasons: string[] };
  generation_metadata: Record<string, unknown>;
  prior_review_events: Array<Record<string, unknown>>;
};

export type BulkReviewResponse = {
  status: string;
  artifact_ids: string[];
  errors: string[];
  summary: Record<string, number>;
};

export type ReviewerWorkload = {
  reviewer_id: string;
  assigned: number;
  in_review: number;
  overdue: number;
  total_open: number;
};

export type ContentArtifact = {
  artifact_id: string;
  scope_id: string;
  content_layer: string;
  artifact_type: string;
  caps_ref?: string | null;
  status: string;
};


export type ScopeBlocker = {
  code: string;
  severity: "info" | "warning" | "blocking";
  layer?: string | null;
  caps_ref?: string | null;
  required?: number | null;
  approved?: number | null;
  pending_review?: number | null;
};

export type LayerReadinessSummary = {
  layer: string;
  caps_ref: string;
  target: number;
  approved: number;
  pending_review: number;
  generated: number;
  validation_failed: number;
  rejected: number;
  quarantined: number;
  seeded_staging: number;
  promoted_production: number;
  stageable: number;
  status: string;
};

export type ScopeStagingVerificationReport = {
  scope_id: string;
  status: string;
  can_seed_staging: boolean;
  can_promote_production: boolean;
  blockers: ScopeBlocker[];
  layers: LayerReadinessSummary[];
  summary: Record<string, number | string | boolean>;
};

export type AllScopeStagingVerificationReport = {
  run_id?: string | null;
  status: string;
  can_seed_staging: boolean;
  can_promote_production: boolean;
  scopes: ScopeStagingVerificationReport[];
  summary: Record<string, number | string | boolean>;
  created_by?: string | null;
  created_at: string;
};

export type EtlStatus = {
  status: string;
  documents_indexed?: number;
  mcp_runtime_imported?: boolean;
};

export function fetchContentFactoryScopes() {
  return fetchApi<ContentScope[]>("/admin/content-factory/scopes");
}

export function fetchContentFactoryCoverage(scopeId: string) {
  return fetchApi<ScopeCoverageReport>(`/admin/content-factory/scopes/${scopeId}/coverage`);
}

export function fetchContentFactoryRuns() {
  return fetchApi<GenerationRun[]>("/admin/content-factory/runs");
}

export function fetchContentFactoryReviewQueue(params: Record<string, string> = {}) {
  const query = new URLSearchParams(params).toString();
  return fetchApi<ReviewQueuePage>(`/admin/content-factory/review-queue${query ? `?${query}` : ""}`);
}

export function fetchReviewBundle(artifactId: string) {
  return fetchApi<ReviewBundle>(`/admin/content-factory/artifacts/${artifactId}/review-bundle`);
}

export function bulkApproveReview(artifactIds: string[], notes: string) {
  return fetchApi<BulkReviewResponse>("/admin/content-factory/review/bulk-approve", {
    method: "POST",
    body: JSON.stringify({ artifact_ids: artifactIds, notes }),
  });
}

export function bulkRejectReview(artifactIds: string[], reason: string) {
  return fetchApi<BulkReviewResponse>("/admin/content-factory/review/bulk-reject", {
    method: "POST",
    body: JSON.stringify({ artifact_ids: artifactIds, reason }),
  });
}

export function bulkQuarantineReview(artifactIds: string[], reason: string) {
  return fetchApi<BulkReviewResponse>("/admin/content-factory/review/bulk-quarantine", {
    method: "POST",
    body: JSON.stringify({ artifact_ids: artifactIds, reason }),
  });
}

export function assignReviewBatch(artifactIds: string[], reviewerId: string) {
  return fetchApi<BulkReviewResponse>("/admin/content-factory/review-assignments/bulk", {
    method: "POST",
    body: JSON.stringify({ artifact_ids: artifactIds, reviewer_id: reviewerId }),
  });
}

export function fetchReviewerWorkload(reviewerId: string) {
  return fetchApi<ReviewerWorkload>(`/admin/content-factory/reviewers/${reviewerId}/workload`);
}

export function fetchAdminEtlStatus() {
  return fetchApi<EtlStatus>("/admin/etl/status");
}


export function runAllScopeStagingVerification() {
  return fetchApi<AllScopeStagingVerificationReport>("/admin/content-factory/staging-verification/all-scopes", {
    method: "POST",
  });
}

export function fetchScopeStagingReadiness(scopeId: string) {
  return fetchApi<ScopeStagingVerificationReport>(`/admin/content-factory/scopes/${scopeId}/staging-readiness`);
}


export function fetchGenerationRunTasks(runId: string) {
  return fetchApi<GenerationTask[]>(`/admin/content-factory/runs/${runId}/tasks`);
}

export function planMissingGenerationTasks(runId: string) {
  return fetchApi<GenerationPlanResponse>(`/admin/content-factory/runs/${runId}/plan-missing`, { method: "POST" });
}

export function executeGenerationRun(runId: string) {
  return fetchApi<GenerationExecutionResponse>(`/admin/content-factory/runs/${runId}/execute`, { method: "POST" });
}

export function executeGenerationTask(taskId: string) {
  return fetchApi<GenerationExecutionResponse>(`/admin/content-factory/tasks/${taskId}/execute`, { method: "POST" });
}

export function fetchGenerationExecutionReport(runId: string) {
  return fetchApi<GenerationExecutionReport>(`/admin/content-factory/runs/${runId}/execution-report`);
}
