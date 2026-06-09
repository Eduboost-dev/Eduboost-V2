import Dexie, { Table } from 'dexie';

export interface CachedLessonShell {
  id: string;
  lessonId: string;
  subject: string;
  title: string;
  content: unknown; // structured lesson shell JSON
  cachedAt: string; // ISO
  lastAccessedAt: string; // ISO
  sizeBytes: number;
  schemaVersion: number; // 1
  learnerScope: 'synthetic' | 'local-demo';
}

export interface SystemMetadata {
  key: string;
  value: string;
  updatedAt: string;
}

export class EduBoostOfflineDB extends Dexie {
  cachedLessons!: Table<CachedLessonShell, string>;
  metadata!: Table<SystemMetadata, string>;

  constructor() {
    super('EduBoostOfflineDB');
    this.version(1).stores({
      cachedLessons: 'id, lessonId, subject, lastAccessedAt',
      metadata: 'key',
    });
  }
}

// Export a lazy proxy that instantiates the real Dexie DB only on first use.
function createLazyDb(): EduBoostOfflineDB {
  // Use a Proxy to defer construction until a property is accessed.
  let real: EduBoostOfflineDB | null = null;
  const ensure = () => {
    if (!real) real = new EduBoostOfflineDB();
    return real;
  };

  // Return a Proxy typed as EduBoostOfflineDB but lazily delegating.
  const proxy = new Proxy(
    {},
    {
      get(_, prop) {
        const r = ensure();
        return r[prop as keyof EduBoostOfflineDB];
      },
      set(_, prop, value) {
        const r = ensure();
        (r as unknown as Record<string, unknown>)[prop as string] = value;
        return true;
      },
    }
  ) as unknown as EduBoostOfflineDB;

  return proxy;
}

export const db = createLazyDb();
