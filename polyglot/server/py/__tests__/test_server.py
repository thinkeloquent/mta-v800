"""
Unit tests for server module.

Tests cover:
- Statement coverage for all code paths
- Branch coverage for all conditionals
- Boundary value analysis
- Error handling verification
"""
import asyncio
import tempfile
import os
import pytest
from unittest.mock import MagicMock, patch, AsyncMock

from fastapi import FastAPI

from server import init, start, stop


class TestInit:
    """Tests for init() function."""

    # =========================================================================
    # Statement Coverage
    # =========================================================================

    class TestStatementCoverage:
        """Ensure every statement executes at least once."""

        def test_init_returns_fastapi_instance(self, sample_config):
            """init() should return a FastAPI instance."""
            app = init(sample_config)
            assert isinstance(app, FastAPI)

        def test_init_sets_title(self, sample_config):
            """init() should set the app title from config."""
            app = init(sample_config)
            assert app.title == "Test API"

    # =========================================================================
    # Branch Coverage
    # =========================================================================

    class TestBranchCoverage:
        """Test all if/else paths."""

        def test_init_with_default_title(self):
            """init() should use default title when not provided."""
            app = init({})
            assert app.title == "API Server"

        def test_init_with_custom_title(self):
            """init() should use custom title when provided."""
            app = init({"title": "Custom API"})
            assert app.title == "Custom API"


class TestStart:
    """Tests for start() function."""

    # =========================================================================
    # Statement Coverage
    # =========================================================================

    class TestStatementCoverage:
        """Ensure every statement executes at least once."""

        @pytest.mark.asyncio
        async def test_start_stores_hooks_in_state(self, sample_config):
            """start() should store hooks in app state."""
            app = init(sample_config)

            # Mock uvicorn to prevent actual server start
            with patch("server.uvicorn") as mock_uvicorn:
                mock_server = MagicMock()
                mock_server.serve = AsyncMock()
                mock_uvicorn.Server.return_value = mock_server

                await start(app, sample_config)

            assert hasattr(app.state, "startup_hooks")
            assert hasattr(app.state, "shutdown_hooks")
            assert hasattr(app.state, "config")

        @pytest.mark.asyncio
        async def test_start_stores_initial_state(self, sample_config):
            """start() should store initial_state when provided."""
            app = init(sample_config)

            with patch("server.uvicorn") as mock_uvicorn:
                mock_server = MagicMock()
                mock_server.serve = AsyncMock()
                mock_uvicorn.Server.return_value = mock_server

                await start(app, sample_config)

            assert hasattr(app.state, "initial_state")
            assert app.state.initial_state["user"] == "test"

    # =========================================================================
    # Branch Coverage
    # =========================================================================

    class TestBranchCoverage:
        """Test all if/else paths."""

        @pytest.mark.asyncio
        async def test_start_without_bootstrap(self):
            """start() should work without bootstrap config."""
            app = init({"title": "Test"})

            with patch("server.uvicorn") as mock_uvicorn:
                mock_server = MagicMock()
                mock_server.serve = AsyncMock()
                mock_uvicorn.Server.return_value = mock_server

                # Should not raise
                await start(app, {"title": "Test"})

            assert app.state.startup_hooks == []
            assert app.state.shutdown_hooks == []

        @pytest.mark.asyncio
        async def test_start_without_initial_state(self):
            """start() should work without initial_state."""
            config = {"title": "Test"}
            app = init(config)

            with patch("server.uvicorn") as mock_uvicorn:
                mock_server = MagicMock()
                mock_server.serve = AsyncMock()
                mock_uvicorn.Server.return_value = mock_server

                await start(app, config)

            assert not hasattr(app.state, "initial_state")

        @pytest.mark.asyncio
        async def test_start_with_env_dir_not_exists(self):
            """start() should handle non-existent env directory."""
            config = {
                "title": "Test",
                "bootstrap": {"load_env": "/nonexistent/path"},
            }
            app = init(config)

            with patch("server.uvicorn") as mock_uvicorn:
                mock_server = MagicMock()
                mock_server.serve = AsyncMock()
                mock_uvicorn.Server.return_value = mock_server

                # Should not raise, just warn
                await start(app, config)

        @pytest.mark.asyncio
        async def test_start_with_lifecycle_dir_not_exists(self):
            """start() should handle non-existent lifecycle directory."""
            config = {
                "title": "Test",
                "bootstrap": {"lifecycle": "/nonexistent/path"},
            }
            app = init(config)

            with patch("server.uvicorn") as mock_uvicorn:
                mock_server = MagicMock()
                mock_server.serve = AsyncMock()
                mock_uvicorn.Server.return_value = mock_server

                # Should not raise, just warn
                await start(app, config)

        @pytest.mark.asyncio
        async def test_start_with_existing_env_dir(self):
            """start() should load modules from env directory."""
            with tempfile.TemporaryDirectory() as tmpdir:
                # Create a dummy env module
                env_file = os.path.join(tmpdir, "test_env.py")
                with open(env_file, "w") as f:
                    f.write("# Test env module\nprint('env loaded')")

                config = {
                    "title": "Test",
                    "bootstrap": {"load_env": tmpdir},
                }
                app = init(config)

                with patch("server.uvicorn") as mock_uvicorn:
                    mock_server = MagicMock()
                    mock_server.serve = AsyncMock()
                    mock_uvicorn.Server.return_value = mock_server

                    await start(app, config)

        @pytest.mark.asyncio
        async def test_start_with_lifecycle_hooks(self):
            """start() should load lifecycle hooks from modules."""
            with tempfile.TemporaryDirectory() as tmpdir:
                # Create lifecycle module with hooks
                lifecycle_file = os.path.join(tmpdir, "test_lifecycle.py")
                with open(lifecycle_file, "w") as f:
                    f.write("""
def onStartup(app, config):
    pass

async def onShutdown(app, config):
    pass
""")

                config = {
                    "title": "Test",
                    "bootstrap": {"lifecycle": tmpdir},
                }
                app = init(config)

                with patch("server.uvicorn") as mock_uvicorn:
                    mock_server = MagicMock()
                    mock_server.serve = AsyncMock()
                    mock_uvicorn.Server.return_value = mock_server

                    await start(app, config)

                assert len(app.state.startup_hooks) == 1
                assert len(app.state.shutdown_hooks) == 1

    # =========================================================================
    # Port Configuration
    # =========================================================================

    class TestPortConfiguration:
        """Test port configuration options."""

        @pytest.mark.asyncio
        async def test_uses_config_port(self):
            """start() should use port from config."""
            config = {"title": "Test", "port": 9000}
            app = init(config)

            with patch("server.uvicorn") as mock_uvicorn:
                mock_server = MagicMock()
                mock_server.serve = AsyncMock()
                mock_uvicorn.Server.return_value = mock_server

                await start(app, config)

                # Check the config passed to uvicorn
                call_args = mock_uvicorn.Config.call_args
                assert call_args.kwargs["port"] == 9000

        @pytest.mark.asyncio
        async def test_uses_env_port(self, clean_env):
            """start() should prefer PORT env var over config."""
            clean_env(PORT="7000")
            config = {"title": "Test", "port": 9000}
            app = init(config)

            with patch("server.uvicorn") as mock_uvicorn:
                mock_server = MagicMock()
                mock_server.serve = AsyncMock()
                mock_uvicorn.Server.return_value = mock_server

                await start(app, config)

                call_args = mock_uvicorn.Config.call_args
                assert call_args.kwargs["port"] == 7000

        @pytest.mark.asyncio
        async def test_uses_default_port(self):
            """start() should use default port when not specified."""
            config = {"title": "Test"}
            app = init(config)

            with patch("server.uvicorn") as mock_uvicorn:
                mock_server = MagicMock()
                mock_server.serve = AsyncMock()
                mock_uvicorn.Server.return_value = mock_server
                with patch.dict(os.environ, {}, clear=True):
                    await start(app, config)

                call_args = mock_uvicorn.Config.call_args
                assert call_args.kwargs["port"] == 8080


