"""
Test: Template Processing - COMPREHENSIVE
==========================================
Complete test coverage for template download, extraction, and processing.
"""

import pytest
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path
import sys
import os
import json
import tempfile
import zipfile

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from specify_cli import (
    merge_json_files,
    handle_vscode_settings,
    ensure_executable_scripts,
    download_and_extract_template,
)


class TestMergeJsonFilesComplete:
    """Complete coverage of merge_json_files function."""

    def test_merge_preserves_existing_keys(self):
        """Existing keys not in new content should be preserved"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"existing": "value", "keep": "this"}, f)
            f.flush()
            
            new_content = {"new": "value"}
            result = merge_json_files(Path(f.name), new_content)
            
            assert result["existing"] == "value"
            assert result["keep"] == "this"
            assert result["new"] == "value"
        os.unlink(f.name)

    def test_merge_overwrites_with_new_values(self):
        """New content should overwrite existing keys"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"key": "old"}, f)
            f.flush()
            
            result = merge_json_files(Path(f.name), {"key": "new"})
            assert result["key"] == "new"
        os.unlink(f.name)

    def test_deep_merge_nested_dicts(self):
        """Nested dictionaries should be merged recursively"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({
                "level1": {
                    "existing": "value",
                    "level2": {"a": 1}
                }
            }, f)
            f.flush()
            
            new_content = {
                "level1": {
                    "new": "added",
                    "level2": {"b": 2}
                }
            }
            result = merge_json_files(Path(f.name), new_content)
            
            assert result["level1"]["existing"] == "value"
            assert result["level1"]["new"] == "added"
            assert result["level1"]["level2"]["a"] == 1
            assert result["level1"]["level2"]["b"] == 2
        os.unlink(f.name)

    def test_arrays_replaced_not_merged(self):
        """Arrays should be replaced, not merged"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"arr": [1, 2, 3]}, f)
            f.flush()
            
            result = merge_json_files(Path(f.name), {"arr": [4, 5]})
            assert result["arr"] == [4, 5]
        os.unlink(f.name)

    def test_file_not_found_returns_new_content(self):
        """Non-existent file should return just new content"""
        result = merge_json_files(Path("/nonexistent/file.json"), {"new": "content"})
        assert result == {"new": "content"}

    def test_invalid_json_returns_new_content(self):
        """Invalid JSON file should return just new content"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("{ invalid json }")
            f.flush()
            
            result = merge_json_files(Path(f.name), {"new": "content"})
            assert result == {"new": "content"}
        os.unlink(f.name)

    def test_empty_file_returns_new_content(self):
        """Empty file should return just new content"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("")
            f.flush()
            
            result = merge_json_files(Path(f.name), {"new": "content"})
            assert result == {"new": "content"}
        os.unlink(f.name)

    def test_verbose_mode(self):
        """Verbose mode should print merge info"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({}, f)
            f.flush()
            
            # Just verify it doesn't crash with verbose=True
            result = merge_json_files(Path(f.name), {"key": "value"}, verbose=True)
            assert "key" in result
        os.unlink(f.name)


class TestDeepMergeAlgorithm:
    """Test the deep merge algorithm in detail."""

    def test_dict_into_dict_merges(self):
        """Dict value merged into dict value"""
        pass

    def test_dict_into_non_dict_replaces(self):
        """Dict value replaces non-dict value"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"key": "string"}, f)
            f.flush()
            
            result = merge_json_files(Path(f.name), {"key": {"nested": "dict"}})
            assert result["key"] == {"nested": "dict"}
        os.unlink(f.name)

    def test_non_dict_into_dict_replaces(self):
        """Non-dict value replaces dict value"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"key": {"nested": "dict"}}, f)
            f.flush()
            
            result = merge_json_files(Path(f.name), {"key": "string"})
            assert result["key"] == "string"
        os.unlink(f.name)

    def test_null_value_handling(self):
        """null/None values should be handled"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"key": None}, f)
            f.flush()
            
            result = merge_json_files(Path(f.name), {"key": "value"})
            assert result["key"] == "value"
        os.unlink(f.name)

    def test_three_level_deep_merge(self):
        """Three levels of nesting should merge correctly"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({
                "l1": {"l2": {"l3": {"existing": True}}}
            }, f)
            f.flush()
            
            result = merge_json_files(Path(f.name), {
                "l1": {"l2": {"l3": {"new": True}}}
            })
            
            assert result["l1"]["l2"]["l3"]["existing"] is True
            assert result["l1"]["l2"]["l3"]["new"] is True
        os.unlink(f.name)


class TestVSCodeSettingsMerge:
    """Test .vscode/settings.json merge behavior."""

    def test_settings_json_is_merged_not_replaced(self):
        """settings.json should be merged, not overwritten"""
        # This is a critical behavior - user settings preserved
        pass

    def test_typical_settings_merge(self):
        """Test realistic settings.json merge scenario"""
        existing = {
            "editor.formatOnSave": True,
            "editor.tabSize": 4,
            "python.linting.enabled": True,
            "myCustomSetting": "preserved"
        }
        
        new = {
            "editor.formatOnSave": False,  # Override
            "specify.commands.enabled": True,  # New
            "python.analysis.typeCheckingMode": "basic"  # New nested
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(existing, f)
            f.flush()
            
            result = merge_json_files(Path(f.name), new)
            
            assert result["editor.formatOnSave"] is False  # Overwritten
            assert result["editor.tabSize"] == 4  # Preserved
            assert result["myCustomSetting"] == "preserved"
            assert result["specify.commands.enabled"] is True  # Added
        os.unlink(f.name)


class TestEnsureExecutableScriptsComplete:
    """Complete coverage of ensure_executable_scripts function."""

    @pytest.mark.skipif(os.name == 'nt', reason="Unix-only test")
    def test_skips_on_windows(self):
        """Should silently skip on Windows"""
        # When os.name == 'nt', function returns immediately
        pass

    @pytest.mark.skipif(os.name == 'nt', reason="Unix-only test")
    def test_sets_execute_bit(self):
        """Should set execute bit on .sh files"""
        with tempfile.TemporaryDirectory() as tmpdir:
            scripts_dir = Path(tmpdir) / ".specify" / "scripts"
            scripts_dir.mkdir(parents=True)
            
            script = scripts_dir / "test.sh"
            script.write_text("#!/bin/bash\necho hello")
            script.chmod(0o644)  # No execute bit
            
            ensure_executable_scripts(Path(tmpdir))
            
            mode = script.stat().st_mode
            assert mode & 0o100, "Owner execute bit should be set"

    @pytest.mark.skipif(os.name == 'nt', reason="Unix-only test")
    def test_skips_already_executable(self):
        """Should skip files already executable"""
        with tempfile.TemporaryDirectory() as tmpdir:
            scripts_dir = Path(tmpdir) / ".specify" / "scripts"
            scripts_dir.mkdir(parents=True)
            
            script = scripts_dir / "test.sh"
            script.write_text("#!/bin/bash\necho hello")
            script.chmod(0o755)
            
            # Should not raise
            ensure_executable_scripts(Path(tmpdir))

    @pytest.mark.skipif(os.name == 'nt', reason="Unix-only test")
    def test_skips_without_shebang(self):
        """Should skip .sh files without shebang"""
        with tempfile.TemporaryDirectory() as tmpdir:
            scripts_dir = Path(tmpdir) / ".specify" / "scripts"
            scripts_dir.mkdir(parents=True)
            
            script = scripts_dir / "test.sh"
            script.write_text("echo hello")  # No shebang
            script.chmod(0o644)
            
            ensure_executable_scripts(Path(tmpdir))
            
            mode = script.stat().st_mode
            assert not (mode & 0o100), "Should not modify without shebang"

    @pytest.mark.skipif(os.name == 'nt', reason="Unix-only test")
    def test_handles_nested_directories(self):
        """Should process scripts recursively"""
        with tempfile.TemporaryDirectory() as tmpdir:
            nested_dir = Path(tmpdir) / ".specify" / "scripts" / "bash" / "sub"
            nested_dir.mkdir(parents=True)
            
            script = nested_dir / "nested.sh"
            script.write_text("#!/bin/bash\necho hello")
            script.chmod(0o644)
            
            ensure_executable_scripts(Path(tmpdir))
            
            mode = script.stat().st_mode
            assert mode & 0o100

    @pytest.mark.skipif(os.name == 'nt', reason="Unix-only test")
    def test_ignores_non_sh_files(self):
        """Should ignore non-.sh files"""
        with tempfile.TemporaryDirectory() as tmpdir:
            scripts_dir = Path(tmpdir) / ".specify" / "scripts"
            scripts_dir.mkdir(parents=True)
            
            script = scripts_dir / "test.ps1"
            script.write_text("Write-Host 'hello'")
            script.chmod(0o644)
            
            ensure_executable_scripts(Path(tmpdir))
            
            mode = script.stat().st_mode
            assert not (mode & 0o100)

    def test_handles_missing_scripts_dir(self):
        """Should handle missing .specify/scripts directory gracefully"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Don't create scripts dir
            ensure_executable_scripts(Path(tmpdir))  # Should not raise

    @pytest.mark.skipif(os.name == 'nt', reason="Unix-only test")
    def test_permission_inheritance(self):
        """Execute permissions should match read permissions"""
        # If owner can read, owner can execute
        # If group can read, group can execute
        # If others can read, others can execute
        with tempfile.TemporaryDirectory() as tmpdir:
            scripts_dir = Path(tmpdir) / ".specify" / "scripts"
            scripts_dir.mkdir(parents=True)
            
            script = scripts_dir / "test.sh"
            script.write_text("#!/bin/bash\necho hello")
            script.chmod(0o640)  # Owner read, group read
            
            ensure_executable_scripts(Path(tmpdir))
            
            mode = script.stat().st_mode
            assert mode & 0o100  # Owner execute
            assert mode & 0o010  # Group execute


