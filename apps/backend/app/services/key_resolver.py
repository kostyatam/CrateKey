import time

import structlog

from app.repositories.tracks import TrackRepository
from app.schemas.resolve import ResolveRequest, ResolveResponse
from app.services.getsongbpm import GetSongBPMClient
from app.services.hashing import hash_artist_track, hash_audio_url
from app.services.title_parser import TitleParser

log = structlog.get_logger()


class KeyResolver:
    """Backend half of the resolution hierarchy: step 2 (cache) → step 3 (GetSongBPM)."""

    def __init__(
        self,
        tracks: TrackRepository,
        getsongbpm: GetSongBPMClient,
        title_parser: TitleParser,
    ) -> None:
        self._tracks = tracks
        self._getsongbpm = getsongbpm
        self._title_parser = title_parser

    async def resolve(self, request: ResolveRequest) -> ResolveResponse:
        started = time.monotonic()

        # Step 2: cache lookup by audio_url hash, then artist+track hash
        cached = await self._lookup_cache(request)
        if cached is not None:
            self._log(request, "cache", cache_hit=True, started=started, confidence="cache")
            return cached

        # Step 3: GetSongBPM — parse the title first if artist/track are missing
        artist, track = request.artist, request.track
        if not artist or not track:
            # TODO: cache parsed titles alongside track data — never re-parse the same URL
            parsed = await self._title_parser.parse(request.title)
            if parsed is not None:
                artist, track = parsed.artist, parsed.track

        if artist and track:
            found = await self._getsongbpm.search(artist, track)
            if found is not None and found.key is not None:
                await self._tracks.save(
                    audio_url_hash=hash_audio_url(request.audio_url) if request.audio_url else None,
                    artist_track_hash=hash_artist_track(artist, track),
                    artist=artist,
                    track=track,
                    key=found.key,
                    mode=found.mode,
                    bpm=found.bpm,
                    source="getsongbpm",
                    confidence="getsongbpm",
                )
                self._log(request, "getsongbpm", cache_hit=False, started=started, confidence="getsongbpm")
                return ResolveResponse(
                    key=found.key, mode=found.mode, bpm=found.bpm, confidence="getsongbpm"
                )

        # Step 5 (backend side): nothing found — extension may still try essentia (step 4)
        self._log(request, "none", cache_hit=False, started=started, confidence="none")
        return ResolveResponse(key=None, confidence="none")

    async def _lookup_cache(self, request: ResolveRequest) -> ResolveResponse | None:
        row = None
        if request.audio_url:
            row = await self._tracks.get_by_audio_url_hash(hash_audio_url(request.audio_url))
        if row is None and request.artist and request.track:
            row = await self._tracks.get_by_artist_track_hash(
                hash_artist_track(request.artist, request.track)
            )
        if row is None or row.key is None:
            return None
        return ResolveResponse(key=row.key, mode=row.mode, bpm=row.bpm, confidence="cache")

    def _log(
        self, request: ResolveRequest, source: str, *, cache_hit: bool, started: float, confidence: str
    ) -> None:
        track_hash = (
            hash_artist_track(request.artist, request.track)
            if request.artist and request.track
            else None
        )
        log.info(
            "track.resolved",
            source=source,
            cache_hit=cache_hit,
            track_hash=track_hash,
            duration_ms=int((time.monotonic() - started) * 1000),
            confidence=confidence,
        )
