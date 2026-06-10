import type { TrackInfo } from '../../types/track'
import { runContentScript } from '../run'

/** Bandcamp exposes a direct mp3 URL in TralbumData — enables essentia (step 4). */
export async function detect(): Promise<TrackInfo | null> {
  const trackTitle = document.querySelector('.trackTitle')?.textContent?.trim()
  if (!trackTitle) return null

  const artist = document.querySelector('#name-section h3 a, .albumTitle a')?.textContent?.trim()

  let audioUrl: string | undefined
  for (const script of document.querySelectorAll('script[data-tralbum]')) {
    const raw = script.getAttribute('data-tralbum')
    if (!raw) continue
    try {
      const data: unknown = JSON.parse(raw)
      audioUrl = extractStreamUrl(data)
      if (audioUrl) break
    } catch {
      // malformed embed data — fall through to name-based lookup
    }
  }

  return {
    platform: 'bandcamp',
    pageUrl: location.href,
    title: document.title,
    artist: artist || undefined,
    track: trackTitle,
    audioUrl,
  }
}

function extractStreamUrl(data: unknown): string | undefined {
  if (typeof data !== 'object' || data === null) return undefined
  const trackinfo = (data as { trackinfo?: unknown }).trackinfo
  if (!Array.isArray(trackinfo) || trackinfo.length === 0) return undefined
  const file = (trackinfo[0] as { file?: Record<string, string> }).file
  if (!file) return undefined
  return Object.values(file)[0]
}

runContentScript(detect)
