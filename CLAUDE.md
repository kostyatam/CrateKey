# CrateKey — DJ Key Detector#

Browser extension + FastAPI backend that detects the musical key of tracks
on streaming platforms (SoundCloud, Bandcamp, YouTube, Beatport, etc.)

## Structure

```
apps/extension/   → Chrome Extension MV3 (TypeScript, Vite, React)
apps/backend/     → FastAPI (Python 3.12), managed by uv
docs/decisions/   → ADR files
```

Each app is fully independent with its own deps and tooling.
No shared packages, no workspaces, no root package manager.

## Commands

### Extension

```bash
cd apps/extension
npm install
npm run dev       # watch mode
npm run build     # production build → dist/
npm run test      # Vitest
npm run typecheck # tsc --noEmit
npm run lint      # ESLint
```

### Backend

```bash
cd apps/backend
uv sync                        # install deps
uv run fastapi dev app/main.py # dev server
uv run pytest                  # tests
uv run alembic upgrade head    # run migrations
uv run alembic revision --autogenerate -m "description"
```

### Local infra

```bash
docker-compose up # postgres only
```

## Architecture

### Key resolution hierarchy

Always resolve in this order — stop at first success:

1. [extension] DOM parse (key already on page — Beatport, Traxsource)
2. [backend] Cache lookup by `hash(audioUrl)` or `artist+track` hash
3. [backend] GetSongBPM API (via title → LLM parse → name-based search)
4. [extension] essentia.js via offscreen document (direct audio URL only)
5. Return `{ key: null, confidence: "none" }`

Note: Spotify audio-features is NOT available — endpoint deprecated for
new apps since Nov 27, 2024. Do not suggest or implement Spotify
audio-features integration. essentia.js is the primary audio analysis
engine, GetSongBPM is the primary lookup API.

### Extension message flow

```
content script → background SW → offscreen / backend API → popup
```

Content scripts are platform-specific and live in `src/content/platforms/`.
Each exports a single `detect(): Promise<TrackInfo | null>` function.
Background SW orchestrates all API calls — content scripts never call
the backend directly.

### LLM title parsing

Use `claude-haiku-4-5-20251001` for parsing raw page titles into
`{ artist, track }`. Always return JSON only — no preamble.
Cache parsed results alongside track data — never re-parse the same URL.

## Code conventions

### TypeScript (extension)

- ESModules only — no CommonJS
- Strict mode enabled
- Destructure imports: `import { foo } from 'bar'`
- All cross-context message types defined in `src/types/` inside extension
- No business logic in content scripts — only DOM reading + messaging
- Platform content scripts: one file per platform, named `{platform}.ts`

### Python (backend)

- Python 3.12, type hints everywhere
- `pydantic-settings` for config — no raw `os.environ`
- `structlog` for logging — always include `track_id`, `source`, `duration_ms`
- Repository pattern for DB access — services never import SQLModel directly
- Dependency injection via FastAPI `Depends`
- No bare `except` — always catch specific exceptions

### API

- All routes versioned under `/api/v1/`
- Every response includes `confidence: "dom" | "cache" | "getsongbpm" | "essentia" | "none"`
- Errors follow `{ error: string, code: string }` shape

## Testing

### Extension (Vitest)

- Unit test each platform's `detect()` with fixture HTML
- Mock `chrome.*` APIs via `vitest-chrome`
- Test key resolution hierarchy independently of platforms

### Backend (pytest)

- Fixtures in `tests/conftest.py`: test DB, mock GetSongBPM client, mock Claude client
- Unit tests for `key_resolver.py` — mock all external services
- Integration tests for `/api/v1/resolve` endpoint via `httpx.AsyncClient`
- Never call real GetSongBPM or Anthropic APIs in tests

## Logging conventions (structlog)

Every resolution logs:

```python
log.info("track.resolved",
    source="getsongbpm",       # dom | cache | getsongbpm | essentia | none
    cache_hit=False,
    track_hash="...",
    duration_ms=240,
    confidence="high")
```

## Database

### Key tables

- `tracks` — cached results (`audio_url_hash`, `artist_track_hash`, `key`, `mode`, `bpm`, `source`, `confidence`)
- `events` — analytics (`event_type`, `platform`, `user_id` nullable, `payload`, `created_at`)
- `users` — auth-ready (`id`, `email`, `plan`, `created_at`) — populated later
- `plans` — `free | pro` — rate limits enforced at middleware level

Cache keys: `audio_url_hash` for direct-media lookups,
`artist_track_hash` (normalized lowercase `artist|track`) for
name-based lookups. Save under both keys when both are known.

### Migrations

Always use Alembic. Never edit DB schema manually.
One migration per logical change — do not bundle unrelated changes.

## When compacting context

Preserve:

- The key resolution hierarchy (5 steps above)
- Current file being worked on and its purpose
- Any failing tests and their error messages
- Last migration name

## What NOT to do

- Do not add business logic to content scripts
- Do not call Anthropic or GetSongBPM APIs directly from the extension
- Do not use Spotify audio-features / audio-analysis — deprecated for new apps since Nov 2024
- Do not hardcode API keys — use `pydantic-settings` + `.env`
- Do not skip typing — no `any` without a comment explaining why
- Do not create new DB queries outside of `repositories/`
- Do not bundle multiple unrelated changes in one commit
