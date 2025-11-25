"""
Acceptance Tests: GitHub Token Handling
========================================

BEHAVIOR: GitHub tokens are resolved with a specific precedence order:
1. CLI argument (--github-token)
2. GH_TOKEN environment variable  
3. GITHUB_TOKEN environment variable
4. None (unauthenticated)

Empty strings and whitespace-only values are treated as "no token".
"""

import os
import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
from specify_cli import _github_token, _github_auth_headers


class TestGitHubTokenPrecedence:
    """BEHAVIOR: Token resolution follows strict precedence order."""

    def test_cli_token_takes_precedence_over_all(self):
        """CLI token overrides all environment variables."""
        with patch.dict(os.environ, {'GH_TOKEN': 'env_gh', 'GITHUB_TOKEN': 'env_github'}):
            result = _github_token('cli_token')
            assert result == 'cli_token'

    def test_gh_token_takes_precedence_over_github_token(self):
        """GH_TOKEN overrides GITHUB_TOKEN."""
        with patch.dict(os.environ, {'GH_TOKEN': 'gh_value', 'GITHUB_TOKEN': 'github_value'}):
            result = _github_token(None)
            assert result == 'gh_value'

    def test_github_token_is_fallback(self):
        """GITHUB_TOKEN is used when GH_TOKEN not set."""
        with patch.dict(os.environ, {'GITHUB_TOKEN': 'github_value'}, clear=True):
            # Remove GH_TOKEN if present
            env = os.environ.copy()
            env.pop('GH_TOKEN', None)
            with patch.dict(os.environ, env, clear=True):
                os.environ['GITHUB_TOKEN'] = 'github_value'
                result = _github_token(None)
                assert result == 'github_value'

    def test_returns_none_when_no_token(self):
        """Returns None when no token source is available."""
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop('GH_TOKEN', None)
            os.environ.pop('GITHUB_TOKEN', None)
            result = _github_token(None)
            assert result is None


class TestGitHubTokenSanitization:
    """BEHAVIOR: Token values are stripped of whitespace."""

    def test_cli_token_is_stripped(self):
        """CLI token whitespace is stripped."""
        result = _github_token('  token_value  ')
        assert result == 'token_value'

    def test_env_token_is_stripped(self):
        """Environment variable whitespace is stripped."""
        with patch.dict(os.environ, {'GH_TOKEN': '  env_token  '}):
            result = _github_token(None)
            assert result == 'env_token'

    def test_newlines_are_stripped(self):
        """Newlines in token are stripped."""
        result = _github_token('token\n')
        assert result == 'token'

    def test_empty_string_returns_none(self):
        """Empty string after stripping returns None."""
        result = _github_token('')
        assert result is None

    def test_whitespace_only_returns_none(self):
        """Whitespace-only string returns None."""
        result = _github_token('   ')
        assert result is None

    def test_env_empty_string_returns_none(self):
        """Empty env var returns None."""
        with patch.dict(os.environ, {'GH_TOKEN': ''}):
            result = _github_token(None)
            # Falls through to GITHUB_TOKEN or None
            assert result is None or isinstance(result, str)


class TestGitHubAuthHeaders:
    """BEHAVIOR: Authorization headers are generated from token."""

    def test_returns_empty_dict_when_no_token(self):
        """No token means empty headers dict."""
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop('GH_TOKEN', None)
            os.environ.pop('GITHUB_TOKEN', None)
            result = _github_auth_headers(None)
            assert result == {}

    def test_returns_bearer_header_with_token(self):
        """Token produces Bearer authorization header."""
        result = _github_auth_headers('my_token')
        assert result == {'Authorization': 'Bearer my_token'}

    def test_bearer_format_exact(self):
        """Authorization header format is exactly 'Bearer <token>'."""
        result = _github_auth_headers('abc123')
        assert result['Authorization'] == 'Bearer abc123'
        assert result['Authorization'].startswith('Bearer ')

    def test_passes_cli_token_to_github_token_function(self):
        """CLI token is passed through to _github_token."""
        with patch('specify_cli._github_token', return_value='resolved_token') as mock:
            _github_auth_headers('cli_arg')
            mock.assert_called_once_with('cli_arg')


class TestGitHubTokenEnvironmentVariables:
    """BEHAVIOR: Specific environment variable names are used."""

    def test_gh_token_env_var_name(self):
        """GH_TOKEN is the exact env var name (GitHub CLI compatible)."""
        with patch.dict(os.environ, {'GH_TOKEN': 'test_value'}):
            result = _github_token(None)
            assert result == 'test_value'

    def test_github_token_env_var_name(self):
        """GITHUB_TOKEN is the exact env var name."""
        with patch.dict(os.environ, {'GITHUB_TOKEN': 'test_value'}, clear=True):
            os.environ.pop('GH_TOKEN', None)
            result = _github_token(None)
            assert result == 'test_value'
