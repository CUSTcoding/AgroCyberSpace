"""Unit and integration tests for User model and UserRepository."""

import uuid
from unittest.mock import MagicMock

from app.modules.users.models import User
from app.modules.users.repository import UserRepository


def test_user_model_defaults() -> None:
    user = User(
        email="farmer@limpopo.mz",
        hashed_password="argon2_hashed_secret",
        full_name="Joao Chokwe",
    )
    assert user.role == "player"
    assert user.is_active is True
    assert user.preferred_language == "pt"
    assert user.selected_region_id is None
    assert "farmer@limpopo.mz" in repr(user)


def test_user_repository_get_by_id() -> None:
    mock_db = MagicMock()
    user_id = uuid.uuid4()
    expected_user = User(
        id=user_id,
        email="test@example.com",
        hashed_password="hash",
        full_name="Test User",
    )
    mock_db.scalars.return_value.first.return_value = expected_user

    repo = UserRepository(mock_db)
    result = repo.get_by_id(user_id)

    assert result == expected_user
    mock_db.scalars.assert_called_once()


def test_user_repository_get_by_email() -> None:
    mock_db = MagicMock()
    expected_user = User(
        email="test@example.com",
        hashed_password="hash",
        full_name="Test User",
    )
    mock_db.scalars.return_value.first.return_value = expected_user

    repo = UserRepository(mock_db)
    result = repo.get_by_email("  TEST@example.com  ")

    assert result == expected_user
    mock_db.scalars.assert_called_once()


def test_user_repository_create_and_update() -> None:
    mock_db = MagicMock()
    user = User(
        email="test@example.com",
        hashed_password="hash",
        full_name="Test User",
    )
    repo = UserRepository(mock_db)

    created = repo.create(user)
    assert created == user
    mock_db.add.assert_called_once_with(user)
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once_with(user)

    mock_db.commit.reset_mock()
    mock_db.refresh.reset_mock()

    user.full_name = "Updated Name"
    updated = repo.update(user)
    assert updated.full_name == "Updated Name"
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once_with(user)


def test_user_repository_list() -> None:
    mock_db = MagicMock()
    user1 = User(email="u1@example.com", hashed_password="h", full_name="U1")
    user2 = User(email="u2@example.com", hashed_password="h", full_name="U2")

    mock_db.scalar.return_value = 2
    mock_db.scalars.return_value.all.return_value = [user1, user2]

    repo = UserRepository(mock_db)
    items, total = repo.list(offset=0, limit=10)

    assert total == 2
    assert len(items) == 2
    assert items[0] == user1
