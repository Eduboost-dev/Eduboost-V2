import { expect, test } from 'vitest'
import { detectVoiceSupport } from '@/lib/voice/capability'

test('detectVoiceSupport returns false in node-like environment', () => {
  const orig = (globalThis as any).window
  try {
    delete (globalThis as any).window
    const cap = detectVoiceSupport()
    expect(cap.supported).toBe(false)
  } finally {
    if (orig) (globalThis as any).window = orig
  }
})
