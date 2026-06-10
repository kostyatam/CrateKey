import type { TrackInfo } from '../../types/track'
import { runContentScript } from '../run'

/** Beatport shows the key on track pages — resolution step 1 (DOM parse). */
export async function detect(): Promise<TrackInfo | null> {
  if (!/\/track\//.test(location.pathname)) return null

  const title = document.title
  const artist = document.querySelector('[data-testid="artist-name"]')?.textContent?.trim()
  const track = document.querySelector('[data-testid="track-name"], h1')?.textContent?.trim()
  const key = findMetaValue('Key')

  if (!track && !title) return null

  return {
    platform: 'beatport',
    pageUrl: location.href,
    title,
    artist: artist || undefined,
    track: track || undefined,
    key: key || undefined,
  }
}

function findMetaValue(label: string): string | null {
  const items = document.querySelectorAll('[class*="MetaItem"], li, div')
  for (const item of items) {
    const labelEl = item.querySelector('span, dt')
    if (labelEl?.textContent?.trim() === label) {
      const value = item.querySelector('span:last-child, dd')?.textContent?.trim()
      if (value && value !== label) return value
    }
  }
  return null
}

runContentScript(detect)
