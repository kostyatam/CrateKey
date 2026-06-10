import { describe, it, expect, beforeEach } from 'vitest'
import { readFileSync } from 'node:fs'
import { detect } from '../../src/content/platforms/beatport'

// Path is relative to the package root — vitest's cwd.
const fixture = readFileSync('tests/fixtures/beatport.html', 'utf-8')

describe('beatport detect()', () => {
  beforeEach(() => {
    document.documentElement.innerHTML = fixture
    window.history.pushState({}, '', '/track/strobe-original-mix/12345')
  })

  it('parses key, artist and track from the DOM', async () => {
    const track = await detect()
    expect(track).not.toBeNull()
    expect(track?.platform).toBe('beatport')
    expect(track?.key).toBe('B Major')
    expect(track?.artist).toBe('deadmau5')
    expect(track?.track).toBe('Strobe (Original Mix)')
  })

  it('returns null on non-track pages', async () => {
    window.history.pushState({}, '', '/genre/house/5')
    const track = await detect()
    expect(track).toBeNull()
  })
})
