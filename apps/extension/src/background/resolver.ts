import type { KeyResult, TrackInfo } from '../types/track'
import type { AnalyzeAudioResult } from '../types/messages'

export interface ResolverDeps {
  resolveViaBackend: (track: TrackInfo) => Promise<KeyResult>
  analyzeAudio: (audioUrl: string) => Promise<AnalyzeAudioResult | null>
  cacheResult: (track: TrackInfo, result: KeyResult) => Promise<void>
}

/**
 * Key resolution hierarchy — stop at first success:
 *  1. DOM parse (key already on the page)
 *  2. Backend cache lookup
 *  3. Backend GetSongBPM lookup
 *  4. essentia.js via offscreen document (direct audio URL only)
 *  5. { key: null, confidence: "none" }
 */
export async function resolveKey(
  track: TrackInfo,
  deps: ResolverDeps,
): Promise<KeyResult> {
  // 1. DOM
  if (track.key) {
    return { key: track.key, confidence: 'dom' }
  }

  // 2 + 3. Backend (cache, then GetSongBPM)
  const backendResult = await deps.resolveViaBackend(track)
  if (backendResult.confidence !== 'none' && backendResult.key !== null) {
    return backendResult
  }

  // 4. essentia.js — only when we have a direct audio URL
  if (track.audioUrl) {
    const analysis = await deps.analyzeAudio(track.audioUrl)
    if (analysis?.key) {
      const result: KeyResult = {
        key: analysis.key,
        mode: analysis.mode,
        bpm: analysis.bpm,
        confidence: 'essentia',
      }
      await deps.cacheResult(track, result)
      return result
    }
  }

  // 5. Nothing worked
  return { key: null, confidence: 'none' }
}
