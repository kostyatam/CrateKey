import hashlib


def hash_audio_url(audio_url: str) -> str:
    return hashlib.sha256(audio_url.encode("utf-8")).hexdigest()


def hash_artist_track(artist: str, track: str) -> str:
    """Normalized lowercase `artist|track` hash — see CLAUDE.md cache keys."""
    normalized = f"{artist.strip().lower()}|{track.strip().lower()}"
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()
