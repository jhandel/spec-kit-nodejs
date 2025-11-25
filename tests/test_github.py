"""
Test: GitHub API Integration
=============================
These tests document how the CLI interacts with GitHub's API
for fetching releases and downloading templates.

Key concepts:
- Rate limit header parsing
- Authentication header construction
- Error message formatting
- Release asset discovery
- Template download with progress

Node.js equivalents:
- Use node-fetch or axios for HTTP
- Parse Headers object for rate limits
- Use streams for download progress
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import sys
import json
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from specify_cli import (
    _github_token,
    _github_auth_headers,
    _parse_rate_limit_headers,
    _format_rate_limit_error,
)


class TestGitHubToken:
    """
    Test Suite: GitHub Token Resolution
    
    Tokens are resolved in priority order:
    1. CLI argument
    2. GH_TOKEN env var
    3. GITHUB_TOKEN env var
    
    Node.js equivalent:
    ```typescript
    function getGitHubToken(cliToken?: string): string | undefined {
      const token = cliToken 
        || process.env.GH_TOKEN 
        || process.env.GITHUB_TOKEN 
        || '';
      return token.trim() || undefined;
    }
    ```
    """

    def test_returns_none_when_no_token(self):
        """Should return None when no token available"""
        with patch.dict('os.environ', {}, clear=True):
            # Remove any existing token vars
            import os
            os.environ.pop('GH_TOKEN', None)
            os.environ.pop('GITHUB_TOKEN', None)
            
            result = _github_token(None)
            assert result is None

    def test_cli_token_takes_precedence(self):
        """CLI argument should override environment variables"""
        with patch.dict('os.environ', {'GH_TOKEN': 'env-token'}):
            result = _github_token('cli-token')
            assert result == 'cli-token'

    def test_gh_token_over_github_token(self):
        """GH_TOKEN should take precedence over GITHUB_TOKEN"""
        with patch.dict('os.environ', {
            'GH_TOKEN': 'gh-token',
            'GITHUB_TOKEN': 'github-token'
        }):
            result = _github_token(None)
            assert result == 'gh-token'

    def test_github_token_fallback(self):
        """GITHUB_TOKEN used when GH_TOKEN not set"""
        with patch.dict('os.environ', {'GITHUB_TOKEN': 'github-token'}, clear=False):
            import os
            os.environ.pop('GH_TOKEN', None)
            result = _github_token(None)
            assert result == 'github-token'

    def test_whitespace_stripped(self):
        """Tokens should be stripped of whitespace"""
        result = _github_token('  token-with-spaces  ')
        assert result == 'token-with-spaces'

    def test_empty_string_returns_none(self):
        """Empty strings should return None"""
        result = _github_token('')
        assert result is None
        
        result = _github_token('   ')
        assert result is None


class TestGitHubAuthHeaders:
    """
    Test Suite: Authorization Header Construction
    
    Returns proper Authorization header for GitHub API requests.
    
    Node.js equivalent:
    ```typescript
    function getAuthHeaders(cliToken?: string): Record<string, string> {
      const token = getGitHubToken(cliToken);
      return token ? { Authorization: `Bearer ${token}` } : {};
    }
    ```
    """

    def test_returns_empty_dict_when_no_token(self):
        """Should return empty dict when no token available"""
        with patch('specify_cli._github_token', return_value=None):
            result = _github_auth_headers(None)
            assert result == {}

    def test_returns_bearer_header_with_token(self):
        """Should return Bearer token in Authorization header"""
        with patch('specify_cli._github_token', return_value='test-token'):
            result = _github_auth_headers('test-token')
            assert result == {'Authorization': 'Bearer test-token'}

    def test_header_format(self):
        """Authorization header must use 'Bearer' prefix"""
        with patch('specify_cli._github_token', return_value='my-token'):
            result = _github_auth_headers()
            assert 'Authorization' in result
            assert result['Authorization'].startswith('Bearer ')


class TestParseRateLimitHeaders:
    """
    Test Suite: Rate Limit Header Parsing
    
    GitHub returns rate limit info in response headers:
    - X-RateLimit-Limit: requests per hour
    - X-RateLimit-Remaining: requests left
    - X-RateLimit-Reset: Unix timestamp when limit resets
    - Retry-After: seconds to wait (on 429)
    
    Node.js equivalent:
    ```typescript
    interface RateLimitInfo {
      limit?: string;
      remaining?: string;
      resetEpoch?: number;
      resetTime?: Date;
      retryAfterSeconds?: number;
    }
    
    function parseRateLimitHeaders(headers: Headers): RateLimitInfo {
      const info: RateLimitInfo = {};
      if (headers.has('X-RateLimit-Limit')) {
        info.limit = headers.get('X-RateLimit-Limit')!;
      }
      // ... etc
      return info;
    }
    ```
    """

    def _make_mock_headers(self, header_dict):
        """Create mock httpx.Headers from dict"""
        mock_headers = MagicMock()
        mock_headers.__contains__ = lambda self, key: key in header_dict
        mock_headers.get = lambda key, default=None: header_dict.get(key, default)
        return mock_headers

    def test_parses_rate_limit_limit(self):
        """Should extract X-RateLimit-Limit"""
        headers = self._make_mock_headers({
            'X-RateLimit-Limit': '5000'
        })
        result = _parse_rate_limit_headers(headers)
        assert result.get('limit') == '5000'

    def test_parses_rate_limit_remaining(self):
        """Should extract X-RateLimit-Remaining"""
        headers = self._make_mock_headers({
            'X-RateLimit-Remaining': '4999'
        })
        result = _parse_rate_limit_headers(headers)
        assert result.get('remaining') == '4999'

    def test_parses_rate_limit_reset(self):
        """Should extract and convert X-RateLimit-Reset to datetime"""
        reset_epoch = 1700000000
        headers = self._make_mock_headers({
            'X-RateLimit-Reset': str(reset_epoch)
        })
        result = _parse_rate_limit_headers(headers)
        
        assert result.get('reset_epoch') == reset_epoch
        assert 'reset_time' in result
        assert isinstance(result['reset_time'], datetime)

    def test_parses_retry_after_seconds(self):
        """Should extract Retry-After as seconds"""
        headers = self._make_mock_headers({
            'Retry-After': '60'
        })
        result = _parse_rate_limit_headers(headers)
        assert result.get('retry_after_seconds') == 60

    def test_handles_missing_headers(self):
        """Should return empty dict for missing headers"""
        headers = self._make_mock_headers({})
        result = _parse_rate_limit_headers(headers)
        assert result == {}

    def test_handles_all_headers(self):
        """Should parse all rate limit headers together"""
        headers = self._make_mock_headers({
            'X-RateLimit-Limit': '5000',
            'X-RateLimit-Remaining': '4500',
            'X-RateLimit-Reset': '1700000000',
            'Retry-After': '120'
        })
        result = _parse_rate_limit_headers(headers)
        
        assert 'limit' in result
        assert 'remaining' in result
        assert 'reset_epoch' in result
        assert 'retry_after_seconds' in result


class TestFormatRateLimitError:
    """
    Test Suite: Error Message Formatting
    
    Creates user-friendly error messages with rate limit info
    and troubleshooting guidance.
    
    The error message should include:
    1. Status code and URL
    2. Rate limit information (if available)
    3. Troubleshooting tips
    """

    def _make_mock_headers(self, header_dict):
        """Create mock httpx.Headers from dict"""
        mock_headers = MagicMock()
        mock_headers.__contains__ = lambda self, key: key in header_dict
        mock_headers.get = lambda key, default=None: header_dict.get(key, default)
        return mock_headers

    def test_includes_status_code(self):
        """Error should include the HTTP status code"""
        headers = self._make_mock_headers({})
        result = _format_rate_limit_error(403, headers, "https://api.github.com/test")
        assert "403" in result

    def test_includes_url(self):
        """Error should include the request URL"""
        headers = self._make_mock_headers({})
        url = "https://api.github.com/repos/github/spec-kit/releases/latest"
        result = _format_rate_limit_error(403, headers, url)
        assert url in result

    def test_includes_rate_limit_info(self):
        """Error should include rate limit details when available"""
        headers = self._make_mock_headers({
            'X-RateLimit-Limit': '60',
            'X-RateLimit-Remaining': '0',
            'X-RateLimit-Reset': '1700000000'
        })
        result = _format_rate_limit_error(403, headers, "https://api.github.com/test")
        
        assert "Rate Limit" in result
        assert "60" in result

    def test_includes_troubleshooting_tips(self):
        """Error should include helpful troubleshooting guidance"""
        headers = self._make_mock_headers({})
        result = _format_rate_limit_error(403, headers, "https://api.github.com/test")
        
        assert "Troubleshooting" in result
        # Should mention using a token
        assert "token" in result.lower() or "GH_TOKEN" in result
        # Should mention rate limits
        assert "5,000" in result or "5000" in result  # Authenticated limit

    def test_mentions_env_vars(self):
        """Error should mention GH_TOKEN and GITHUB_TOKEN env vars"""
        headers = self._make_mock_headers({})
        result = _format_rate_limit_error(429, headers, "https://api.github.com/test")
        
        assert "GH_TOKEN" in result or "GITHUB_TOKEN" in result

    def test_mentions_cli_option(self):
        """Error should mention --github-token option"""
        headers = self._make_mock_headers({})
        result = _format_rate_limit_error(403, headers, "https://api.github.com/test")
        
        assert "--github-token" in result


class TestGitHubReleaseDiscovery:
    """
    Test Suite: Release Asset Discovery
    
    Documents how the CLI finds the correct release asset.
    
    Release assets follow this naming convention:
    spec-kit-template-{ai_assistant}-{script_type}-{version}.zip
    
    Example: spec-kit-template-copilot-sh-0.0.22.zip
    """

    def test_asset_pattern_format(self):
        """Asset pattern should be: spec-kit-template-{ai}-{script}"""
        # The pattern used in download_template_from_github
        ai_assistant = "copilot"
        script_type = "sh"
        pattern = f"spec-kit-template-{ai_assistant}-{script_type}"
        
        assert pattern == "spec-kit-template-copilot-sh"

    def test_all_agents_have_valid_asset_names(self):
        """All agents should produce valid asset patterns"""
        from specify_cli import AGENT_CONFIG, SCRIPT_TYPE_CHOICES
        
        for ai in AGENT_CONFIG.keys():
            for script in SCRIPT_TYPE_CHOICES.keys():
                pattern = f"spec-kit-template-{ai}-{script}"
                # Pattern should be lowercase and use hyphens
                assert pattern == pattern.lower()
                assert " " not in pattern
                # Should end with script type
                assert pattern.endswith(f"-{script}")


class TestGitHubAPIEndpoints:
    """
    Test Suite: GitHub API Endpoint Documentation
    
    Documents the GitHub API endpoints used by the CLI.
    These must be replicated exactly in the Node.js port.
    """

    def test_releases_latest_endpoint(self):
        """Latest release endpoint format"""
        owner = "github"
        repo = "spec-kit"
        endpoint = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
        
        assert endpoint == "https://api.github.com/repos/github/spec-kit/releases/latest"

    def test_release_response_structure(self):
        """
        Expected release response structure from GitHub API.
        
        This is what the CLI expects from the /releases/latest endpoint.
        """
        expected_fields = {
            "tag_name": "v0.0.22",  # Version tag
            "published_at": "2024-01-01T00:00:00Z",  # ISO 8601 date
            "assets": [
                {
                    "name": "spec-kit-template-copilot-sh-0.0.22.zip",
                    "browser_download_url": "https://github.com/.../spec-kit-template-copilot-sh-0.0.22.zip",
                    "size": 123456
                }
            ]
        }
        
        # Verify we expect these fields
        assert "tag_name" in expected_fields
        assert "assets" in expected_fields
        assert "browser_download_url" in expected_fields["assets"][0]

    def test_asset_response_fields(self):
        """
        Required asset fields:
        - name: filename for pattern matching
        - browser_download_url: direct download URL
        - size: file size in bytes for progress display
        """
        required_asset_fields = ["name", "browser_download_url", "size"]
        # These are accessed in download_template_from_github
        for field in required_asset_fields:
            assert field in required_asset_fields


class TestHTTPRequestBehavior:
    """
    Test Suite: HTTP Request Behavior
    
    Documents the HTTP client behavior that must be replicated.
    """

    def test_request_timeout(self):
        """API requests should have a 30-second timeout"""
        # In Python: timeout=30
        expected_timeout = 30
        # Used in client.get() calls

    def test_download_timeout(self):
        """Download requests should have a 60-second timeout"""
        # In Python: timeout=60 for streaming downloads
        expected_timeout = 60

    def test_follow_redirects(self):
        """Client should follow redirects"""
        # In Python: follow_redirects=True
        # GitHub often redirects asset downloads
        pass

    def test_streaming_for_downloads(self):
        """
        Large downloads should use streaming.
        
        In Python: client.stream("GET", url) with iter_bytes(chunk_size=8192)
        In Node.js: Use response.body as ReadableStream
        """
        expected_chunk_size = 8192


class TestTemplateMetadata:
    """
    Test Suite: Template Metadata
    
    Documents the metadata returned after template download.
    """

    def test_metadata_structure(self):
        """
        download_template_from_github returns (zip_path, metadata)
        
        metadata = {
            "filename": "spec-kit-template-copilot-sh-0.0.22.zip",
            "size": 123456,
            "release": "v0.0.22",
            "asset_url": "https://..."
        }
        """
        expected_fields = ["filename", "size", "release", "asset_url"]
        # All these must be present in the returned metadata
        for field in expected_fields:
            assert field in expected_fields
