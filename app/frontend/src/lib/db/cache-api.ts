import { db, CachedLessonShell } from './schema';
import { enforceCacheBudget, CacheEvictionResult } from './storage-budget';

const FORBIDDEN_KEYS = ['progress', 'syncQueue', 'auditQueue', 'consentQueue'];

function validateLessonShell(lesson: Record<string, unknown>) {
  for (const k of FORBIDDEN_KEYS) {
    if (Object.prototype.hasOwnProperty.call(lesson, k)) {
      throw new Error(`Prohibited key in lesson shell: ${k}`);
    }
  }
}

export async function saveCachedLessonShell(lesson: CachedLessonShell): Promise<void> {
  validateLessonShell(lesson as unknown as Record<string, unknown>);
  const toSave: CachedLessonShell = {
    ...lesson,
    cachedAt: lesson.cachedAt ?? new Date().toISOString(),
    lastAccessedAt: lesson.lastAccessedAt ?? new Date().toISOString(),
    schemaVersion: 1,
  };

  await db.cachedLessons.put(toSave);
  await enforceCacheBudget();
}

export async function getCachedLessonShell(id: string): Promise<CachedLessonShell | null> {
  const rec = await db.cachedLessons.get(id);
  if (!rec) return null;
  // update lastAccessedAt
  await db.cachedLessons.update(id, { lastAccessedAt: new Date().toISOString() });
  return { ...(rec as CachedLessonShell) };
}

export async function deleteCachedLessonShell(id: string): Promise<void> {
  await db.cachedLessons.delete(id);
}

export async function listCachedLessonShells(scope?: 'synthetic' | 'local-demo') {
  if (!scope) return db.cachedLessons.toArray();
  return db.cachedLessons.where('learnerScope').equals(scope).toArray();
}

export async function cacheStatusSummary(): Promise<{ totalBytes: number; count: number }> {
  const all = await db.cachedLessons.toArray();
  const total = all.reduce((s, r) => s + (r.sizeBytes || 0), 0);
  return { totalBytes: total, count: all.length };
}
