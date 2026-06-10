import { useEffect, useState } from 'react'
import type { KeyResult } from '../types/track'
import type { GetKeyResultMessage } from '../types/messages'

export function App() {
  const [result, setResult] = useState<KeyResult | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    void (async () => {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true })
      if (tab?.url) {
        const message: GetKeyResultMessage = {
          type: 'GET_KEY_RESULT',
          payload: { pageUrl: tab.url },
        }
        const response = (await chrome.runtime.sendMessage(message)) as KeyResult | null
        setResult(response)
      }
      setLoading(false)
    })()
  }, [])

  if (loading) return <Status text="Loading…" />
  if (!result || result.key === null) return <Status text="No key detected on this page" />

  return (
    <div style={{ padding: 16 }}>
      <div style={{ fontSize: 32, fontWeight: 700 }}>
        {result.key}
        {result.mode ? ` ${result.mode}` : ''}
      </div>
      {result.camelot && <div style={{ fontSize: 14, opacity: 0.8 }}>Camelot: {result.camelot}</div>}
      {result.bpm !== undefined && <div style={{ fontSize: 14, opacity: 0.8 }}>{result.bpm} BPM</div>}
      <div style={{ fontSize: 12, opacity: 0.5, marginTop: 8 }}>source: {result.confidence}</div>
    </div>
  )
}

function Status({ text }: { text: string }) {
  return <div style={{ padding: 16, fontSize: 14, opacity: 0.7 }}>{text}</div>
}
