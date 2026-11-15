"""Tests for application settings validation."""

import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_production_rejects_development_jwt_secret() -> None:
    with pytest.raises(ValidationError, match="Production requires a JWT_SECRET"):
        Settings(ENVIRONMENT="production")


def test_production_rejects_short_jwt_secret() -> None:
    with pytest.raises(ValidationError, match="Production requires a JWT_SECRET"):
        Settings(ENVIRONMENT="production", JWT_SECRET="short")


def test_production_accepts_long_custom_jwt_secret() -> None:
    config = Settings(ENVIRONMENT="production", JWT_SECRET="x" * 32)

    assert config.JWT_SECRET == "x" * 32
