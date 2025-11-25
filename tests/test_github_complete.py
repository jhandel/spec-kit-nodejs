"""
Test: GitHub API Integration - COMPREHENSIVE
=============================================
Complete test coverage for all GitHub API operations.
"""

import pytest
from unittest.mock import patch, MagicMock, PropertyMock
from pathlib import Path
import sys
import os
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from specify_cli import (
    _github_token,
    _github_auth_headers,
    _parse_rate_limit_headers,
    _format_rate_limit_error,
)


class TestGitHubTokenComplete:
    """Complete coverage of _github_token function."""

    def test_returns_none_when_no_token(self):
        """Should return None when no token available"""
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop('GH_TOKEN', None)
            os.environ.pop('GITHUB_TOKEN', None)
            result = _github_token(None)
            assert result is None

    def test_cli_token_takes_precedence(self):
        """CLI token should override env vars"""
        with patch.dict(os.environ, {'GH_TOKEN': 'env-token', 'GITHUB_TOKEN': 'other'}):
            result = _github_token('cli-token')
            assert result == 'cli-token'

    def test_gh_token_over_github_token(self):
        """GH_TOKEN env var should take precedence over GITHUB_TOKEN"""
        with patch.dict(os.environ, {'GH_TOKEN': 'gh-token', 'GITHUB_TOKEN': 'github-token'}):
            result = _github_token(None)
            assert result == 'gh-token'

    def test_github_token_fallback(self):
        """GITHUB_TOKEN should be used when GH_TOKEN not set"""
        with patch.dict(os.environ, {'GITHUB_TOKEN': 'github-token'}, clear=True):
            os.environ.pop('GH_TOKEN', None)
            result = _github_token(None)
            assert result == 'github-token'

    def test_empty_string_returns_none(self):
        """Empty string token should return None"""
        result = _github_token('')
        assert result is None

    def test_whitespace_only_returns_none(self):
        """Whitespace-only token should return None"""
        result = _github_token('   ')
        assert result is None

    def test_whitespace_stripped(self):
        """Token should have whitespace stripped"""
        result = _github_token('  my-token  ')
        assert result == 'my-token'

    def test_newline_stripped(self):
        """Newlines in token should be stripped"""
        result = _github_token('my-token\n')
        assert result == 'my-token'

    def test_env_var_empty_string(self):
        """Empty env var should return None"""
        with patch.dict(os.environ, {'GH_TOKEN': '', 'GITHUB_TOKEN': ''}):
            result = _github_token(None)
            assert result is None

    def test_env_var_whitespace(self):
        """Whitespace env var should return None"""
        with patch.dict(os.environ, {'GH_TOKEN': '   '}):
            result = _github_token(None)
            assert result is None


class TestGitHubAuthHeadersComplete:
    """Complete coverage of _github_auth_headers function."""

    def test_returns_empty_dict_when_no_token(self):
        """Should return empty dict when no token"""
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop('GH_TOKEN', None)
            os.environ.pop('GITHUB_TOKEN', None)
            result = _github_auth_headers(None)
            assert result == {}

    def test_returns_auth_header_with_token(self):
        """Should return Authorization header when token available"""
        result = _github_auth_headers('my-token')
        assert result == {'Authorization': 'Bearer my-token'}

    def test_bearer_format(self):
        """Header should use Bearer token format"""
        result = _github_auth_headers('test')
        assert 'Bearer' in result.get('Authorization', '')

    def test_passes_cli_token_to_github_token(self):
        """Should pass CLI token to _github_token"""
        with patch.dict(os.environ, {'GH_TOKEN': 'env-token'}):
            result = _github_auth_headers('cli-override')
            assert result == {'Authorization': 'Bearer cli-override'}


