from datetime import datetime, timezone

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.track import Track


class TrackRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_audio_url_hash(self, audio_url_hash: str) -> Track | None:
        result = await self._session.exec(
            select(Track).where(Track.audio_url_hash == audio_url_hash)
        )
        return result.first()

    async def get_by_artist_track_hash(self, artist_track_hash: str) -> Track | None:
        result = await self._session.exec(
            select(Track).where(Track.artist_track_hash == artist_track_hash)
        )
        return result.first()

    async def save(
        self,
        *,
        audio_url_hash: str | None,
        artist_track_hash: str | None,
        artist: str | None,
        track: str | None,
        key: str | None,
        mode: str | None,
        bpm: float | None,
        source: str,
        confidence: str,
    ) -> Track:
        """Upsert a cached result. Saves under both hash keys when both are known."""
        existing: Track | None = None
        if audio_url_hash:
            existing = await self.get_by_audio_url_hash(audio_url_hash)
        if existing is None and artist_track_hash:
            existing = await self.get_by_artist_track_hash(artist_track_hash)

        if existing is None:
            existing = Track(
                audio_url_hash=audio_url_hash,
                artist_track_hash=artist_track_hash,
                artist=artist,
                track=track,
                key=key,
                mode=mode,
                bpm=bpm,
                source=source,
                confidence=confidence,
            )
        else:
            existing.audio_url_hash = existing.audio_url_hash or audio_url_hash
            existing.artist_track_hash = existing.artist_track_hash or artist_track_hash
            existing.artist = artist or existing.artist
            existing.track = track or existing.track
            existing.key = key
            existing.mode = mode
            existing.bpm = bpm
            existing.source = source
            existing.confidence = confidence
            existing.updated_at = datetime.now(timezone.utc)

        self._session.add(existing)
        await self._session.commit()
        await self._session.refresh(existing)
        return existing
