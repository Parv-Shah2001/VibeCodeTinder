from functools import lru_cache
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    APP_NAME: str = "VibeCodeTinder"
    ENV: str = "development"
    SECRET_KEY: str = "change-me-super-secret-key-please-32-chars"
    API_V1_PREFIX: str = "/api/v1"

    DATABASE_URL: str = "sqlite:///./vibe.db"
    REDIS_URL: str = "redis://localhost:6379/0"

    S3_ENDPOINT_URL: str | None = None
    S3_ACCESS_KEY: str = "minioadmin"
    S3_SECRET_KEY: str = "minioadmin"
    S3_BUCKET_MEDIA: str = "vibe-media"
    S3_BUCKET_MESSAGE_MEDIA: str = "vibe-message-media"
    S3_REGION: str = "us-east-1"
    MEDIA_CDN_URL: str = "http://localhost:9000/vibe-media"

    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60
    JWT_REFRESH_EXPIRE_DAYS: int = 30

    MAX_PHOTOS_PER_USER: int = 9
    MAX_MEDIA_SIZE_MB: int = 20
    MESSAGE_RATE_LIMIT_PER_MINUTE: int = 60
    SWIPE_RATE_LIMIT_PER_MINUTE: int = 100

    RECOMMENDATION_CANDIDATE_LIMIT: int = 100
    RECOMMENDATION_GEO_RADIUS_KM_DEFAULT: int = 50
    RECOMMENDATION_CACHE_TTL_SECONDS: int = 300

    FRONTEND_URL: str = "http://localhost:5173"
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    @property
    def is_sqlite(self) -> bool:
        return self.DATABASE_URL.startswith("sqlite")

    @property
    def is_prod(self) -> bool:
        return self.ENV == "production"

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
