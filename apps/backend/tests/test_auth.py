"""Integration tests for Authentication API endpoints."""

import uuid
from collections.abc import Generator
from unittest.mock import MagicMock

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.database import get_db
from app.core.security import hash_password
from app.main import app
from app.modules.users.models import User


class InMemoryUserRepo:
    """Mock in-memory repository to test endpoints without requiring live DB."""

    def __init__(self) -> None:
        self.users_by_id: dict[uuid.UUID, User] = {}
        self.users_by_email: dict[str, User] = {}

    def get_by_id(self, user_id: uuid.UUID) -> User | None:
        return self.users_by_id.get(user_id)

    def get_by_email(self, email: str) -> User | None:
        return self.users_by_email.get(email.strip().lower())

    def create(self, user: User) -> User:
        self.users_by_id[user.id] = user
        self.users_by_email[user.email.strip().lower()] = user
        return user

    def update(self, user: User) -> User:
        self.users_by_id[user.id] = user
        self.users_by_email[user.email.strip().lower()] = user
        return user


@pytest.fixture
def mock_user_repo() -> InMemoryUserRepo:
    return InMemoryUserRepo()


@pytest.fixture(autouse=True)
def override_db_dependency(mock_user_repo: InMemoryUserRepo) -> Generator[None, None, None]:
    # Mock get_db session to inject InMemoryUserRepo via UserRepository monkeypatching or factory
    mock_session = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_session

    from app.modules.auth.router import get_auth_service
    from app.modules.auth.service import AuthService

    # Directly inject AuthService backed by mock_user_repo
    app.dependency_overrides[get_auth_service] = lambda: AuthService(mock_user_repo)  # type: ignore[arg-type]

    yield

    app.dependency_overrides.pop(get_db, None)
    app.dependency_overrides.pop(get_auth_service, None)


@pytest.mark.asyncio
async def test_register_success() -> None:
    transport = ASGITransport(app=app)
    payload = {
        "email": "agricultor@chokwe.mz",
        "password": "SenhaForte123!",
        "full_name": "Mateus Mondlane",
        "preferred_language": "pt",
    }
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/v1/auth/register", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "agricultor@chokwe.mz"
    assert data["full_name"] == "Mateus Mondlane"
    assert data["role"] == "player"
    assert "password" not in data
    assert "hashed_password" not in data


@pytest.mark.asyncio
async def test_register_duplicate_email_conflict(mock_user_repo: InMemoryUserRepo) -> None:
    # Pre-register user
    user = User(
        email="agricultor@chokwe.mz",
        hashed_password=hash_password("Senha123!"),
        full_name="Existing User",
    )
    mock_user_repo.create(user)

    transport = ASGITransport(app=app)
    payload = {
        "email": "agricultor@chokwe.mz",
        "password": "OutraSenha123!",
        "full_name": "Duplicate User",
    }
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/v1/auth/register", json=payload)

    assert response.status_code == 409
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "CONFLICT"
    assert "already registered" in data["error"]["message"]


@pytest.mark.asyncio
async def test_register_validation_error() -> None:
    transport = ASGITransport(app=app)
    # Password too short (< 8 chars)
    payload = {
        "email": "not-an-email",
        "password": "123",
        "full_name": "A",
    }
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/v1/auth/register", json=payload)

    assert response.status_code == 422
    data = response.json()
    assert data["error"]["code"] == "VALIDATION_ERROR"


@pytest.mark.asyncio
async def test_login_success(mock_user_repo: InMemoryUserRepo) -> None:
    user = User(
        email="player@zambezia.mz",
        hashed_password=hash_password("MinhaSenhaSegura123"),
        full_name="Helena Licungo",
    )
    mock_user_repo.create(user)

    transport = ASGITransport(app=app)
    payload = {
        "email": "player@zambezia.mz",
        "password": "MinhaSenhaSegura123",
    }
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/v1/auth/login", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["user"]["email"] == "player@zambezia.mz"
    assert "tokens" in data
    assert "access_token" in data["tokens"]
    assert "refresh_token" in data["tokens"]
    assert data["tokens"]["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_invalid_password(mock_user_repo: InMemoryUserRepo) -> None:
    user = User(
        email="player@zambezia.mz",
        hashed_password=hash_password("MinhaSenhaSegura123"),
        full_name="Helena Licungo",
    )
    mock_user_repo.create(user)

    transport = ASGITransport(app=app)
    payload = {
        "email": "player@zambezia.mz",
        "password": "SenhaErrada",
    }
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/v1/auth/login", json=payload)

    assert response.status_code == 401
    data = response.json()
    assert data["error"]["code"] == "UNAUTHORIZED"


@pytest.mark.asyncio
async def test_refresh_token_lifecycle(mock_user_repo: InMemoryUserRepo) -> None:
    user = User(
        email="player@tete.mz",
        hashed_password=hash_password("Senha12345!"),
        full_name="Alberto Zambeze",
    )
    mock_user_repo.create(user)

    transport = ASGITransport(app=app)
    # 1. Login to get refresh token
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        login_res = await client.post(
            "/api/v1/auth/login",
            json={"email": "player@tete.mz", "password": "Senha12345!"},
        )
        refresh_token = login_res.json()["tokens"]["refresh_token"]

        # 2. Call refresh endpoint
        refresh_res = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )

    assert refresh_res.status_code == 200
    data = refresh_res.json()
    assert "access_token" in data
    assert "refresh_token" in data