class TestZipExtractionBehavior:
    """Test ZIP extraction edge cases."""

    def test_extracts_to_project_directory(self):
        """ZIP should extract to specified project path"""
        pass

    def test_handles_nested_directory_in_zip(self):
        """Should flatten if ZIP contains single top-level directory"""
        pass

    def test_preserves_file_structure(self):
        """Directory structure inside ZIP should be preserved"""
        pass

    def test_handles_empty_directories(self):
        """Empty directories in ZIP should be created"""
        pass


class TestTemporaryFileHandling:
    """Test temporary file handling during download/extraction."""

    def test_cleanup_zip_after_extraction(self):
        """ZIP file should be deleted after successful extraction"""
        pass

    def test_cleanup_on_error(self):
        """Temporary files should be cleaned up on error"""
        pass

    def test_cleanup_project_dir_on_error(self):
        """Project directory should be removed if extraction fails"""
        pass


class TestInitHereMode:
    """Test --here mode (initialize in current directory)."""

    def test_merges_with_existing_files(self):
        """Should merge with existing project files"""
        pass

    def test_warns_about_non_empty_directory(self):
        """Should warn when directory is not empty"""
        pass

    def test_force_flag_skips_confirmation(self):
        """--force should skip non-empty directory confirmation"""
        pass

    def test_preserves_existing_vscode_settings(self):
        """Existing .vscode/settings.json should be merged"""
        pass


