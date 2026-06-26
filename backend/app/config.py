from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    ENVIRONMENT: str = "development"

    DATABASE_URL: str = "postgresql+asyncpg://blip:blippass@localhost:5432/blip"
    REDIS_URL: str = "redis://:redispass@localhost:6379/0"

    SECRET_KEY: str = "change-this-secret-key"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]

    GOOGLE_MAPS_API_KEY: str = ""
    AI_API_KEY: str = ""  # Get free key at https://console.groq.com

    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET: str = "blip-reports"
    MINIO_SECURE: bool = False

    N8N_WEBHOOK_BASE: str = "http://localhost:5678"
    N8N_WEBHOOK_SECRET: str = "change-this-webhook-secret"

    RAZORPAY_KEY_ID: str = ""
    RAZORPAY_KEY_SECRET: str = ""

    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""

    SENTRY_DSN: str = ""

    FREE_REPORT_COMPETITOR_LIMIT: int = 3
    MAX_SEARCH_RADIUS_METERS: int = 10000


settings = Settings()
