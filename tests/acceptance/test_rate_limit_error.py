"""
Acceptance Tests: Rate Limit Error Formatting
==============================================

BEHAVIOR: Rate limit errors are formatted with detailed troubleshooting info.
The error message includes rate limit info, timestamps, and guidance.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
from specify_cli import _format_rate_limit_error


class MockHeaders:
    """Mock httpx.Headers for testing."""
    def __init__(self, data):
        self._data = data
    
    def __contains__(self, key):
        return key in self._data
    
    def get(self, key, default=None):
        return self._data.get(key, default)


class TestRateLimitErrorFormatting:
    """BEHAVIOR: Error message structure and content."""

    def test_includes_status_code(self):
        """Error message includes HTTP status code."""
        headers = MockHeaders({})
        result = _format_rate_limit_error(403, headers, "https://api.github.com/test")
        assert "403" in result

    def test_includes_url(self):
        """Error message includes the failed URL."""
        headers = MockHeaders({})
        result = _format_rate_limit_error(403, headers, "https://api.github.com/test")
        assert "https://api.github.com/test" in result

    def test_includes_rate_limit_section_when_headers_present(self):
        """Rate Limit Information section appears when headers present."""
        headers = MockHeaders({'X-RateLimit-Limit': '60'})
        result = _format_rate_limit_error(403, headers, "https://api.github.com/test")
        assert "Rate Limit Information" in result

    def test_includes_troubleshooting_tips(self):
        """Troubleshooting Tips section is always present."""
        headers = MockHeaders({})
        result = _format_rate_limit_error(403, headers, "https://api.github.com/test")
        assert "Troubleshooting Tips" in result

    def test_mentions_github_token_option(self):
        """Mentions --github-token CLI option."""
        headers = MockHeaders({})
        result = _format_rate_limit_error(403, headers, "https://api.github.com/test")
        assert "--github-token" in result

    def test_mentions_gh_token_env_var(self):
        """Mentions GH_TOKEN environment variable."""
        headers = MockHeaders({})
        result = _format_rate_limit_error(403, headers, "https://api.github.com/test")
        assert "GH_TOKEN" in result

    def test_mentions_github_token_env_var(self):
        """Mentions GITHUB_TOKEN environment variable."""
        headers = MockHeaders({})
        result = _format_rate_limit_error(403, headers, "https://api.github.com/test")
        assert "GITHUB_TOKEN" in result

    def test_mentions_authenticated_rate_limit(self):
        """Mentions 5,000/hour authenticated vs 60/hour unauthenticated."""
        headers = MockHeaders({})
        result = _format_rate_limit_error(403, headers, "https://api.github.com/test")
        assert "5,000" in result
        assert "60" in result

    def test_mentions_ci_environment(self):
        """Mentions CI/corporate environment consideration."""
        headers = MockHeaders({})
        result = _format_rate_limit_error(403, headers, "https://api.github.com/test")
        assert "CI" in result or "corporate" in result


class TestRateLimitErrorWithHeaders:
    """BEHAVIOR: Rate limit info from headers is included."""

    def test_shows_limit_value(self):
        """Shows the rate limit value."""
        headers = MockHeaders({'X-RateLimit-Limit': '60'})
        result = _format_rate_limit_error(403, headers, "https://api.github.com/test")
        assert "60 requests/hour" in result or "60" in result

    def test_shows_remaining_value(self):
        """Shows remaining requests."""
        headers = MockHeaders({'X-RateLimit-Remaining': '0'})
        result = _format_rate_limit_error(403, headers, "https://api.github.com/test")
        assert "Remaining" in result

    def test_shows_reset_time(self):
        """Shows reset time when available."""
        headers = MockHeaders({'X-RateLimit-Reset': '1700000000'})
        result = _format_rate_limit_error(403, headers, "https://api.github.com/test")
        assert "Resets at" in result

    def test_shows_retry_after(self):
        """Shows retry-after when available."""
        headers = MockHeaders({'Retry-After': '3600'})
        result = _format_rate_limit_error(403, headers, "https://api.github.com/test")
        assert "Retry after" in result or "3600" in result


class TestRateLimitErrorStatusCodes:
    """BEHAVIOR: Works with various HTTP status codes."""

    def test_status_403_forbidden(self):
        """Works with 403 Forbidden."""
        headers = MockHeaders({})
        result = _format_rate_limit_error(403, headers, "https://api.github.com/test")
        assert "403" in result

    def test_status_429_too_many_requests(self):
        """Works with 429 Too Many Requests."""
        headers = MockHeaders({})
        result = _format_rate_limit_error(429, headers, "https://api.github.com/test")
        assert "429" in result

    def test_status_401_unauthorized(self):
        """Works with 401 Unauthorized."""
        headers = MockHeaders({})
        result = _format_rate_limit_error(401, headers, "https://api.github.com/test")
        assert "401" in result
