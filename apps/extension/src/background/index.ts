import type { ExtensionMessage, AnalyzeAudioResult, KeyResultResponse } from '../types/messages'
import type { KeyResult, TrackInfo } from '../types/track'
import { resolveKey } from './resolver'
import { resolveViaBackend, cacheResult } from './api'

const resultsByPageUrl = new Map<string, KeyResult>()

chrome.runtime.onMessage.addListener(
  (message: ExtensionMessage, _sender, sendResponse: (r: KeyResultResponse) => void) => {
    if (message.type === 'TRACK_DETECTED') {
      void handleTrackDetected(message.payload)
      return false
    }
    if (message.type === 'GET_KEY_RESULT') {
      sendResponse(resultsByPageUrl.get(message.payload.pageUrl) ?? null)
      return false
    }
    return false
  },
)

async function handleTrackDetected(track: TrackInfo): Promise<void> {
  const result = await resolveKey(track, {
    resolveViaBackend,
    analyzeAudio,
    cacheResult,
  })
  resultsByPageUrl.set(track.pageUrl, result)
  await chrome.storage.session.set({ [track.pageUrl]: result }).catch(() => undefined)
}

/** Step 4 runs in an offscreen document because the SW has no AudioContext. */
async function analyzeAudio(audioUrl: string): Promise<AnalyzeAudioResult | null> {
  await ensureOffscreenDocument()
  try {
    return (await chrome.runtime.sendMessage({
      type: 'ANALYZE_AUDIO',
      payload: { audioUrl },
    })) as AnalyzeAudioResult | null
  } catch {
    return null
  }
}

async function ensureOffscreenDocument(): Promise<void> {
  const contexts = await chrome.runtime.getContexts({
    contextTypes: [chrome.runtime.ContextType.OFFSCREEN_DOCUMENT],
  })
  if (contexts.length > 0) return
  await chrome.offscreen.createDocument({
    url: 'src/offscreen/offscreen.html',
    reasons: [chrome.offscreen.Reason.AUDIO_PLAYBACK],
    justification: 'Decode audio and run essentia.js key detection',
  })
}
