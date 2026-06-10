from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.deps import get_key_resolver, get_track_repository
from app.repositories.tracks import TrackRepository
from app.schemas.resolve import CacheTrackRequest, ResolveRequest, ResolveResponse
from app.services.hashing import hash_artist_track, hash_audio_url
from app.services.key_resolver import KeyResolver

router = APIRouter(prefix="/api/v1")


@router.post("/resolve", response_model=ResolveResponse)
async def resolve(
    request: ResolveRequest,
    resolver: Annotated[KeyResolver, Depends(get_key_resolver)],
) -> ResolveResponse:
    return await resolver.resolve(request)


@router.post("/tracks", response_model=ResolveResponse, status_code=201)
async def cache_track(
    request: CacheTrackRequest,
    tracks: Annotated[TrackRepository, Depends(get_track_repository)],
) -> ResolveResponse:
    """Extension reports an essentia result (step 4) so future lookups hit the cache."""
    await tracks.save(
        audio_url_hash=hash_audio_url(request.audio_url) if request.audio_url else None,
        artist_track_hash=(
            hash_artist_track(request.artist, request.track)
            if request.artist and request.track
            else None
        ),
        artist=request.artist,
        track=request.track,
        key=request.key,
        mode=request.mode,
        bpm=request.bpm,
        source=request.source,
        confidence="essentia",
    )
    return ResolveResponse(key=request.key, mode=request.mode, bpm=request.bpm, confidence="essentia")
