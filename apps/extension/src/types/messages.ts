import type { KeyResult, TrackInfo } from './track'

export interface TrackDetectedMessage {
  type: 'TRACK_DETECTED'
  payload: TrackInfo
}

export interface GetKeyResultMessage {
  type: 'GET_KEY_RESULT'
  payload: { pageUrl: string }
}

export interface AnalyzeAudioMessage {
  type: 'ANALYZE_AUDIO'
  payload: { audioUrl: string }
}

export interface AnalyzeAudioResult {
  key: string | null
  mode?: 'major' | 'minor'
  bpm?: number
}

export type ExtensionMessage =
  | TrackDetectedMessage
  | GetKeyResultMessage
  | AnalyzeAudioMessage

export type KeyResultResponse = KeyResult | null