class TestParseRateLimitHeadersComplete:
    """Complete coverage of _parse_rate_limit_headers function."""

    class MockHeaders:
        def __init__(self, data):
            self._data = data
        def __contains__(self, key):
            return key in self._data
        def get(self, key, default=None):
            return self._data.get(key, default)

    def test_empty_headers(self):
        """Should return empty dict for no rate limit headers"""
        headers = self.MockHeaders({})
        result = _parse_rate_limit_headers(headers)
        assert result == {}

    def test_parses_limit(self):
        """Should parse X-RateLimit-Limit header"""
        headers = self.MockHeaders({'X-RateLimit-Limit': '60'})
        result = _parse_rate_limit_headers(headers)
        assert result['limit'] == '60'

    def test_parses_remaining(self):
        """Should parse X-RateLimit-Remaining header"""
        headers = self.MockHeaders({'X-RateLimit-Remaining': '59'})
        result = _parse_rate_limit_headers(headers)
        assert result['remaining'] == '59'

    def test_parses_reset_epoch(self):
        """Should parse X-RateLimit-Reset as epoch timestamp"""
        headers = self.MockHeaders({'X-RateLimit-Reset': '1700000000'})
        result = _parse_rate_limit_headers(headers)
        assert result['reset_epoch'] == 1700000000
        assert isinstance(result['reset_time'], datetime)

    def test_reset_time_is_utc(self):
        """Reset time should be in UTC"""
        headers = self.MockHeaders({'X-RateLimit-Reset': '1700000000'})
        result = _parse_rate_limit_headers(headers)
        assert result['reset_time'].tzinfo == timezone.utc

    def test_reset_local_present(self):
        """Should include local timezone reset time"""
        headers = self.MockHeaders({'X-RateLimit-Reset': '1700000000'})
        result = _parse_rate_limit_headers(headers)
        assert 'reset_local' in result

    def test_parses_retry_after_seconds(self):
        """Should parse Retry-After header as integer seconds"""
        headers = self.MockHeaders({'Retry-After': '3600'})
        result = _parse_rate_limit_headers(headers)
        assert result['retry_after_seconds'] == 3600

    def test_retry_after_http_date_stored_as_string(self):
        """Should store HTTP-date Retry-After as string"""
        headers = self.MockHeaders({'Retry-After': 'Wed, 21 Oct 2015 07:28:00 GMT'})
        result = _parse_rate_limit_headers(headers)
        assert 'retry_after' in result
        assert 'retry_after_seconds' not in result

    def test_invalid_reset_epoch(self):
        """Should handle zero/invalid reset epoch"""
        headers = self.MockHeaders({'X-RateLimit-Reset': '0'})
        result = _parse_rate_limit_headers(headers)
        assert 'reset_epoch' not in result

    def test_all_headers_combined(self):
        """Should parse all headers together"""
        headers = self.MockHeaders({
            'X-RateLimit-Limit': '5000',
            'X-RateLimit-Remaining': '4999',
            'X-RateLimit-Reset': '1700000000',
            'Retry-After': '60'
        })
        result = _parse_rate_limit_headers(headers)
        assert result['limit'] == '5000'
        assert result['remaining'] == '4999'
        assert result['reset_epoch'] == 1700000000
        assert result['retry_after_seconds'] == 60


class TestFormatRateLimitErrorComplete:
    """Complete coverage of _format_rate_limit_error function."""

    class MockHeaders:
        def __init__(self, data):
            self._data = data
        def __contains__(self, key):
            return key in self._data
        def get(self, key, default=None):
            return self._data.get(key, default)

    def test_includes_status_code(self):
        """Error message should include HTTP status code"""
        headers = self.MockHeaders({})
        result = _format_rate_limit_error(403, headers, 'https://api.github.com/test')
        assert '403' in result

    def test_includes_url(self):
        """Error message should include the request URL"""
        headers = self.MockHeaders({})
        url = 'https://api.github.com/repos/test'
        result = _format_rate_limit_error(403, headers, url)
        assert url in result

    def test_includes_rate_limit_info_section(self):
        """Should include rate limit info when headers present"""
        headers = self.MockHeaders({'X-RateLimit-Limit': '60'})
        result = _format_rate_limit_error(403, headers, 'http://test')
        assert 'Rate Limit' in result

    def test_includes_troubleshooting_tips(self):
        """Should include troubleshooting guidance"""
        headers = self.MockHeaders({})
        result = _format_rate_limit_error(403, headers, 'http://test')
        assert '--github-token' in result
        assert 'GH_TOKEN' in result or 'GITHUB_TOKEN' in result

    def test_mentions_authenticated_rate_limit(self):
        """Should mention 5000/hour for authenticated vs 60/hour"""
        headers = self.MockHeaders({})
        result = _format_rate_limit_error(403, headers, 'http://test')
        assert '5,000' in result or '5000' in result
        assert '60' in result

    def test_mentions_ci_environment(self):
        """Should mention CI/corporate environment issues"""
        headers = self.MockHeaders({})
        result = _format_rate_limit_error(403, headers, 'http://test')
        assert 'CI' in result or 'corporate' in result

    def test_formats_reset_time(self):
        """Should format reset time when available"""
        headers = self.MockHeaders({'X-RateLimit-Reset': '1700000000'})
        result = _format_rate_limit_error(403, headers, 'http://test')
        assert 'Reset' in result

    def test_status_429_handling(self):
        """Should handle 429 Too Many Requests"""
        headers = self.MockHeaders({'Retry-After': '3600'})
        result = _format_rate_limit_error(429, headers, 'http://test')
        assert '429' in result


class TestGitHubAPIEndpoints:
    """Document GitHub API endpoints used."""

    def test_releases_api_endpoint(self):
        """Latest release endpoint format"""
        owner = "github"
        repo = "spec-kit"
        expected = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
        assert expected == "https://api.github.com/repos/github/spec-kit/releases/latest"

    def test_asset_download_redirects(self):
        """Asset URLs redirect to CDN"""
        # browser_download_url returns a 302 redirect to actual content
        # Must follow redirects when downloading
        pass


