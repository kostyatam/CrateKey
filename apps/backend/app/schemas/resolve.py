from typing import Literal

from pydantic import BaseModel

Confidence = Literal["dom", "cache", "getsongbpm", "essentia", "none"]


class ResolveRequest(BaseModel):
    page_url: str
    title: str
    artist: str | None = None
    track: str | None = None
    audio_url: str | None = None
    platform: str | None = None


class ResolveResponse(BaseModel):
    key: str | None
    mode: str | None = None
    bpm: float | None = None
    confidence: Confidence


class CacheTrackRequest(BaseModel):
    """Extension reports an essentia result back for caching (step 4)."""

    audio_url: str | None = None
    artist: str | None = None
    track: str | None = None
    key: str | None
    mode: str | None = None
    bpm: float | None = None
    source: Literal["essentia"] = "essentia"


class ErrorResponse(BaseModel):
    error: str
    code: str
