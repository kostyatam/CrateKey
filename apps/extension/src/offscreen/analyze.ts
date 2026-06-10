import type { AnalyzeAudioResult } from '../types/messages'

const SAMPLE_RATE = 22050
const MAX_SECONDS = 120 // first two minutes are enough for key detection

/** Fetch a direct audio URL, decode it, and run essentia.js key extraction. */
export async function analyzeAudioUrl(audioUrl: string): Promise<AnalyzeAudioResult | null> {
  const response = await fetch(audioUrl)
  if (!response.ok) return null
  const buffer = await response.arrayBuffer()

  const ctx = new OfflineAudioContext(1, SAMPLE_RATE * MAX_SECONDS, SAMPLE_RATE)
  const decoded = await ctx.decodeAudioData(buffer)
  const mono = decoded.getChannelData(0)

  const { Essentia, EssentiaWASM } = await import('essentia.js')
  const essentia = new Essentia(EssentiaWASM)

  const signal = essentia.arrayToVector(mono)
  try {
    const keyResult = essentia.KeyExtractor(signal, true, 4096, 4096, 12, 3500, 60, 25, 0.2)
    const bpmResult = essentia.PercivalBpmEstimator(signal, 1024, 2048, 128, 128, 210, 50, SAMPLE_RATE)
    return {
      key: keyResult.key ?? null,
      mode: keyResult.scale === 'major' ? 'major' : 'minor',
      bpm: Math.round(bpmResult.bpm),
    }
  } finally {
    signal.delete()
  }
}
