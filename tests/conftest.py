"""
pytest configuration and fixtures for Specify CLI tests.

This module provides:
- Shared fixtures for all tests
- pytest markers configuration
- Test utilities
"""

import pytest
import tempfile
import shutil
import os
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def temp_dir():
    """
    Create a temporary directory for tests.
    
    Automatically cleaned up after each test.
    
    Node.js equivalent (vitest):
    ```typescript
    import { mkdtempSync, rmSync } from 'fs';
    import { tmpdir } from 'os';
    import { join } from 'path';
    
    let tempDir: string;
    
    beforeEach(() => {
      tempDir = mkdtempSync(join(tmpdir(), 'specify-test-'));
    });
    
    afterEach(() => {
      rmSync(tempDir, { recursive: true, force: true });
    });
    ```
    """
    temp_path = tempfile.mkdtemp(prefix="specify_test_")
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def mock_env():
    """
    Context manager to temporarily modify environment variables.
    
    Node.js equivalent:
    ```typescript
    function withEnv(vars: Record<string, string>, fn: () => void) {
      const original: Record<string, string | undefined> = {};
      for (const [key, value] of Object.entries(vars)) {
        original[key] = process.env[key];
        process.env[key] = value;
      }
      try {
        fn();
      } finally {
        for (const [key, value] of Object.entries(original)) {
          if (value === undefined) {
            delete process.env[key];
          } else {
            process.env[key] = value;
          }
        }
      }
    }
    ```
    """
    original_env = os.environ.copy()
    
    def _mock_env(vars):
        os.environ.update(vars)
    
    yield _mock_env
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def project_root():
    """
    Return the project root directory.
    """
    return Path(__file__).parent.parent


@pytest.fixture
def sample_release_response():
    """
    Sample GitHub release API response for mocking.
    
    This represents the structure returned by:
    GET https://api.github.com/repos/github/spec-kit/releases/latest
    """
    return {
        "tag_name": "v0.0.22",
        "name": "Release v0.0.22",
        "published_at": "2024-01-15T10:00:00Z",
        "assets": [
            {
                "name": "spec-kit-template-copilot-sh-0.0.22.zip",
                "browser_download_url": "https://github.com/github/spec-kit/releases/download/v0.0.22/spec-kit-template-copilot-sh-0.0.22.zip",
                "size": 150000
            },
            {
                "name": "spec-kit-template-copilot-ps-0.0.22.zip",
                "browser_download_url": "https://github.com/github/spec-kit/releases/download/v0.0.22/spec-kit-template-copilot-ps-0.0.22.zip",
                "size": 155000
            },
            {
                "name": "spec-kit-template-claude-sh-0.0.22.zip",
                "browser_download_url": "https://github.com/github/spec-kit/releases/download/v0.0.22/spec-kit-template-claude-sh-0.0.22.zip",
                "size": 148000
            },
            {
                "name": "spec-kit-template-claude-ps-0.0.22.zip",
                "browser_download_url": "https://github.com/github/spec-kit/releases/download/v0.0.22/spec-kit-template-claude-ps-0.0.22.zip",
                "size": 152000
            }
        ]
    }


@pytest.fixture
def sample_rate_limit_headers():
    """
    Sample GitHub rate limit headers for testing.
    """
    return {
        "X-RateLimit-Limit": "60",
        "X-RateLimit-Remaining": "0",
        "X-RateLimit-Reset": "1700000000",
        "Retry-After": "3600"
    }


# =============================================================================
# Markers Configuration
# =============================================================================

def pytest_configure(config):
    """
    Register custom pytest markers.
    
    Usage in tests:
    - @pytest.mark.integration - Slow integration tests
    - @pytest.mark.network - Tests requiring network
    - @pytest.mark.slow - Particularly slow tests
    - @pytest.mark.windows - Windows-only tests
    - @pytest.mark.unix - Unix-only tests
    """
    config.addinivalue_line(
        "markers", 
        "integration: marks tests as integration tests (may be slow, deselect with '-m \"not integration\"')"
    )
    config.addinivalue_line(
        "markers", 
        "network: marks tests as requiring network access"
    )
    config.addinivalue_line(
        "markers", 
        "slow: marks tests as slow running"
    )
    config.addinivalue_line(
        "markers", 
        "windows: marks tests to run only on Windows"
    )
    config.addinivalue_line(
        "markers", 
        "unix: marks tests to run only on Unix/macOS"
    )


def pytest_collection_modifyitems(config, items):
    """
    Automatically skip platform-specific tests.
    """
    skip_windows = pytest.mark.skip(reason="Windows-only test")
    skip_unix = pytest.mark.skip(reason="Unix-only test")
    
    for item in items:
        if "windows" in item.keywords and os.name != "nt":
            item.add_marker(skip_windows)
        if "unix" in item.keywords and os.name == "nt":
            item.add_marker(skip_unix)


# =============================================================================
# Test Utilities
# =============================================================================

class MockHeaders:
    """
    Mock HTTP headers for testing rate limit parsing.
    
    Simulates httpx.Headers behavior.
    """
    
    def __init__(self, headers_dict):
        self._headers = headers_dict
    
    def __contains__(self, key):
        return key in self._headers
    
    def get(self, key, default=None):
        return self._headers.get(key, default)


def create_mock_zip(path, contents):
    """
    Create a mock ZIP file for testing extraction.
    
    Args:
        path: Path to create ZIP file
        contents: Dict mapping archive paths to content strings
    
    Example:
        create_mock_zip("test.zip", {
            ".specify/memory/constitution.md": "# Constitution",
            ".specify/scripts/bash/common.sh": "#!/bin/bash"
        })
    """
    import zipfile
    
    with zipfile.ZipFile(path, 'w') as zf:
        for archive_path, content in contents.items():
            zf.writestr(archive_path, content)


def assert_files_exist(base_path, file_list):
    """
    Assert that all files in the list exist.
    
    Args:
        base_path: Base directory path
        file_list: List of relative file paths
    
    Example:
        assert_files_exist("/project", [
            ".specify/memory/constitution.md",
            ".vscode/settings.json"
        ])
    """
    base = Path(base_path)
    missing = []
    
    for file_path in file_list:
        full_path = base / file_path
        if not full_path.exists():
            missing.append(file_path)
    
    if missing:
        raise AssertionError(
            f"Missing files:\n" + "\n".join(f"  - {f}" for f in missing)
        )


def assert_json_contains(json_path, expected_keys):
    """
    Assert that a JSON file contains expected keys.
    
    Args:
        json_path: Path to JSON file
        expected_keys: Dict of expected key-value pairs (nested keys use dot notation)
    
    Example:
        assert_json_contains("settings.json", {
            "editor.formatOnSave": True,
            "python.linting.enabled": True
        })
    """
    import json
    
    with open(json_path) as f:
        data = json.load(f)
    
    def get_nested(obj, key):
        parts = key.split('.')
        for part in parts:
            if isinstance(obj, dict):
                obj = obj.get(part)
            else:
                return None
        return obj
    
    for key, expected_value in expected_keys.items():
        actual_value = get_nested(data, key)
        if actual_value != expected_value:
            raise AssertionError(
                f"JSON key '{key}': expected {expected_value!r}, got {actual_value!r}"
            )
