"""Unit tests for password hashing and JWT security helpers."""

import uuid
from datetime import timedelta

import pytest

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.shared.exceptions import UnauthorizedException


def test_password_hashing_and_verification() -> None:
    raw_password = "SecurePassword123!"
    hashed = hash_password(raw_password)

    # Must be valid argon2 hash
    assert hashed.startswith("$argon2")
    assert verify_password(raw_password, hashed) is True
    assert verify_password("WrongPassword", hashed) is False


def test_access_token_creation_and_decoding() -> None:
    user_id = uuid.uuid4()
    token = create_access_token(user_id, role="player")

    payload = decode_token(token, expected_type="access")
    assert payload["sub"] == str(user_id)
    assert payload["role"] == "player"
    assert payload["type"] == "access"


def test_refresh_token_creation_and_decoding() -> None:
    user_id = uuid.uuid4()
    token = create_refresh_token(user_id)

    payload = decode_token(token, expected_type="refresh")
    assert payload["sub"] == str(user_id)
    assert payload["type"] == "refresh"


def test_decode_token_type_mismatch() -> None:
    user_id = uuid.uuid4()
    token = create_access_token(user_id)

    with pytest.raises(UnauthorizedException, match="Expected token of type 'refresh'"):
        decode_token(token, expected_type="refresh")


def test_decode_token_expired() -> None:
    user_id = uuid.uuid4()
    expired_token = create_access_token(user_id, expires_delta=timedelta(seconds=-1))

    with pytest.raises(UnauthorizedException, match="Token has expired"):
        decode_token(expired_token)


def test_decode_token_invalid() -> None:
    with pytest.raises(UnauthorizedException, match="Invalid authentication token"):
        decode_token("not.a.valid.jwt.token")
