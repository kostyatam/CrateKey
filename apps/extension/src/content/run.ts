import type { TrackInfo } from '../types/track'
import type { TrackDetectedMessage } from '../types/messages'

/**
 * Shared content-script runner: detect once on load, re-detect on SPA
 * navigation. Messaging only — all resolution logic lives in the background SW.
 */
export function runContentScript(
  detect: () => Promise<TrackInfo | null>,
): void {
  let lastUrl = ''

  const send = async () => {
    if (location.href === lastUrl) return
    lastUrl = location.href
    const track = await detect()
    if (!track) return
    const message: TrackDetectedMessage = {
      type: 'TRACK_DETECTED',
      payload: track,
    }
    void chrome.runtime.sendMessage(message)
  }

  void send()

  // SPA platforms (SoundCloud, YouTube) navigate without page loads.
  const observer = new MutationObserver(() => void send())
  observer.observe(document.documentElement, { childList: true, subtree: true })
}
