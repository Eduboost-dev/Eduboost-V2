declare module 'dexie' {
  // Minimal ambient declarations used in the frontend until proper types are available.
  export default class Dexie {
    constructor(name?: string);
    version(versionNumber: number): { stores: (schema: Record<string, string>) => void };
  }

  export type Table<T, K> = {
    get(key: K): Promise<T | undefined>;
    put(item: T): Promise<K>;
    where(index: string): any;
  };

  export {};
}
