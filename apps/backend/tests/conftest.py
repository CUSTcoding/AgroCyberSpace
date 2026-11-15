"""Pytest global configuration and fixtures."""

from collections.abc import AsyncGenerator, Generator
from typing import Any

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.core.database import get_db
from app.main import app


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Provide an asynchronous HTTP client for testing API endpoints."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture(scope="session")
def test_engine() -> Any:
    """Provide an engine connected to the dedicated TEST_DATABASE_URL."""
    test_db_url = settings.sync_test_database_url
    if not test_db_url:
        pytest.skip("TEST_DATABASE_URL not configured. Skipping live database tests.")
    engine = create_engine(
        test_db_url,
        pool_pre_ping=True,
        connect_args={"connect_timeout": 10},
    )
    return engine


@pytest.fixture
def db_session(test_engine: Any) -> Generator[Session, None, None]:
    """Provide an isolated database session rolled back after every test."""
    connection = test_engine.connect()
    transaction = connection.begin()
    session_factory = sessionmaker(autocommit=False, autoflush=False, bind=connection)
    session = session_factory()

    # Override get_db dependency in FastAPI app
    app.dependency_overrides[get_db] = lambda: session

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()
        app.dependency_overrides.pop(get_db, None)
