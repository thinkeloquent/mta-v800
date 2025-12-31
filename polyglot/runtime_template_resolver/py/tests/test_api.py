"""
FastAPI integration tests.

Tests cover:
- Dependency injection
- Request-scoped resolver
- Endpoint testing using TestClient
"""
import pytest
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient

from runtime_template_resolver import ResolverOptions, MissingStrategy
from runtime_template_resolver.integrations.fastapi_utils import (
    create_resolver_dependency,
    ConfiguredResolverProtocol,
)


class TestFastAPIIntegration:
    """Tests for FastAPI integration."""

    @pytest.fixture
    def app(self):
        """Create test FastAPI application."""
        app = FastAPI(title="Test API")

        get_resolver = create_resolver_dependency()

        @app.get("/resolve")
        def resolve_endpoint(
            template: str,
            resolver: ConfiguredResolverProtocol = Depends(get_resolver)
        ):
            context = {"name": "World", "count": 42}
            result = resolver.resolve(template, context)
            return {"result": result}

        @app.post("/resolve-object")
        def resolve_object_endpoint(
            data: dict,
            resolver: ConfiguredResolverProtocol = Depends(get_resolver)
        ):
            context = {"name": "World", "count": 42}
            result = resolver.resolve_object(data, context)
            return {"result": result}

        return app

    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return TestClient(app)

    class TestResolveEndpoint:
        """Tests for /resolve endpoint."""

        def test_resolve_simple_template(self, client):
            """Resolves simple template via API."""
            response = client.get("/resolve", params={"template": "Hello {{name}}!"})
            assert response.status_code == 200
            assert response.json()["result"] == "Hello World!"

        def test_resolve_numeric_value(self, client):
            """Resolves numeric value via API."""
            response = client.get("/resolve", params={"template": "Count: {{count}}"})
            assert response.status_code == 200
            assert response.json()["result"] == "Count: 42"

        def test_resolve_missing_value(self, client):
            """Handles missing value via API."""
            response = client.get("/resolve", params={"template": "Missing: {{missing}}"})
            assert response.status_code == 200
            assert response.json()["result"] == "Missing: "

    class TestResolveObjectEndpoint:
        """Tests for /resolve-object endpoint."""

        def test_resolve_object_dict(self, client):
            """Resolves object via API."""
            response = client.post(
                "/resolve-object",
                json={"greeting": "Hello {{name}}!"}
            )
            assert response.status_code == 200
            assert response.json()["result"]["greeting"] == "Hello World!"

        def test_resolve_object_nested(self, client):
            """Resolves nested object via API."""
            response = client.post(
                "/resolve-object",
                json={
                    "level1": {
                        "message": "Count is {{count}}"
                    }
                }
            )
            assert response.status_code == 200
            assert response.json()["result"]["level1"]["message"] == "Count is 42"

    class TestDependencyConfiguration:
        """Tests for dependency configuration."""

        def test_resolver_with_custom_options(self):
            """Resolver respects custom options."""
            app = FastAPI()
            opts = ResolverOptions(missing_strategy=MissingStrategy.KEEP)
            get_resolver = create_resolver_dependency(options=opts)

            @app.get("/test")
            def test_endpoint(resolver: ConfiguredResolverProtocol = Depends(get_resolver)):
                return {"result": resolver.resolve("{{missing}}", {})}

            client = TestClient(app)
            response = client.get("/test")
            assert response.status_code == 200
            assert response.json()["result"] == "{{missing}}"

        def test_resolver_isolation_between_requests(self, client):
            """Each request gets fresh resolver."""
            response1 = client.get("/resolve", params={"template": "{{name}}"})
            response2 = client.get("/resolve", params={"template": "{{name}}"})
            assert response1.json()["result"] == response2.json()["result"] == "World"


class TestFastAPIMiddlewarePatterns:
    """Tests for common middleware patterns."""

    def test_request_context_injection(self):
        """Test injecting request context into resolver."""
        app = FastAPI()
        get_resolver = create_resolver_dependency()

        @app.get("/with-headers")
        def with_headers_endpoint(
            resolver: ConfiguredResolverProtocol = Depends(get_resolver),
        ):
            context = {"header_value": "test-header"}
            return {"result": resolver.resolve("Header: {{header_value}}", context)}

        client = TestClient(app)
        response = client.get("/with-headers", headers={"X-Custom": "test"})
        assert response.status_code == 200
        assert response.json()["result"] == "Header: test-header"


class TestFastAPIErrorHandling:
    """Tests for error handling in FastAPI context."""

    def test_invalid_template_returns_original(self):
        """Invalid template returns original placeholder."""
        app = FastAPI()
        get_resolver = create_resolver_dependency()

        @app.get("/test")
        def test_endpoint(resolver: ConfiguredResolverProtocol = Depends(get_resolver)):
            return {"result": resolver.resolve("{{_private}}", {})}

        client = TestClient(app)
        response = client.get("/test")
        assert response.status_code == 200
        assert response.json()["result"] == "{{_private}}"
