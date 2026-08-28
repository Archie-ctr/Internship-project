"""Typed, environment-based configuration for the API.

Keeping configuration here prevents secrets and deployment-specific URLs from
being scattered through route handlers. Values come from environment variables
or a local `.env` file, never from hard-coded production secrets.
"""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "BizReg API"
    environment: str = "development"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"
    database_url: str
    redis_url: str
    document_storage_path: Path = Path("./storage/documents")

    # Auth values are declared early so their source is clear. They are used in Phase 3.
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    backend_cors_origins: str = "http://localhost:3000"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
