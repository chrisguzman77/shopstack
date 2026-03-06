import os
from pydantic import BaseModel

class Settings(BaseModel):
    app_name: str = "auth"
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    database_url: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://...")
    redis_url: str = os.getenv("REDIS_URL", "redis://redis:6379/0")
    jwt_secret: str = os.getenv("JWT_SECRET", "dev_secret_change_me")
    jwt_algorithm: str = "HS256"
    jwt_exp_minutes: int = int(os.getenv("JWT_EXP_MINUTES", "30"))

settings = Settings()