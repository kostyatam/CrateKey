"""Unit tests for key_resolver — all external services mocked."""

from sqlmodel.ext.asyncio.session import AsyncSession

from app.repositories.tracks import TrackRepository
from app.schemas.resolve import ResolveRequest
from app.services.getsongbpm import GetSongBPMResult
from app.services.hashing import hash_artist_track
from app.services.key_resolver import KeyResolver
from app.services.title_parser import ParsedTitle
from tests.conftest import MockGetSongBPMClient, MockTitleParser


def make_resolver(
    session: AsyncSession,
    getsongbpm: MockGetSongBPMClient,
    title_parser: MockTitleParser,
) -> KeyResolver:
    return KeyResolver(
        tracks=TrackRepository(session),
        getsongbpm=getsongbpm,
        title_parser=title_parser,
    )


async def test_cache_hit_skips_getsongbpm(
    session: AsyncSession,
    mock_getsongbpm: MockGetSongBPMClient,
    mock_title_parser: MockTitleParser,
) -> None:
    repo = TrackRepository(session)
    await repo.save(
        audio_url_hash=None,
        artist_track_hash=hash_artist_track("deadmau5", "Strobe"),
        artist="deadmau5",
        track="Strobe",
        key="B",
        mode="major",
        bpm=128,
        source="getsongbpm",
        confidence="getsongbpm",
    )
    resolver = make_resolver(session, mock_getsongbpm, mock_title_parser)

    result = await resolver.resolve(
        ResolveRequest(page_url="https://x", title="t", artist="deadmau5", track="Strobe")
    )

    assert result.confidence == "cache"
    assert result.key == "B"
    assert mock_getsongbpm.calls == []


async def test_getsongbpm_hit_is_cached(
    session: AsyncSession,
    mock_title_parser: MockTitleParser,
) -> None:
    getsongbpm = MockGetSongBPMClient(GetSongBPMResult(key="F#m", mode="minor", bpm=124.0))
    resolver = make_resolver(session, getsongbpm, mock_title_parser)
    request = ResolveRequest(page_url="https://x", title="t", artist="Artist", track="Track")

    result = await resolver.resolve(request)
    assert result.confidence == "getsongbpm"
    assert result.key == "F#m"

    # Second call must come from cache, not the API
    again = await resolver.resolve(request)
    assert again.confidence == "cache"
    assert len(getsongbpm.calls) == 1


async def test_title_parsed_when_artist_missing(
    session: AsyncSession,
) -> None:
    getsongbpm = MockGetSongBPMClient(GetSongBPMResult(key="Am", mode="minor", bpm=120.0))
    title_parser = MockTitleParser(ParsedTitle(artist="Artist", track="Track"))
    resolver = make_resolver(session, getsongbpm, title_parser)

    result = await resolver.resolve(
        ResolveRequest(page_url="https://x", title="Artist - Track - YouTube")
    )

    assert title_parser.calls == ["Artist - Track - YouTube"]
    assert getsongbpm.calls == [("Artist", "Track")]
    assert result.confidence == "getsongbpm"


async def test_everything_misses_returns_none(
    session: AsyncSession,
    mock_getsongbpm: MockGetSongBPMClient,
    mock_title_parser: MockTitleParser,
) -> None:
    resolver = make_resolver(session, mock_getsongbpm, mock_title_parser)

    result = await resolver.resolve(ResolveRequest(page_url="https://x", title="unparseable"))

    assert result.key is None
    assert result.confidence == "none"
