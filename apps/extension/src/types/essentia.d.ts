// essentia.js ships without usable TypeScript types — declare the minimal
// surface we use so the rest of the codebase stays strictly typed.
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
