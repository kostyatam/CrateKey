import type { TrackInfo } from '../../types/track'
import { runContentScript } from '../run'

/** SoundCloud has no key on the page — backend lookup / essentia handle it. */
export async function detect(): Promise<TrackInfo | null> {
  const isTrackPage = document.querySelector('.listenEngagement, [class*="soundTitle"]') !== null
  if (!isTrackPage) return null

  const title = document.title
  const artist = document
    .querySelector('.soundTitle__username, [class*="usernameTitle"] a')
    ?.textContent?.trim()
  const track = document
    .querySelector('.soundTitle__title span, h1 [class*="title"]')
    ?.textContent?.trim()

  return {
    platform: 'soundcloud',
    pageUrl: location.href,
    title,
    artist: artist || undefined,
    track: track || undefined,
  }
}

runContentScript(detect)
