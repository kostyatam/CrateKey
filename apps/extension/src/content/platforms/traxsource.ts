import type { TrackInfo } from '../../types/track'
import { runContentScript } from '../run'

/** Traxsource lists the key in the track detail table — resolution step 1. */
export async function detect(): Promise<TrackInfo | null> {
  if (!/\/track\//.test(location.pathname)) return null

  const title = document.title
  const artist = document.querySelector('.com-artists a, .artist a')?.textContent?.trim()
  const track = document.querySelector('h1.title, .com-title')?.textContent?.trim()
  const key = document.querySelector('.key')?.textContent?.trim()

  if (!track && !title) return null

  return {
    platform: 'traxsource',
    pageUrl: location.href,
    title,
    artist: artist || undefined,
    track: track || undefined,
    key: key || undefined,
  }
}

runContentScript(detect)
