"""
FastAPI integration tests for vault_file.

Tests cover:
- Lifespan context manager
- EnvStore initialization via FastAPI startup
- Request state isolation
- Error handling during startup
"""
import os
import tempfile
import pytest
from unittest.mock import patch, MagicMock
from contextlib import asynccontextmanager

# FastAPI imports - these may not be available in all environments
pytest.importorskip("fastapi")
pytest.importorskip("httpx")

from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport

from vault_file.env_store import EnvStore


# ============================================================================
# Test Fixtures
# ============================================================================
# Note: EnvStore singleton is reset by autouse fixture in conftest.py

@pytest.fixture
def temp_env_file_for_api():
    """Create a temporary .env file for API tests."""
    created_files = []

    def _create(content: str) -> str:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write(content)
            created_files.append(f.name)
            return f.name

    yield _create

    # Cleanup all created files
    for f in created_files:
        try:
            os.unlink(f)
        except:
            pass


@pytest.fixture
def create_test_app(temp_env_file_for_api):
    """Factory fixture to create FastAPI app with vault_file lifespan."""
    def _create_app(env_content: str = "TEST_API_KEY=test-secret-123\nDATABASE_URL=postgres://test"):
        env_path = temp_env_file_for_api(env_content)

        @asynccontextmanager
        async def lifespan(app: FastAPI):
            """Lifespan that initializes EnvStore."""
            result = EnvStore.on_startup(env_path)
            app.state.vault_loaded = result.total_vars_loaded
            yield

        app = FastAPI(lifespan=lifespan)

        @app.get("/health")
        async def health():
            return {
                "status": "ok",
                "vault_initialized": EnvStore.is_initialized()
            }

        @app.get("/secret/{key}")
        async def get_secret(key: str):
            value = EnvStore.get(key)
            return {
                "key": key,
                "exists": value is not None,
                "masked": "***" if value else None
            }

        @app.get("/secret-value/{key}")
        async def get_secret_value(key: str):
            """For testing only - returns actual value."""
            return {"key": key, "value": EnvStore.get(key)}

        return app

    return _create_app


@pytest.fixture
def app_with_vault_lifespan(create_test_app):
    """Create FastAPI app with vault_file lifespan."""
    return create_test_app()


@pytest.fixture
def client(app_with_vault_lifespan):
    """Synchronous test client with proper lifespan management."""
    # Use context manager to ensure lifespan events run
    with TestClient(app_with_vault_lifespan) as c:
        yield c


# ============================================================================
# Health Endpoint Tests
# ============================================================================

class TestHealthEndpoint:
    """Tests for /health endpoint."""

    def test_health_returns_200(self, client):
        """Health endpoint should return 200 OK."""
        response = client.get("/health")

        assert response.status_code == 200
        assert response.json()["status"] == "ok"

    def test_health_shows_vault_initialized(self, client):
        """Health endpoint should show vault initialized state."""
        response = client.get("/health")

        data = response.json()
        assert data["vault_initialized"] is True


# ============================================================================
# Secret Endpoint Tests
# ============================================================================

class TestSecretEndpoint:
    """Tests for /secret/{key} endpoint."""

    def test_get_existing_secret(self, client):
        """Should return exists=True for existing secret."""
        response = client.get("/secret/TEST_API_KEY")

        data = response.json()
        assert data["key"] == "TEST_API_KEY"
        assert data["exists"] is True
        assert data["masked"] == "***"

    def test_get_nonexistent_secret(self, client):
        """Should return exists=False for missing secret."""
        response = client.get("/secret/NONEXISTENT_KEY")

        data = response.json()
        assert data["key"] == "NONEXISTENT_KEY"
        assert data["exists"] is False

    def test_get_secret_value(self, client):
        """Should return actual secret value (test only)."""
        response = client.get("/secret-value/TEST_API_KEY")

        data = response.json()
        assert data["value"] == "test-secret-123"


# ============================================================================
# Lifespan Tests
# ============================================================================

class TestLifespan:
    """Tests for FastAPI lifespan integration."""

    def test_env_store_initialized_on_startup(self, client):
        """EnvStore should be initialized during app startup."""
        # Just accessing the client triggers startup
        response = client.get("/health")
        assert EnvStore.is_initialized()

    def test_vars_loaded_from_env_file(self, client):
        """Variables from .env file should be loaded."""
        # Trigger startup by making a request
        client.get("/health")
        assert EnvStore.get("TEST_API_KEY") == "test-secret-123"
        assert EnvStore.get("DATABASE_URL") == "postgres://test"


# ============================================================================
# Request Isolation Tests
# ============================================================================

class TestRequestIsolation:
    """Tests for request state isolation."""

    def test_multiple_requests_get_same_env_values(self, client):
        """Multiple requests should see same environment values."""
        response1 = client.get("/secret-value/TEST_API_KEY")
        response2 = client.get("/secret-value/TEST_API_KEY")

        assert response1.json()["value"] == response2.json()["value"]

    def test_concurrent_requests(self, client):
        """Concurrent requests should not interfere with each other."""
        # Make multiple requests
        responses = [
            client.get("/secret/TEST_API_KEY"),
            client.get("/secret/DATABASE_URL"),
            client.get("/secret/NONEXISTENT"),
        ]

        assert responses[0].json()["exists"] is True
        assert responses[1].json()["exists"] is True
        assert responses[2].json()["exists"] is False


# ============================================================================
# Error Handling Tests
# ============================================================================

class TestErrorHandling:
    """Tests for error handling during startup."""

    def test_app_starts_with_missing_env_file(self):
        """App should start even if .env file is missing."""

        @asynccontextmanager
        async def lifespan(app: FastAPI):
            EnvStore.on_startup("/nonexistent/.env")
            yield

        app = FastAPI(lifespan=lifespan)

        @app.get("/health")
        async def health():
            return {"status": "ok"}

        client = TestClient(app)
        response = client.get("/health")

        assert response.status_code == 200


# ============================================================================
# Async Client Tests
# ============================================================================

@pytest.mark.asyncio
class TestAsyncEndpoints:
    """Tests using async client."""

    async def test_async_health_check(self, create_test_app):
        """Test health endpoint with AsyncClient."""
        app = create_test_app()
        # Use TestClient context to trigger lifespan before async test
        with TestClient(app):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                response = await ac.get("/health")

                assert response.status_code == 200
                assert response.json()["status"] == "ok"

    async def test_async_secret_fetch(self, create_test_app):
        """Test secret endpoint with AsyncClient."""
        app = create_test_app()
        # Use TestClient context to trigger lifespan before async test
        with TestClient(app):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                response = await ac.get("/secret/TEST_API_KEY")

                assert response.status_code == 200
                assert response.json()["exists"] is True