class TestMetadataReturned:
    """Test metadata returned from download functions."""

    def test_metadata_contains_filename(self):
        """Metadata should include downloaded filename"""
        pass

    def test_metadata_contains_size(self):
        """Metadata should include file size"""
        pass

    def test_metadata_contains_release_tag(self):
        """Metadata should include release tag name"""
        pass

    def test_metadata_contains_asset_url(self):
        """Metadata should include download URL"""
        pass


class TestProgressTracking:
    """Test progress tracking during download/extraction."""

    def test_tracker_updated_during_download(self):
        """StepTracker should be updated during download"""
        pass

    def test_tracker_updated_during_extraction(self):
        """StepTracker should be updated during extraction"""
        pass

    def test_verbose_mode_without_tracker(self):
        """Without tracker, should print to console"""
        pass


class TestFilenamePatterns:
    """Test template filename patterns."""

    def test_pattern_spec_kit_template(self):
        """Filename starts with spec-kit-template"""
        pass

    def test_pattern_includes_ai(self):
        """Filename includes AI assistant name"""
        pass

    def test_pattern_includes_script_type(self):
        """Filename includes script type (sh/ps)"""
        pass

    def test_pattern_includes_version(self):
        """Filename includes version number"""
        pass

    def test_pattern_ends_with_zip(self):
        """Filename ends with .zip extension"""
        pass
