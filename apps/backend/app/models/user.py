from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(SQLModel, table=True):
    """Auth-ready — populated later, see CLAUDE.md."""

    __tablename__ = "users"

    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    plan: str = Field(default="free", foreign_key="plans.name")
    created_at: datetime = Field(default_factory=_utcnow)
