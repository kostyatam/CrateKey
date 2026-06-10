import { describe, it, expect, vi } from 'vitest'
import { resolveKey, type ResolverDeps } from '../src/background/resolver'
import type { TrackInfo } from '../src/types/track'

const baseTrack: TrackInfo = {
  platform: 'soundcloud',
  pageUrl: 'https://soundcloud.com/artist/track',
  title: 'Artist - Track',
}

function makeDeps(overrides: Partial<ResolverDeps> = {}): ResolverDeps {
  return {
    resolveViaBackend: vi.fn().mockResolvedValue({ key: null, confidence: 'none' }),
    analyzeAudio: vi.fn().mockResolvedValue(null),
    cacheResult: vi.fn().mockResolvedValue(undefined),
    ...overrides,
  }
}

describe('resolveKey hierarchy', () => {
  it('step 1: returns DOM key without touching the backend', async () => {
    const deps = makeDeps()
    const result = await resolveKey({ ...baseTrack, key: 'A Minor' }, deps)

    expect(result).toEqual({ key: 'A Minor', confidence: 'dom' })
    expect(deps.resolveViaBackend).not.toHaveBeenCalled()
    expect(deps.analyzeAudio).not.toHaveBeenCalled()
  })

  it('step 2/3: returns backend result (cache or getsongbpm)', async () => {
    const deps = makeDeps({
      resolveViaBackend: vi.fn().mockResolvedValue({ key: 'F# Minor', bpm: 124, confidence: 'cache' }),
    })
    const result = await resolveKey(baseTrack, deps)

    expect(result.key).toBe('F# Minor')
    expect(result.confidence).toBe('cache')
    expect(deps.analyzeAudio).not.toHaveBeenCalled()
  })

  it('step 4: falls back to essentia when backend misses and audioUrl exists', async () => {
    const deps = makeDeps({
      analyzeAudio: vi.fn().mockResolvedValue({ key: 'G', mode: 'major', bpm: 122 }),
    })
    const track = { ...baseTrack, audioUrl: 'https://cdn.example.com/a.mp3' }
    const result = await resolveKey(track, deps)

    expect(result).toEqual({ key: 'G', mode: 'major', bpm: 122, confidence: 'essentia' })
    expect(deps.cacheResult).toHaveBeenCalledWith(track, result)
  })

  it('step 4 skipped without an audioUrl', async () => {
    const deps = makeDeps()
    const result = await resolveKey(baseTrack, deps)

    expect(deps.analyzeAudio).not.toHaveBeenCalled()
    expect(result).toEqual({ key: null, confidence: 'none' })
  })

  it('step 5: returns none when everything misses', async () => {
    const deps = makeDeps()
    const result = await resolveKey({ ...baseTrack, audioUrl: 'https://cdn.example.com/a.mp3' }, deps)

    expect(result).toEqual({ key: null, confidence: 'none' })
  })
})
