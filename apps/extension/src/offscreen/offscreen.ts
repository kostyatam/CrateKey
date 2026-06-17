import type { ExtensionMessage, AnalyzeAudioResult } from '../types/messages'
import { analyzeAudioUrl } from './analyze'

chrome.runtime.onMessage.addListener(
  (
    message: ExtensionMessage,
    _sender,
    sendResponse: (r: AnalyzeAudioResult | null) => void,
  ) => {
    if (message.type !== 'ANALYZE_AUDIO') return false
    analyzeAudioUrl(message.payload.audioUrl)
      .then(sendResponse)
      .catch(() => sendResponse(null))
    return true // async response
  },
)
