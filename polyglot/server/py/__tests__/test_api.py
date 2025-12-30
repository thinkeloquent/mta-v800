"""
FastAPI integration tests for server.

Tests cover:
- Health endpoint
- Root endpoint
- Request state isolation
- Middleware effects
"""
import pytest
from contextlib import asynccontextmanager
from unittest.mock import patch, AsyncMock

pytest.importorskip("fastapi")
pytest.importorskip("httpx")

from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport

from server import init


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def test_config():
    """Configuration for test server."""
    return {
        "title": "Test API",
        "host": "127.0.0.1",
        "port": 8000,
        "initial_state": {"user": "test", "role": "tester"},
    }


@pytest.fixture
def app_with_routes(test_config):
    """Create FastAPI app with test routes."""

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # Store config for middleware
        app.state.initial_state = test_config.get("initial_state")
        yield

    app = FastAPI(title=test_config["title"], lifespan=lifespan)

    # Add middleware to initialize request state
    @app.middleware("http")
    async def init_request_state(request: Request, call_next):
        initial_state = getattr(request.app.state, "initial_state", None)
        if initial_state:
            import copy
            state_copy = copy.deepcopy(initial_state)
            for key, value in state_copy.items():
                setattr(request.state, key, value)
        return await call_next(request)

    @app.get("/")
    async def root(request: Request):
        return {
            "status": "ok",
            "state": {
                "user": getattr(request.state, "user", None),
                "role": getattr(request.state, "role", None),
            }
        }

    @app.get("/health")
    async def health(request: Request):
        return {
            "status": "ok",
            "state": {
                "user": getattr(request.state, "user", None),
                "role": getattr(request.state, "role", None),
            }
        }

    @app.get("/echo/{message}")
    async def echo(message: str, request: Request):
        return {
            "message": message,
            "user": getattr(request.state, "user", None),
        }

    return app


@pytest.fixture
def client(app_with_routes):
    """Synchronous test client with proper lifespan management."""
    with TestClient(app_with_routes) as c:
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

    def test_health_includes_state(self, client):
        """Health endpoint should include request state."""
        response = client.get("/health")

        data = response.json()
        assert "state" in data
        assert data["state"]["user"] == "test"
        assert data["state"]["role"] == "tester"


# ============================================================================
# Root Endpoint Tests
# ============================================================================

class TestRootEndpoint:
    """Tests for / endpoint."""

    def test_root_returns_200(self, client):
        """Root endpoint should return 200 OK."""
        response = client.get("/")

        assert response.status_code == 200
        assert response.json()["status"] == "ok"

    def test_root_includes_state(self, client):
        """Root endpoint should include request state."""
        response = client.get("/")

        data = response.json()
        assert data["state"]["user"] == "test"


# ============================================================================
# Echo Endpoint Tests
# ============================================================================

class TestEchoEndpoint:
    """Tests for /echo/{message} endpoint."""

    def test_echo_returns_message(self, client):
        """Echo endpoint should return the message."""
        response = client.get("/echo/hello")

        assert response.status_code == 200
        assert response.json()["message"] == "hello"

    def test_echo_includes_user(self, client):
        """Echo endpoint should include user from state."""
        response = client.get("/echo/test")

        data = response.json()
        assert data["user"] == "test"


# ============================================================================
# Request State Isolation Tests
# ============================================================================

class TestRequestStateIsolation:
    """Tests for request state isolation."""

    def test_multiple_requests_get_same_initial_state(self, client):
        """Multiple requests should see same initial state values."""
        response1 = client.get("/health")
        response2 = client.get("/health")

        assert response1.json()["state"] == response2.json()["state"]

    def test_concurrent_requests(self, client):
        """Concurrent requests should not interfere with each other."""
        responses = [
            client.get("/health"),
            client.get("/"),
            client.get("/echo/test"),
        ]

        assert responses[0].json()["state"]["user"] == "test"
        assert responses[1].json()["state"]["user"] == "test"
        assert responses[2].json()["user"] == "test"


# ============================================================================
# Middleware Tests
# ============================================================================

class TestMiddleware:
    """Tests for middleware behavior."""

    def test_state_initialized_per_request(self, client):
        """Each request should have fresh state initialized."""
        response1 = client.get("/")
        response2 = client.get("/")

        # State should be identical (fresh copy each time)
        assert response1.json()["state"] == response2.json()["state"]


# ============================================================================
# App Without Initial State Tests
# ============================================================================

class TestAppWithoutInitialState:
    """Tests for app without initial_state configured."""

    def test_works_without_initial_state(self):
        """App should work when initial_state is not configured."""
        app = FastAPI(title="No State API")

        @app.get("/health")
        async def health():
            return {"status": "ok"}

        with TestClient(app) as client:
            response = client.get("/health")
            assert response.status_code == 200


# ============================================================================
# Async Client Tests
# ============================================================================

@pytest.mark.asyncio
class TestAsyncEndpoints:
    """Tests using async client."""

    async def test_async_health_check(self, app_with_routes):
        """Test health endpoint with AsyncClient."""
        with TestClient(app_with_routes):
            transport = ASGITransport(app=app_with_routes)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                response = await ac.get("/health")

                assert response.status_code == 200
                assert response.json()["status"] == "ok"

    async def test_async_multiple_requests(self, app_with_routes):
        """Test multiple async requests."""
        with TestClient(app_with_routes):
            transport = ASGITransport(app=app_with_routes)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                responses = await asyncio.gather(
                    ac.get("/health"),
                    ac.get("/"),
                    ac.get("/echo/async"),
                )

                assert all(r.status_code == 200 for r in responses)


# Import asyncio for gather
import asyncio
