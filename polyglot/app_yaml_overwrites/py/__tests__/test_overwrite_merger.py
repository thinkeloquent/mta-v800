"""
Unit tests for overwrite_merger module.

Tests cover:
- Statement coverage for all code paths
- Branch coverage for all conditionals
- Boundary value analysis
- Error handling verification
"""
import pytest

from app_yaml_overwrites.overwrite_merger import apply_overwrites


class TestApplyOverwrites:
    """Tests for apply_overwrites function."""

    # =========================================================================
    # Statement Coverage
    # =========================================================================

    class TestStatementCoverage:
        """Ensure every statement executes at least once."""

        def test_returns_original_when_no_overwrites(self):
            """Should return original config when overwrite_section is empty."""
            original = {"key": "value"}

            result = apply_overwrites(original, {})

            assert result == original

        def test_returns_original_when_overwrites_none(self):
            """Should return original config when overwrite_section is None."""
            original = {"key": "value"}

            result = apply_overwrites(original, None)

            assert result == original

        def test_merges_flat_overwrites(self):
            """Should merge flat key-value overwrites."""
            original = {"key1": "original", "key2": "keep"}
            overwrites = {"key1": "overwritten"}

            result = apply_overwrites(original, overwrites)

            assert result["key1"] == "overwritten"
            assert result["key2"] == "keep"

        def test_adds_new_keys(self):
            """Should add new keys from overwrites."""
            original = {"existing": "value"}
            overwrites = {"new_key": "new_value"}

            result = apply_overwrites(original, overwrites)

            assert result["existing"] == "value"
            assert result["new_key"] == "new_value"

    # =========================================================================
    # Branch Coverage
    # =========================================================================

    class TestBranchCoverage:
        """Test all if/else/switch branches."""

        def test_branch_when_overwrite_section_empty(self):
            """Empty overwrite should trigger early return."""
            original = {"key": "value"}

            result = apply_overwrites(original, {})

            assert result == original

        def test_branch_when_overwrite_section_falsy(self):
            """Falsy overwrite should trigger early return."""
            original = {"key": "value"}

            # Test with None
            assert apply_overwrites(original, None) == original

            # Test with empty dict
            assert apply_overwrites(original, {}) == original

        def test_branch_deep_merge_both_dicts(self):
            """When both values are dicts, should deep merge."""
            original = {
                "headers": {
                    "X-Static": "value",
                    "X-Dynamic": None
                }
            }
            overwrites = {
                "headers": {
                    "X-Dynamic": "resolved"
                }
            }

            result = apply_overwrites(original, overwrites)

            assert result["headers"]["X-Static"] == "value"
            assert result["headers"]["X-Dynamic"] == "resolved"

        def test_branch_overwrite_non_dict_with_dict(self):
            """When original is not dict but overwrite is dict, should replace."""
            original = {"key": "string_value"}
            overwrites = {"key": {"nested": "value"}}

            result = apply_overwrites(original, overwrites)

            assert result["key"] == {"nested": "value"}

        def test_branch_overwrite_dict_with_non_dict(self):
            """When original is dict but overwrite is not dict, should replace."""
            original = {"key": {"nested": "value"}}
            overwrites = {"key": "string_value"}

            result = apply_overwrites(original, overwrites)

            assert result["key"] == "string_value"

    # =========================================================================
    # Boundary Value Analysis
    # =========================================================================

    class TestBoundaryValues:
        """Test edge cases: empty, min, max, boundary values."""

        def test_empty_original(self):
            """Should handle empty original config."""
            original = {}
            overwrites = {"key": "value"}

            result = apply_overwrites(original, overwrites)

            assert result == {"key": "value"}

        def test_both_empty(self):
            """Should handle both empty."""
            result = apply_overwrites({}, {})

            assert result == {}

        def test_deeply_nested_merge(self):
            """Should handle deeply nested structures."""
            original = {
                "level1": {
                    "level2": {
                        "level3": {
                            "original": "keep"
                        }
                    }
                }
            }
            overwrites = {
                "level1": {
                    "level2": {
                        "level3": {
                            "new": "added"
                        }
                    }
                }
            }

            result = apply_overwrites(original, overwrites)

            assert result["level1"]["level2"]["level3"]["original"] == "keep"
            assert result["level1"]["level2"]["level3"]["new"] == "added"

        def test_null_values_in_overwrites(self):
            """Should handle null values in overwrites."""
            original = {"key": "value"}
            overwrites = {"key": None}

            result = apply_overwrites(original, overwrites)

            assert result["key"] is None

        def test_list_values(self):
            """Should replace lists (not merge them)."""
            original = {"items": [1, 2, 3]}
            overwrites = {"items": [4, 5]}

            result = apply_overwrites(original, overwrites)

            assert result["items"] == [4, 5]

    # =========================================================================
    # Error Handling
    # =========================================================================

    class TestErrorHandling:
        """Test error conditions and exception paths."""

        def test_does_not_mutate_original(self):
            """apply_overwrites should not mutate the original dict."""
            original = {"key": "original"}
            overwrites = {"key": "changed"}

            result = apply_overwrites(original, overwrites)

            assert original["key"] == "original"
            assert result["key"] == "changed"

        def test_handles_mixed_types(self):
            """Should handle various types in config."""
            original = {
                "string": "text",
                "number": 42,
                "float": 3.14,
                "bool": True,
                "null": None,
                "list": [1, 2, 3],
                "dict": {"nested": "value"}
            }
            overwrites = {
                "string": "new_text",
                "number": 100
            }

            result = apply_overwrites(original, overwrites)

            assert result["string"] == "new_text"
            assert result["number"] == 100
            assert result["float"] == 3.14
            assert result["bool"] is True
            assert result["null"] is None
            assert result["list"] == [1, 2, 3]
            assert result["dict"] == {"nested": "value"}

    # =========================================================================
    # Integration Tests
    # =========================================================================

    class TestIntegration:
        """End-to-end scenarios with realistic data."""

        def test_realistic_provider_config_merge(self):
            """Test merging realistic provider configuration."""
            original = {
                "providers": {
                    "api_provider": {
                        "base_url": "https://api.example.com",
                        "headers": {
                            "X-App-Name": None,
                            "X-App-Version": None,
                            "X-Custom": "static"
                        },
                        "timeout": 30
                    }
                }
            }
            overwrites = {
                "providers": {
                    "api_provider": {
                        "headers": {
                            "X-App-Name": "MyApp",
                            "X-App-Version": "1.0.0"
                        }
                    }
                }
            }

            result = apply_overwrites(original, overwrites)

            provider = result["providers"]["api_provider"]
            assert provider["base_url"] == "https://api.example.com"
            assert provider["headers"]["X-App-Name"] == "MyApp"
            assert provider["headers"]["X-App-Version"] == "1.0.0"
            assert provider["headers"]["X-Custom"] == "static"
            assert provider["timeout"] == 30

        def test_overwrite_from_context_pattern(self):
            """Test the overwrite_from_context pattern used in real configs."""
            config = {
                "headers": {
                    "Authorization": None,
                    "Content-Type": "application/json"
                },
                "overwrite_from_context": {
                    "headers": {
                        "Authorization": "Bearer resolved-token"
                    }
                }
            }

            # Simulate resolution: merge overwrite_from_context into parent
            resolved = apply_overwrites(
                config,
                config.get("overwrite_from_context", {})
            )

            assert resolved["headers"]["Authorization"] == "Bearer resolved-token"
            assert resolved["headers"]["Content-Type"] == "application/json"
