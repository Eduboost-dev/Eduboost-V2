import { vi, afterEach } from 'vitest'

globalThis.fetch = vi.fn((input: any) => {
  const url = typeof input === 'string' ? input : input?.url
  if (url && url.includes('/v2/diagnostics/')) {
    return Promise.resolve({ ok: true, status: 200, json: async () => ({ session_id: 'sess-1', first_item: { item_id: 'ITEM_1', question_text: 'What is 2+2?', options: ['1','2','3','4'] } }) })
  }
  if (url && url.match(/\/v2\/diagnostics\/session\/[\w-]+\/respond/)) {
    return Promise.resolve({ ok: true, status: 200, json: async () => ({ is_complete: false, session_state: { progress: 1 } }) })
  }
  return jsonResponse({})
})

const createStorage = () => {
  let store: Record<string, string> = {}
  return {
    get length() {
      return Object.keys(store).length
    },
    clear: () => {
      store = {}
    },
    getItem: (key: string) => (key in store ? store[key] : null),
    setItem: (key: string, value: string) => {
      store[key] = value
    },
    removeItem: (key: string) => {
      delete store[key]
    },
    key: (index: number) => Object.keys(store)[index] ?? null,
  }
}

const localStorageMock = createStorage()
const sessionStorageMock = createStorage()

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
  writable: true,
})

Object.defineProperty(window, 'sessionStorage', {
  value: sessionStorageMock,
  writable: true,
})

afterEach(() => {
  vi.clearAllMocks()
})
import '@testing-library/jest-dom'
