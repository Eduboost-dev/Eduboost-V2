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

export function fetchContentFactoryReviewQueue() {
  return fetchApi<ContentArtifact[]>("/admin/content-factory/review-queue");
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
