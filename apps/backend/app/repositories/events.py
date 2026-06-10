from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.event import Event


class EventRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def record(
        self,
        *,
        event_type: str,
        platform: str | None = None,
        user_id: int | None = None,
        payload: dict | None = None,
    ) -> Event:
        event = Event(
            event_type=event_type,
            platform=platform,
            user_id=user_id,
            payload=payload or {},
        )
        self._session.add(event)
        await self._session.commit()
        await self._session.refresh(event)
        return event