class TestStop:
    """Tests for stop() function."""

    # =========================================================================
    # Statement Coverage
    # =========================================================================

    class TestStatementCoverage:
        """Ensure every statement executes at least once."""

        @pytest.mark.asyncio
        async def test_stop_does_not_raise(self, sample_config):
            """stop() should complete without raising."""
            app = init(sample_config)

            # stop is a placeholder, should not raise
            await stop(app, sample_config)

        @pytest.mark.asyncio
        async def test_stop_with_empty_config(self):
            """stop() should handle empty config."""
            app = init({})
            await stop(app, {})


class TestLifespan:
    """Tests for lifespan context manager."""

    # =========================================================================
    # Statement Coverage
    # =========================================================================

    class TestStatementCoverage:
        """Ensure every statement executes at least once."""

        @pytest.mark.asyncio
        async def test_lifespan_executes_startup_hooks(self, sample_config):
            """Lifespan should execute startup hooks."""
            startup_called = []

            def startup_hook(app, config):
                startup_called.append(True)

            app = init(sample_config)
            app.state.startup_hooks = [startup_hook]
            app.state.shutdown_hooks = []
            app.state.config = sample_config

            # Trigger lifespan manually using TestClient
            from fastapi.testclient import TestClient
            with TestClient(app):
                pass  # Entering context triggers startup

            assert len(startup_called) == 1

        @pytest.mark.asyncio
        async def test_lifespan_executes_async_hooks(self, sample_config):
            """Lifespan should execute async hooks."""
            startup_called = []

            async def async_startup_hook(app, config):
                startup_called.append(True)

            app = init(sample_config)
            app.state.startup_hooks = [async_startup_hook]
            app.state.shutdown_hooks = []
            app.state.config = sample_config

            from fastapi.testclient import TestClient
            with TestClient(app):
                pass

            assert len(startup_called) == 1
