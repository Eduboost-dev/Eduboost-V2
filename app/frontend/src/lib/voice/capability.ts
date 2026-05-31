import type { VoiceCapability } from './types'

export function detectVoiceSupport(): VoiceCapability {
  if (typeof window === 'undefined') return { supported: false, recognitionApi: null }
  const win: any = window
  if ('webkitSpeechRecognition' in win) return { supported: true, recognitionApi: 'webkit' }
  if ('SpeechRecognition' in win) return { supported: true, recognitionApi: 'standard' }
  return { supported: false, recognitionApi: null }
}
