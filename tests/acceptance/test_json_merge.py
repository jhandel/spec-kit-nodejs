"""
Acceptance Tests: JSON Merge Behavior
======================================

BEHAVIOR: merge_json_files() performs deep merge of JSON objects.
- New keys are added
- Existing keys are preserved unless overwritten
- Nested dictionaries are merged recursively  
- Lists and other values are replaced (not merged)
"""

import json
import tempfile
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
from specify_cli import merge_json_files


class TestMergeJsonBasic:
    """BEHAVIOR: Basic JSON merge operations."""

    def test_returns_dict(self):
        """MUST return a dictionary."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({}, f)
            f.flush()
            result = merge_json_files(Path(f.name), {})
        assert isinstance(result, dict)

    def test_adds_new_keys(self):
        """New keys from update are added."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"existing": "value"}, f)
            f.flush()
            result = merge_json_files(Path(f.name), {"new": "value"})
        assert result["existing"] == "value"
        assert result["new"] == "value"

    def test_preserves_existing_keys(self):
        """Existing keys are preserved if not in update."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"keep": "me"}, f)
            f.flush()
            result = merge_json_files(Path(f.name), {"other": "value"})
        assert result["keep"] == "me"

    def test_overwrites_existing_keys(self):
        """Existing keys are overwritten if in update."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"key": "old"}, f)
            f.flush()
            result = merge_json_files(Path(f.name), {"key": "new"})
        assert result["key"] == "new"


class TestMergeJsonDeepMerge:
    """BEHAVIOR: Nested objects are merged recursively."""

    def test_nested_objects_merged(self):
        """Nested objects are merged, not replaced."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({
                "outer": {
                    "existing": "value"
                }
            }, f)
            f.flush()
            result = merge_json_files(Path(f.name), {
                "outer": {
                    "new": "value"
                }
            })
        assert result["outer"]["existing"] == "value"
        assert result["outer"]["new"] == "value"

    def test_deeply_nested_merge(self):
        """Deeply nested structures are merged."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({
                "a": {"b": {"c": {"existing": "value"}}}
            }, f)
            f.flush()
            result = merge_json_files(Path(f.name), {
                "a": {"b": {"c": {"new": "value"}}}
            })
        assert result["a"]["b"]["c"]["existing"] == "value"
        assert result["a"]["b"]["c"]["new"] == "value"


class TestMergeJsonArrays:
    """BEHAVIOR: Arrays are replaced, not merged."""

    def test_arrays_replaced_not_merged(self):
        """Array values are replaced entirely."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"items": [1, 2, 3]}, f)
            f.flush()
            result = merge_json_files(Path(f.name), {"items": [4, 5]})
        assert result["items"] == [4, 5]  # Replaced, not [1, 2, 3, 4, 5]


class TestMergeJsonValueTypes:
    """BEHAVIOR: Various value types are handled correctly."""

    def test_null_values_merged(self):
        """Null values can be merged."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"key": None}, f)
            f.flush()
            result = merge_json_files(Path(f.name), {"key": "value"})
        assert result["key"] == "value"

    def test_boolean_values_merged(self):
        """Boolean values can be merged."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"enabled": True}, f)
            f.flush()
            result = merge_json_files(Path(f.name), {"enabled": False})
        assert result["enabled"] is False

    def test_numeric_values_merged(self):
        """Numeric values can be merged."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"count": 42}, f)
            f.flush()
            result = merge_json_files(Path(f.name), {"count": 100})
        assert result["count"] == 100


class TestMergeJsonEdgeCases:
    """BEHAVIOR: Edge cases in JSON merge."""

    def test_empty_existing_file(self):
        """Empty existing file works."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({}, f)
            f.flush()
            result = merge_json_files(Path(f.name), {"new": "value"})
        assert result == {"new": "value"}

    def test_empty_update(self):
        """Empty update preserves existing."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"existing": "value"}, f)
            f.flush()
            result = merge_json_files(Path(f.name), {})
        assert result == {"existing": "value"}

    def test_nonexistent_file_returns_update(self):
        """Nonexistent file returns just the update content."""
        result = merge_json_files(Path("/nonexistent/path.json"), {"new": "value"})
        assert result == {"new": "value"}

    def test_invalid_json_returns_update(self):
        """Invalid JSON file returns just the update content."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("not valid json {{{")
            f.flush()
            result = merge_json_files(Path(f.name), {"new": "value"})
        assert result == {"new": "value"}


class TestVSCodeSettingsMerge:
    """BEHAVIOR: VS Code settings.json specific merge scenarios."""

    def test_chat_prompt_files_merged(self):
        """chat.promptFilesRecommendations are merged."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({
                "chat.promptFilesRecommendations": {
                    "existing": True
                }
            }, f)
            f.flush()
            result = merge_json_files(Path(f.name), {
                "chat.promptFilesRecommendations": {
                    "speckit.constitution": True
                }
            })
        assert result["chat.promptFilesRecommendations"]["existing"] is True
        assert result["chat.promptFilesRecommendations"]["speckit.constitution"] is True

    def test_chat_tools_terminal_merged(self):
        """chat.tools.terminal.autoApprove is merged."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({
                "chat.tools.terminal.autoApprove": {
                    "existing/path/": True
                }
            }, f)
            f.flush()
            result = merge_json_files(Path(f.name), {
                "chat.tools.terminal.autoApprove": {
                    ".specify/scripts/bash/": True
                }
            })
        assert result["chat.tools.terminal.autoApprove"]["existing/path/"] is True
        assert result["chat.tools.terminal.autoApprove"][".specify/scripts/bash/"] is True
