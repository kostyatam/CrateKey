"""Integration tests for /api/v1 via httpx.AsyncClient."""

from httpx import AsyncClient

from app.services.getsongbpm import GetSongBPMResult
from tests.conftest import MockGetSongBPMClient


async def test_resolve_returns_none_confidence_when_unknown(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/resolve",
        json={"page_url": "https://soundcloud.com/a/b", "title": "some title"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["key"] is None
    assert body["confidence"] == "none"


async def test_resolve_via_getsongbpm(
    client: AsyncClient, mock_getsongbpm: MockGetSongBPMClient
) -> None:
    mock_getsongbpm.result = GetSongBPMResult(key="Gm", mode="minor", bpm=126.0)

    response = await client.post(
        "/api/v1/resolve",
        json={
            "page_url": "https://soundcloud.com/a/b",
            "title": "t",
            "artist": "Artist",
            "track": "Track",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["key"] == "Gm"
    assert body["confidence"] == "getsongbpm"


async def test_cache_track_then_resolve_hits_cache(client: AsyncClient) -> None:
    created = await client.post(
        "/api/v1/tracks",
        json={
            "audio_url": "https://cdn.example.com/a.mp3",
            "artist": "Artist",
            "track": "Track",
            "key": "D",
            "mode": "major",
            "bpm": 122,
        },
    )
    assert created.status_code == 201

    response = await client.post(
        "/api/v1/resolve",
        json={
            "page_url": "https://x",
            "title": "t",
            "audio_url": "https://cdn.example.com/a.mp3",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["key"] == "D"
    assert body["confidence"] == "cache"


async def test_validation_error_shape(client: AsyncClient) -> None:
    response = await client.post("/api/v1/resolve", json={})
    assert response.status_code == 422
    body = response.json()
    assert "error" in body
    assert body["code"] == "validation_error"
