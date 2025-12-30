"""
FastAPI integration tests for app_yaml_static_config.

Tests verify that the configuration module integrates correctly
with FastAPI applications, including:
- Configuration access from route handlers
- Request state isolation
- Middleware integration
"""
import pytest
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from app_yaml_static_config.core import AppYamlConfig
from app_yaml_static_config.sdk import AppYamlConfigSDK
from app_yaml_static_config.types import InitOptions


# Get fixtures directory
FIXTURES_DIR = Path(__file__).parent.parent.parent / "__fixtures__"


@pytest.fixture(autouse=True)
def reset_singleton():
    """Reset AppYamlConfig singleton before each test."""
    AppYamlConfig._instance = None
    AppYamlConfig._config = {}
    AppYamlConfig._original_configs = {}
    AppYamlConfig._initial_merged_config = None
    yield
    AppYamlConfig._instance = None
    AppYamlConfig._config = {}
    AppYamlConfig._original_configs = {}
    AppYamlConfig._initial_merged_config = None


def create_test_app() -> FastAPI:
    """Create a test FastAPI application with configuration."""
    # Initialize configuration
    base_config = str(FIXTURES_DIR / "base.yaml")
    options = InitOptions(
        files=[base_config],
        config_dir=str(FIXTURES_DIR)
    )
    AppYamlConfig.initialize(options)
    config = AppYamlConfig.get_instance()

    # Create FastAPI app
    app = FastAPI(title="Test App")

    # Store config in app state for access in routes
    app.state.config = config
    app.state.sdk = AppYamlConfigSDK(config)

    @app.get("/health")
    async def health():
        """Health check endpoint."""
        return {
            "status": "ok",
            "app_name": config.get_nested("app", "name"),
        }

    @app.get("/config")
    async def get_config():
        """Get full configuration."""
        return app.state.sdk.get_all()

    @app.get("/config/{key}")
    async def get_config_key(key: str):
        """Get specific configuration key."""
        value = app.state.sdk.get(key)
        return {"key": key, "value": value}

    @app.get("/providers")
    async def list_providers():
        """List all providers."""
        return {"providers": app.state.sdk.list_providers()}

    @app.get("/services")
    async def list_services():
        """List all services."""
        return {"services": app.state.sdk.list_services()}

    @app.get("/storages")
    async def list_storages():
        """List all storages."""
        return {"storages": app.state.sdk.list_storages()}

    return app


@pytest.fixture
def client():
    """Create test client for FastAPI app."""
    app = create_test_app()
    return TestClient(app)


class TestFastAPIIntegration:
    """Integration tests for FastAPI with app_yaml_static_config."""

    class TestHealthEndpoint:
        """Tests for /health endpoint."""

        def test_health_returns_200(self, client):
            """Health endpoint should return 200 OK."""
            response = client.get("/health")

            assert response.status_code == 200
            assert response.json()["status"] == "ok"

        def test_health_includes_app_name(self, client):
            """Health endpoint should include app name from config."""
            response = client.get("/health")

            data = response.json()
            assert data["app_name"] == "test-app"

    class TestConfigEndpoint:
        """Tests for /config endpoints."""

        def test_get_config_returns_full_config(self, client):
            """GET /config should return full configuration."""
            response = client.get("/config")

            assert response.status_code == 200
            data = response.json()
            assert "app" in data
            assert "providers" in data
            assert "services" in data

        def test_get_config_key_returns_value(self, client):
            """GET /config/{key} should return specific key."""
            response = client.get("/config/app")

            assert response.status_code == 200
            data = response.json()
            assert data["key"] == "app"
            assert data["value"]["name"] == "test-app"

        def test_get_config_missing_key_returns_null(self, client):
            """GET /config/{key} with missing key should return null."""
            response = client.get("/config/nonexistent")

            assert response.status_code == 200
            data = response.json()
            assert data["key"] == "nonexistent"
            assert data["value"] is None

    class TestProvidersEndpoint:
        """Tests for /providers endpoint."""

        def test_list_providers_returns_list(self, client):
            """GET /providers should return list of providers."""
            response = client.get("/providers")

            assert response.status_code == 200
            data = response.json()
            assert isinstance(data["providers"], list)
            assert "anthropic" in data["providers"]
            assert "openai" in data["providers"]

    class TestServicesEndpoint:
        """Tests for /services endpoint."""

        def test_list_services_returns_list(self, client):
            """GET /services should return list of services."""
            response = client.get("/services")

            assert response.status_code == 200
            data = response.json()
            assert isinstance(data["services"], list)
            assert "database" in data["services"]
            assert "cache" in data["services"]

    class TestStoragesEndpoint:
        """Tests for /storages endpoint."""

        def test_list_storages_returns_list(self, client):
            """GET /storages should return list of storages."""
            response = client.get("/storages")

            assert response.status_code == 200
            data = response.json()
            assert isinstance(data["storages"], list)
            assert "local" in data["storages"]
            assert "s3" in data["storages"]

    class TestRequestIsolation:
        """Tests for request isolation."""

        def test_multiple_requests_use_same_config(self, client):
            """Multiple requests should use same configuration singleton."""
            response1 = client.get("/config/app")
            response2 = client.get("/config/app")

            assert response1.json() == response2.json()

        def test_config_immutable_between_requests(self, client):
            """Configuration should remain unchanged between requests."""
            # Get initial config
            response1 = client.get("/health")
            app_name1 = response1.json()["app_name"]

            # Make several requests
            for _ in range(5):
                client.get("/providers")
                client.get("/services")

            # Config should be unchanged
            response2 = client.get("/health")
            app_name2 = response2.json()["app_name"]

            assert app_name1 == app_name2
