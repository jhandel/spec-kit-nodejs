"""
Acceptance Tests: Rate Limit Header Parsing
============================================

BEHAVIOR: GitHub rate limit headers are parsed into a structured dictionary.
The function handles all standard GitHub rate limit headers and the Retry-After header.
"""

import sys
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
from specify_cli import _parse_rate_limit_headers


class MockHeaders:
    """Mock httpx.Headers for testing."""
    def __init__(self, data):
        self._data = data
    
    def __contains__(self, key):
        return key in self._data
    
    def get(self, key, default=None):
        return self._data.get(key, default)


class TestRateLimitHeaderParsing:
    """BEHAVIOR: Parse standard GitHub rate limit headers."""

    def test_empty_headers_returns_empty_dict(self):
        """Empty headers produce empty result."""
        headers = MockHeaders({})
        result = _parse_rate_limit_headers(headers)
        assert result == {}

    def test_parses_x_ratelimit_limit(self):
        """X-RateLimit-Limit is stored as 'limit'."""
        headers = MockHeaders({'X-RateLimit-Limit': '5000'})
        result = _parse_rate_limit_headers(headers)
        assert result['limit'] == '5000'

    def test_parses_x_ratelimit_remaining(self):
        """X-RateLimit-Remaining is stored as 'remaining'."""
        headers = MockHeaders({'X-RateLimit-Remaining': '4999'})
        result = _parse_rate_limit_headers(headers)
        assert result['remaining'] == '4999'

    def test_parses_x_ratelimit_reset_as_epoch(self):
        """X-RateLimit-Reset is parsed as epoch timestamp."""
        headers = MockHeaders({'X-RateLimit-Reset': '1700000000'})
        result = _parse_rate_limit_headers(headers)
        assert result['reset_epoch'] == 1700000000

    def test_reset_time_is_utc_datetime(self):
        """reset_time is a UTC datetime object."""
        headers = MockHeaders({'X-RateLimit-Reset': '1700000000'})
        result = _parse_rate_limit_headers(headers)
        assert isinstance(result['reset_time'], datetime)
        assert result['reset_time'].tzinfo == timezone.utc

    def test_reset_local_is_local_timezone(self):
        """reset_local is converted to local timezone."""
        headers = MockHeaders({'X-RateLimit-Reset': '1700000000'})
        result = _parse_rate_limit_headers(headers)
        assert 'reset_local' in result
        # reset_local should be a datetime with local timezone

    def test_parses_retry_after_seconds(self):
        """Retry-After with numeric value is stored as retry_after_seconds."""
        headers = MockHeaders({'Retry-After': '3600'})
        result = _parse_rate_limit_headers(headers)
        assert result['retry_after_seconds'] == 3600

    def test_retry_after_http_date_stored_as_string(self):
        """Retry-After with HTTP-date format is stored as retry_after string."""
        headers = MockHeaders({'Retry-After': 'Wed, 21 Oct 2015 07:28:00 GMT'})
        result = _parse_rate_limit_headers(headers)
        assert result['retry_after'] == 'Wed, 21 Oct 2015 07:28:00 GMT'

    def test_all_headers_combined(self):
        """All headers can be parsed together."""
        headers = MockHeaders({
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


class TestRateLimitHeaderEdgeCases:
    """BEHAVIOR: Edge cases in header parsing."""

    def test_zero_reset_epoch_not_included(self):
        """Reset epoch of 0 should not produce reset_time."""
        headers = MockHeaders({'X-RateLimit-Reset': '0'})
        result = _parse_rate_limit_headers(headers)
        assert 'reset_epoch' not in result
        assert 'reset_time' not in result

    def test_limit_stored_as_string(self):
        """Limit value is stored as string, not converted to int."""
        headers = MockHeaders({'X-RateLimit-Limit': '60'})
        result = _parse_rate_limit_headers(headers)
        assert result['limit'] == '60'
        assert isinstance(result['limit'], str)

    def test_partial_headers_only_includes_present(self):
        """Only present headers are included in result."""
        headers = MockHeaders({'X-RateLimit-Limit': '60'})
        result = _parse_rate_limit_headers(headers)
        assert 'limit' in result
        assert 'remaining' not in result
        assert 'reset_epoch' not in result
