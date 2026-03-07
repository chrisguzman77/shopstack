import os

from pydantic import BaseModel


class Settings(BaseModel):
    # Application metadata
    app_name: str = "notifications"
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    # Database connection
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://postgres:postgres@postgres:5432/notifications_db",
    )

    # Redis connection
    redis_url: str = os.getenv(
        "REDIS_URL",
        "redis://redis:6379/0",
    )

    # Redis stream configuration
    stream_name: str = os.getenv(
        "ORDERS_STREAM",
        "orders.events",
    )

    # Consumer group settings
    group_name: str = os.getenv(
        "NOTIFICATIONS_GROUP",
        "notifications",
    )

    consumer_name: str = os.getenv(
        "CONSUMER_NAME",
        "worker-1",
    )

    # Retry / dead-letter handling
    max_attempts: int = int(os.getenv("MAX_NOTIFICATION_ATTEMPTS", "5"))


settings = Settings()