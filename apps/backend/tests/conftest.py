"""Shared fixtures: test DB, mock GetSongBPM client, mock Claude client.

Never calls real GetSongBPM or Anthropic APIs — see CLAUDE.md testing rules.
"""

from collections.abc import AsyncIterator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

import app.models  # noqa: F401 — register tables
from app.api.deps import get_getsongbpm_client, get_title_parser
from app.db.session import get_session
from app.main import app as fastapi_app
from app.services.getsongbpm import GetSongBPMClient, GetSongBPMResult
from app.services.title_parser import ParsedTitle, TitleParser


class MockGetSongBPMClient(GetSongBPMClient):
    def __init__(self, result: GetSongBPMResult | None = None) -> None:
        self.result = result
        self.calls: list[tuple[str, str]] = []

    async def search(self, artist: str, track: str) -> GetSongBPMResult | None:
        self.calls.append((artist, track))
        return self.result


class MockTitleParser(TitleParser):
    def __init__(self, parsed: ParsedTitle | None = None) -> None:
        self.parsed = parsed
        self.calls: list[str] = []

    async def parse(self, title: str) -> ParsedTitle | None:
        self.calls.append(title)
        return self.parsed


@pytest.fixture
async def session() -> AsyncIterator[AsyncSession]:
    engine = create_async_engine("sqlite+aiosqlite://")
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    async with AsyncSession(engine, expire_on_commit=False) as s:
        yield s
    await engine.dispose()


@pytest.fixture
def mock_getsongbpm() -> MockGetSongBPMClient:
    return MockGetSongBPMClient()


@pytest.fixture
def mock_title_parser() -> MockTitleParser:
    return MockTitleParser()


@pytest.fixture
async def client(
    session: AsyncSession,
    mock_getsongbpm: MockGetSongBPMClient,
    mock_title_parser: MockTitleParser,
) -> AsyncIterator[AsyncClient]:
    async def override_session() -> AsyncIterator[AsyncSession]:
        yield session

    fastapi_app.dependency_overrides[get_session] = override_session
    fastapi_app.dependency_overrides[get_getsongbpm_client] = lambda: mock_getsongbpm
    fastapi_app.dependency_overrides[get_title_parser] = lambda: mock_title_parser

    transport = ASGITransport(app=fastapi_app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c

    fastapi_app.dependency_overrides.clear()
