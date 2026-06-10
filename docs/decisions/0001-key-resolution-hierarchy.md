# ADR 0001: Key resolution hierarchy

## Status

Accepted

## Decision

Resolve track keys in a fixed order, stopping at the first success:

1. [extension] DOM parse — key already on the page (Beatport, Traxsource)
2. [backend] Cache lookup by `hash(audioUrl)` or `artist+track` hash
3. [backend] GetSongBPM API (title → LLM parse → name-based search)
4. [extension] essentia.js via offscreen document (direct audio URL only)
5. Return `{ key: null, confidence: "none" }`

## Context

Spotify audio-features is deprecated for new apps (Nov 27, 2024) and must not
be used. essentia.js is the primary audio analysis engine; GetSongBPM is the
primary lookup API. Cheap signals (DOM, cache) run before paid/slow ones
(LLM parse + API search, WASM audio analysis).
