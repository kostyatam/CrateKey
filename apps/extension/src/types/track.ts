export type Confidence = 'dom' | 'cache' | 'getsongbpm' | 'essentia' | 'none'

export interface TrackInfo {
  platform: 'beatport' | 'traxsource' | 'soundcloud' | 'bandcamp' | 'youtube'
  pageUrl: string
  /** Raw page title — backend parses it into artist/track via LLM when needed. */
  title: string
  artist?: string
  track?: string
  /** Key read straight off the page DOM (Beatport, Traxsource). */
  key?: string
  /** Direct audio URL, when the platform exposes one — enables essentia analysis. */
  audioUrl?: string
}

export interface KeyResult {
  key: string | null
  mode?: 'major' | 'minor'
  camelot?: string
  bpm?: number
  confidence: Confidence
}
