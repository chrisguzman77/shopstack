from __future__ import annotations

from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "auth"
    log_level: str = "INFO"
    database_url: str = "postgresql+asyncpg://postgres:postgres@postgres:5432/auth_db"
    redis_url: str = "redis://redis:6379/0"
    jwt_secret: str = "dev_secret_change_me"
    jwt_algorithm: str = "HS256"
    jwt_exp_minutes: int = 30


settings = Settings()