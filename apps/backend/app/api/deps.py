from typing import Annotated

from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import Settings, get_settings
from app.db.session import get_session
from app.repositories.tracks import TrackRepository
from app.services.getsongbpm import GetSongBPMClient
from app.services.key_resolver import KeyResolver
from app.services.title_parser import TitleParser

SessionDep = Annotated[AsyncSession, Depends(get_session)]
SettingsDep = Annotated[Settings, Depends(get_settings)]


def get_track_repository(session: SessionDep) -> TrackRepository:
    return TrackRepository(session)


def get_getsongbpm_client(settings: SettingsDep) -> GetSongBPMClient:
    return GetSongBPMClient(api_key=settings.getsongbpm_api_key)


def get_title_parser(settings: SettingsDep) -> TitleParser:
    return TitleParser(api_key=settings.anthropic_api_key, model=settings.title_parser_model)


def get_key_resolver(
    tracks: Annotated[TrackRepository, Depends(get_track_repository)],
    getsongbpm: Annotated[GetSongBPMClient, Depends(get_getsongbpm_client)],
    title_parser: Annotated[TitleParser, Depends(get_title_parser)],
) -> KeyResolver:
    return KeyResolver(tracks=tracks, getsongbpm=getsongbpm, title_parser=title_parser)
