import type { TrackInfo } from '../../types/track'
import { runContentScript } from '../run'

/** YouTube has no key and no stable direct audio URL — name-based lookup only. */
export async function detect(): Promise<TrackInfo | null> {
  if (!location.pathname.startsWith('/watch')) return null

  const title =
    document.querySelector('h1.ytd-watch-metadata yt-formatted-string')?.textContent?.trim() ??
    document.title.replace(/ - YouTube$/, '')

  if (!title) return null

  return {
    platform: 'youtube',
    pageUrl: location.href,
    title,
  }
}

runContentScript(detect)
