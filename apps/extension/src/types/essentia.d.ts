// essentia.js@0.1.3 ships .d.ts files in dist/, but its package.json doesn't
// reference them (no `types` field / `exports` map / root index.d.ts), so they
// aren't auto-discovered — and they're almost entirely `any` (e.g. KeyExtractor
// returns `any`) and shaped around a default export, not the named
// `{ Essentia, EssentiaWASM }` import we use. Declare the precise surface we
// need so the rest of the codebase stays strictly typed.
declare module 'essentia.js' {
  export interface EssentiaVector {
    delete(): void
  }

  export class Essentia {
    constructor(wasm: unknown)
    arrayToVector(data: Float32Array): EssentiaVector
    KeyExtractor(
      signal: EssentiaVector,
      averageDetuningCorrection?: boolean,
      frameSize?: number,
      hopSize?: number,
      hpcpSize?: number,
      maxFrequency?: number,
      maximumSpectralPeaks?: number,
      minFrequency?: number,
      pcpThreshold?: number,
    ): { key: string; scale: string; strength: number }
    PercivalBpmEstimator(
      signal: EssentiaVector,
      frameSize?: number,
      frameSizeOSS?: number,
      hopSize?: number,
      hopSizeOSS?: number,
      maxBPM?: number,
      minBPM?: number,
      sampleRate?: number,
    ): { bpm: number }
  }

  export const EssentiaWASM: unknown
}
