"""Integration tests for User Profile (/users/me) and Role Permissions."""

import uuid
from collections.abc import Generator
from typing import Annotated
from unittest.mock import MagicMock

import pytest
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials
from httpx import ASGITransport, AsyncClient

from app.core.database import get_db
from app.core.security import create_access_token, decode_token, hash_password
from app.main import app
from app.modules.auth.dependencies import get_current_user, http_bearer
from app.modules.users.models import User
from app.modules.users.router import get_user_service
from app.modules.users.service import UserService
from app.shared.exceptions import UnauthorizedException


class InMemoryUserRepo:
    """Mock repository for isolated HTTP testing."""

    def __init__(self) -> None:
        self.users: dict[uuid.UUID, User] = {}

    def get_by_id(self, user_id: uuid.UUID) -> User | None:
        return self.users.get(user_id)

    def get_by_email(self, email: str) -> User | None:
        for u in self.users.values():
            if u.email.strip().lower() == email.strip().lower():
                return u
        return None

    def create(self, user: User) -> User:
        self.users[user.id] = user
        return user

    def update(self, user: User) -> User:
        self.users[user.id] = user
        return user


@pytest.fixture
def repo() -> InMemoryUserRepo:
    return InMemoryUserRepo()


@pytest.fixture(autouse=True)
def override_deps(repo: InMemoryUserRepo) -> Generator[None, None, None]:
    mock_session = MagicMock()

    def override_get_db() -> Generator[MagicMock, None, None]:
        yield mock_session

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_user_service] = lambda: UserService(repo)  # type: ignore[arg-type]

    def custom_get_current_user(
        credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(http_bearer)],
    ) -> User:
        if not credentials or not credentials.credentials:
            raise UnauthorizedException("Authentication token is missing.")
        payload = decode_token(credentials.credentials, expected_type="access")
        user_uuid = uuid.UUID(payload["sub"])
        user = repo.get_by_id(user_uuid)
        if not user:
            raise UnauthorizedException("User associated with token not found.")
        if not user.is_active:
            raise UnauthorizedException("User account is disabled.")
        return user

    app.dependency_overrides[get_current_user] = custom_get_current_user

    yield

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_me_success(repo: InMemoryUserRepo) -> None:
    user = User(
        email="player@limpopo.mz",
        hashed_password=hash_password("Pass123!"),
        full_name="Samora Chokwe",
        role="player",
    )
    repo.create(user)
    token = create_access_token(user.id, role="player")

    transport = ASGITransport(app=app)
    headers = {"Authorization": f"Bearer {token}"}
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/users/me", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "player@limpopo.mz"
    assert data["full_name"] == "Samora Chokwe"
    assert data["role"] == "player"


@pytest.mark.asyncio
async def test_get_me_unauthorized() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/users/me")

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"


@pytest.mark.asyncio
async def test_patch_me_updates_profile(repo: InMemoryUserRepo) -> None:
    user = User(
        email="player@limpopo.mz",
        hashed_password=hash_password("Pass123!"),
        full_name="Samora Chokwe",
    )
    repo.create(user)
    token = create_access_token(user.id)

    new_region_id = str(uuid.uuid4())
    transport = ASGITransport(app=app)
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "full_name": "Samora Machel Mondlane",
        "preferred_language": "en",
        "selected_region_id": new_region_id,
    }
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.patch("/api/v1/users/me", json=payload, headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == "Samora Machel Mondlane"
    assert data["preferred_language"] == "en"
    assert data["selected_region_id"] == new_region_id


@pytest.mark.asyncio
async def test_admin_ping_access_control(repo: InMemoryUserRepo) -> None:
    admin = User(
        email="admin@agrosight.mz",
        hashed_password=hash_password("AdminPass123!"),
        full_name="System Admin",
        role="admin",
    )
    player = User(
        email="player@agrosight.mz",
        hashed_password=hash_password("PlayerPass123!"),
        full_name="Normal Player",
        role="player",
    )
    repo.create(admin)
    repo.create(player)

    admin_token = create_access_token(admin.id, role="admin")
    player_token = create_access_token(player.id, role="player")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Admin request should succeed
        res_admin = await client.get(
            "/api/v1/users/admin/ping",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert res_admin.status_code == 200
        assert res_admin.json()["admin_email"] == "admin@agrosight.mz"

        # Player request should fail with 403 Forbidden
        res_player = await client.get(
            "/api/v1/users/admin/ping",
            headers={"Authorization": f"Bearer {player_token}"},
        )
        assert res_player.status_code == 403
        assert res_player.json()["error"]["code"] == "FORBIDDEN"
