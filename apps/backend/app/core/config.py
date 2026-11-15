"""Application configuration and environment settings."""

from __future__ import annotations

import json
from typing import Any

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """AgroSight Fair Space API settings."""

    # API Metadata
    PROJECT_NAME: str = "AgroSight Fair Space API"
    VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"
    API_V1_PREFIX: str = "/api/v1"

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    # Database
    DATABASE_URL: str = ""
    TEST_DATABASE_URL: str = ""
    DATABASE_URL_DIRECT: str | None = None

    # Security & JWT
    JWT_SECRET: str = "insecure_dev_jwt_secret_must_change_in_production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Storage
    STORAGE_BACKEND: str = "local"
    STORAGE_PATH: str = "./storage"

    # Earth Observation Credentials
    EARTHDATA_TOKEN: str | None = None
    USGS_USERNAME: str | None = None
    USGS_TOKEN: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    @model_validator(mode="after")
    def validate_production_jwt_secret(self) -> Settings:
        """Prevent deployments from using the public development signing key."""
        if self.ENVIRONMENT.lower() in {"prod", "production"} and (
            self.JWT_SECRET == "insecure_dev_jwt_secret_must_change_in_production"
            or len(self.JWT_SECRET) < 32
        ):
            raise ValueError("Production requires a JWT_SECRET of at least 32 characters.")
        return self

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Any) -> list[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        if isinstance(v, str) and v.startswith("["):
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return [str(item) for item in parsed]
            except Exception:
                pass
        if isinstance(v, list):
            return [str(item) for item in v]
        return ["http://localhost:3000"]

    @property
    def sync_database_url(self) -> str:
        """Ensure DATABASE_URL uses the postgresql+psycopg dialect."""
        url = self.DATABASE_URL
        if url.startswith("postgres://"):
            return url.replace("postgres://", "postgresql+psycopg://", 1)
        if url.startswith("postgresql://") and not url.startswith("postgresql+"):
            return url.replace("postgresql://", "postgresql+psycopg://", 1)
        return url

    @property
    def sync_test_database_url(self) -> str:
        """Ensure TEST_DATABASE_URL uses the postgresql+psycopg dialect."""
        url = self.TEST_DATABASE_URL
        if url.startswith("postgres://"):
            return url.replace("postgres://", "postgresql+psycopg://", 1)
        if url.startswith("postgresql://") and not url.startswith("postgresql+"):
            return url.replace("postgresql://", "postgresql+psycopg://", 1)
        return url


settings = Settings()
