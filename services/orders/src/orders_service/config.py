import os

from pydantic import BaseModel


class Settings(BaseModel):
    # Application metadata
    app_name: str = "orders"
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    # Database connection
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://postgres:postgres@postgres:5432/orders_db",
    )

    # Redis connection
    redis_url: str = os.getenv(
        "REDIS_URL",
        "redis://redis:6379/0",
    )

    # Auth service (used to verify JWTs)
    auth_service_url: str = os.getenv(
        "AUTH_SERVICE_URL",
        "http://auth:8001",
    )

    # Redis stream name for events
    orders_stream: str = os.getenv(
        "ORDERS_STREAM",
        "orders.events",
    )


settings = Settings()
