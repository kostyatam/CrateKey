import type { KeyResult, TrackInfo } from '../types/track'

const API_BASE = 'http://localhost:8000/api/v1'

/** Steps 2–3 of the hierarchy run server-side behind one endpoint. */
export async function resolveViaBackend(track: TrackInfo): Promise<KeyResult> {
  const res = await fetch(`${API_BASE}/resolve`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      page_url: track.pageUrl,
      title: track.title,
      artist: track.artist ?? null,
      track: track.track ?? null,
      audio_url: track.audioUrl ?? null,
      platform: track.platform,
    }),
  })
  if (!res.ok) return { key: null, confidence: 'none' }
  return (await res.json()) as KeyResult
}

/** Persist an essentia result so the next lookup is a cache hit. */
export async function cacheResult(track: TrackInfo, result: KeyResult): Promise<void> {
  await fetch(`${API_BASE}/tracks`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      audio_url: track.audioUrl ?? null,
      artist: track.artist ?? null,
      track: track.track ?? null,
      key: result.key,
      mode: result.mode ?? null,
      bpm: result.bpm ?? null,
      source: 'essentia',
    }),
  }).catch(() => {
    // caching is best-effort; the user already has their result
  })
}
