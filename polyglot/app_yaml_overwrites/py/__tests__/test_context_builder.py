"""
Unit tests for context_builder module.

Tests cover:
- Statement coverage for all code paths
- Branch coverage for all conditionals
- Boundary value analysis
- Error handling verification
- Log verification (hyper-observability)
"""
import os
import pytest
from unittest.mock import MagicMock, AsyncMock

from app_yaml_overwrites.context_builder import ContextBuilder, ContextExtender


class TestContextBuilder:
    """Tests for ContextBuilder class."""

    # =========================================================================
    # Statement Coverage
    # =========================================================================

    class TestStatementCoverage:
        """Ensure every statement executes at least once."""

        @pytest.mark.asyncio
        async def test_build_returns_context_dict(self):
            """build() should return a dictionary."""
            options = {"config": {"key": "value"}}

            result = await ContextBuilder.build(options)

            assert isinstance(result, dict)

        @pytest.mark.asyncio
        async def test_build_includes_env(self):
            """build() should include env from environment."""
            options = {}

            result = await ContextBuilder.build(options)

            assert "env" in result
            assert isinstance(result["env"], dict)

        @pytest.mark.asyncio
        async def test_build_includes_config(self):
            """build() should include config from options."""
            options = {"config": {"app": {"name": "Test"}}}

            result = await ContextBuilder.build(options)

            assert result["config"] == {"app": {"name": "Test"}}

        @pytest.mark.asyncio
        async def test_build_includes_app(self):
            """build() should include app from options."""
            options = {"app": {"name": "MyApp", "version": "1.0"}}

            result = await ContextBuilder.build(options)

            assert result["app"] == {"name": "MyApp", "version": "1.0"}

        @pytest.mark.asyncio
        async def test_build_includes_state(self):
            """build() should include state from options."""
            options = {"state": {"user_id": 123}}

            result = await ContextBuilder.build(options)

            assert result["state"] == {"user_id": 123}

        @pytest.mark.asyncio
        async def test_build_includes_request(self):
            """build() should include request from options."""
            mock_request = MagicMock()
            options = {"request": mock_request}

            result = await ContextBuilder.build(options)

            assert result["request"] is mock_request

    # =========================================================================
    # Branch Coverage
    # =========================================================================

    class TestBranchCoverage:
        """Test all if/else/switch branches."""

        @pytest.mark.asyncio
        async def test_build_with_no_extenders(self):
            """build() should work without extenders."""
            options = {"config": {"key": "value"}}

            result = await ContextBuilder.build(options, extenders=None)

            assert result["config"] == {"key": "value"}

        @pytest.mark.asyncio
        async def test_build_with_empty_extenders_list(self):
            """build() should work with empty extenders list."""
            options = {"config": {"key": "value"}}

            result = await ContextBuilder.build(options, extenders=[])

            assert result["config"] == {"key": "value"}

        @pytest.mark.asyncio
        async def test_build_with_single_extender(self):
            """build() should apply single extender."""
            async def extender(ctx, req):
                return {"custom": "value"}

            options = {"config": {"key": "original"}}

            result = await ContextBuilder.build(options, extenders=[extender])

            assert result["custom"] == "value"
            assert result["config"] == {"key": "original"}

        @pytest.mark.asyncio
        async def test_build_with_multiple_extenders(self):
            """build() should apply multiple extenders in order."""
            async def extender1(ctx, req):
                return {"from_ext1": "value1"}

            async def extender2(ctx, req):
                return {"from_ext2": "value2"}

            options = {}

            result = await ContextBuilder.build(options, extenders=[extender1, extender2])

            assert result["from_ext1"] == "value1"
            assert result["from_ext2"] == "value2"

        @pytest.mark.asyncio
        async def test_extender_can_access_previous_context(self):
            """Later extenders should see changes from earlier ones."""
            async def extender1(ctx, req):
                return {"step1": True}

            async def extender2(ctx, req):
                # Should see step1 in context
                if ctx.get("step1"):
                    return {"step2": "saw_step1"}
                return {"step2": "no_step1"}

            options = {}

            result = await ContextBuilder.build(options, extenders=[extender1, extender2])

            assert result["step2"] == "saw_step1"

        @pytest.mark.asyncio
        async def test_build_with_custom_env(self):
            """build() should use custom env if provided."""
            custom_env = {"MY_VAR": "my_value"}
            options = {"env": custom_env}

            result = await ContextBuilder.build(options)

            assert result["env"] == custom_env

        @pytest.mark.asyncio
        async def test_build_defaults_env_to_os_environ(self, monkeypatch):
            """build() should default env to os.environ."""
            monkeypatch.setenv("TEST_VAR", "test_value")
            options = {}

            result = await ContextBuilder.build(options)

            assert "TEST_VAR" in result["env"]
            assert result["env"]["TEST_VAR"] == "test_value"

    # =========================================================================
    # Boundary Value Analysis
    # =========================================================================

    class TestBoundaryValues:
        """Test edge cases: empty, min, max, boundary values."""

        @pytest.mark.asyncio
        async def test_empty_options(self):
            """build() should handle empty options."""
            result = await ContextBuilder.build({})

            assert "env" in result
            assert "config" in result
            assert "app" in result
            assert "state" in result
            assert "request" in result

        @pytest.mark.asyncio
        async def test_empty_config(self):
            """build() should handle empty config."""
            result = await ContextBuilder.build({"config": {}})

            assert result["config"] == {}

        @pytest.mark.asyncio
        async def test_none_request(self):
            """build() should handle None request."""
            result = await ContextBuilder.build({"request": None})

            assert result["request"] is None

        @pytest.mark.asyncio
        async def test_deeply_nested_config(self):
            """build() should handle deeply nested config."""
            deep_config = {"level1": {"level2": {"level3": {"level4": "value"}}}}

            result = await ContextBuilder.build({"config": deep_config})

            assert result["config"]["level1"]["level2"]["level3"]["level4"] == "value"

    # =========================================================================
    # Error Handling
    # =========================================================================

    class TestErrorHandling:
        """Test error conditions and exception paths."""

        @pytest.mark.asyncio
        async def test_extender_exception_propagates(self):
            """Exceptions in extenders should propagate."""
            async def bad_extender(ctx, req):
                raise ValueError("Extender error")

            options = {}

            with pytest.raises(ValueError, match="Extender error"):
                await ContextBuilder.build(options, extenders=[bad_extender])

        @pytest.mark.asyncio
        async def test_extender_returning_none(self):
            """Extender returning None should be handled."""
            async def none_extender(ctx, req):
                return None

            options = {"config": {"key": "value"}}

            # This will cause TypeError when trying to .update(None)
            with pytest.raises(TypeError):
                await ContextBuilder.build(options, extenders=[none_extender])

    # =========================================================================
    # Integration Tests
    # =========================================================================

    class TestIntegration:
        """End-to-end scenarios with realistic data."""

        @pytest.mark.asyncio
        async def test_full_context_build_with_request(self):
            """Build full context with all options and request."""
            mock_request = MagicMock()
            mock_request.headers = {"x-request-id": "abc-123"}

            async def auth_extender(ctx, req):
                return {"auth": {"token": "bearer xyz"}}

            options = {
                "env": {"API_KEY": "secret"},
                "config": {"providers": {"test": {}}},
                "app": {"name": "TestApp", "version": "2.0"},
                "state": {"session_id": "sess-456"},
                "request": mock_request
            }

            result = await ContextBuilder.build(options, extenders=[auth_extender])

            assert result["env"]["API_KEY"] == "secret"
            assert result["config"]["providers"]["test"] == {}
            assert result["app"]["name"] == "TestApp"
            assert result["state"]["session_id"] == "sess-456"
            assert result["request"] is mock_request
            assert result["auth"]["token"] == "bearer xyz"
