from pydantic import BaseModel

class Settings(BaseModel):
    log_level: str = "INFO"
    database_url: str = "postgresql+asyncpg://postgres:postgres@postgres:5432/orders_db"
    redis_url: str = "redis://redis:6379/0"
    auth_service_url: str = "http://auth:8001"

settings = Settings()