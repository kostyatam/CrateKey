from sqlmodel import Field, SQLModel


class Plan(SQLModel, table=True):
    __tablename__ = "plans"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)  # free | pro
    rate_limit_per_minute: int = 30
