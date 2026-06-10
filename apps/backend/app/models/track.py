from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Track(SQLModel, table=True):
    __tablename__ = "tracks"

    id: int | None = Field(default=None, primary_key=True)
    audio_url_hash: str | None = Field(default=None, index=True, unique=True)
    artist_track_hash: str | None = Field(default=None, index=True, unique=True)
    artist: str | None = None
    track: str | None = None
    key: str | None = None
    mode: str | None = None
    bpm: float | None = None
    source: str  # dom | cache | getsongbpm | essentia
    confidence: str
    created_at: datetime = Field(default_factory=_utcnow)
    updated_at: datetime = Field(default_factory=_utcnow)