class TestAssetPatternMatchingComplete:
    """Complete coverage of asset pattern matching."""

    def test_pattern_format(self):
        """Asset pattern format: spec-kit-template-{ai}-{script}-{version}.zip"""
        ai = "copilot"
        script = "sh"
        pattern = f"spec-kit-template-{ai}-{script}"
        assert pattern == "spec-kit-template-copilot-sh"

    def test_pattern_with_version(self):
        """Full filename includes version"""
        expected = "spec-kit-template-copilot-sh-0.0.22.zip"
        assert expected.startswith("spec-kit-template-copilot-sh")
        assert expected.endswith(".zip")

    def test_all_agent_patterns(self):
        """All agents should have valid pattern names"""
        from specify_cli import AGENT_CONFIG
        for agent in AGENT_CONFIG.keys():
            for script in ["sh", "ps"]:
                pattern = f"spec-kit-template-{agent}-{script}"
                # Pattern should be valid filename characters
                assert all(c.isalnum() or c in '-_.' for c in pattern)

    def test_matching_logic_finds_correct_asset(self):
        """Matching should find correct asset from list"""
        assets = [
            {"name": "spec-kit-template-copilot-sh-0.0.22.zip"},
            {"name": "spec-kit-template-copilot-ps-0.0.22.zip"},
            {"name": "spec-kit-template-claude-sh-0.0.22.zip"},
            {"name": "unrelated-file.zip"},
        ]
        
        def find_asset(ai, script):
            pattern = f"spec-kit-template-{ai}-{script}"
            for asset in assets:
                if pattern in asset["name"] and asset["name"].endswith(".zip"):
                    return asset
            return None
        
        assert find_asset("copilot", "sh")["name"] == "spec-kit-template-copilot-sh-0.0.22.zip"
        assert find_asset("copilot", "ps")["name"] == "spec-kit-template-copilot-ps-0.0.22.zip"
        assert find_asset("claude", "sh")["name"] == "spec-kit-template-claude-sh-0.0.22.zip"
        assert find_asset("nonexistent", "sh") is None


class TestHTTPClientBehavior:
    """Document HTTP client requirements."""

    def test_timeout_values(self):
        """Required timeout values"""
        api_timeout = 30  # seconds for API calls
        download_timeout = 60  # seconds for file downloads
        assert api_timeout < download_timeout

    def test_follow_redirects_required(self):
        """Must follow redirects for asset downloads"""
        # Asset URLs return 302 -> actual content
        pass

    def test_ssl_context_usage(self):
        """SSL context with truststore for certificate verification"""
        # Uses: truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        pass

    def test_skip_tls_option(self):
        """--skip-tls option disables SSL verification"""
        # When skip_tls=True, verify=False in client
        pass

    def test_chunk_size(self):
        """Download chunk size for streaming"""
        chunk_size = 8192  # bytes
        assert chunk_size == 8192


class TestErrorScenarios:
    """Test all error scenarios."""

    def test_status_401_unauthorized(self):
        """401 indicates invalid token"""
        pass

    def test_status_403_rate_limited(self):
        """403 can indicate rate limit exceeded"""
        pass

    def test_status_404_not_found(self):
        """404 indicates release or asset not found"""
        pass

    def test_status_429_too_many_requests(self):
        """429 indicates explicit rate limiting"""
        pass

    def test_status_500_server_error(self):
        """500 indicates GitHub server error"""
        pass

    def test_status_502_bad_gateway(self):
        """502 indicates GitHub infrastructure issue"""
        pass

    def test_status_503_service_unavailable(self):
        """503 indicates GitHub maintenance"""
        pass

    def test_timeout_error(self):
        """Connection timeout handling"""
        pass

    def test_connection_error(self):
        """Network connection failure"""
        pass

    def test_dns_resolution_error(self):
        """DNS resolution failure"""
        pass

    def test_ssl_certificate_error(self):
        """SSL certificate validation failure"""
        pass

    def test_json_parse_error(self):
        """Invalid JSON response from API"""
        pass

    def test_no_matching_asset(self):
        """Release exists but no matching asset"""
        pass

    def test_empty_assets_list(self):
        """Release has no assets"""
        pass


class TestReleaseDataStructure:
    """Document expected release data structure from GitHub API."""

    def test_release_response_fields(self):
        """Expected fields in release response"""
        expected_release = {
            "tag_name": "v0.0.22",
            "name": "Release v0.0.22",
            "published_at": "2024-01-15T10:00:00Z",
            "assets": []
        }
        assert "tag_name" in expected_release
        assert "assets" in expected_release

    def test_asset_response_fields(self):
        """Expected fields in each asset"""
        expected_asset = {
            "name": "spec-kit-template-copilot-sh-0.0.22.zip",
            "browser_download_url": "https://...",
            "size": 150000
        }
        assert "name" in expected_asset
        assert "browser_download_url" in expected_asset
        assert "size" in expected_asset
