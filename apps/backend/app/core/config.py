from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_url: str = "postgresql+asyncpg://cratekey:cratekey@localhost:5432/cratekey"
    getsongbpm_api_key: str = ""
    anthropic_api_key: str = ""
    title_parser_model: str = "claude-haiku-4-5-20251001"


@lru_cache
def get_settings() -> Settings:
    return Settings()
