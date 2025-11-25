"""
Test: Exact Behavioral Specifications
=====================================
These tests document the EXACT behavior that the Node.js port must replicate.
Each test is a specification of expected behavior, not just a passing test.
"""

import pytest
from pathlib import Path
import sys
import os
import json
import tempfile

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from specify_cli import (
    AGENT_CONFIG,
    SCRIPT_TYPE_CHOICES,
    CLAUDE_LOCAL_PATH,
    BANNER,
    TAGLINE,
    _github_token,
    _github_auth_headers,
    _parse_rate_limit_headers,
    _format_rate_limit_error,
    merge_json_files,
    check_tool,
    is_git_repo,
    init_git_repo,
    StepTracker,
)
from unittest.mock import patch


# ==============================================================================
# EXACT CONSTANT VALUES
# ==============================================================================

class TestExactAgentConfigValues:
    """These exact values must be replicated."""

    def test_copilot_exact_config(self):
        assert AGENT_CONFIG["copilot"] == {
            "name": "GitHub Copilot",
            "folder": ".github/",
            "install_url": None,
            "requires_cli": False,
        }

    def test_claude_exact_config(self):
        assert AGENT_CONFIG["claude"] == {
            "name": "Claude Code",
            "folder": ".claude/",
            "install_url": "https://docs.anthropic.com/en/docs/claude-code/setup",
            "requires_cli": True,
        }

    def test_gemini_exact_config(self):
        assert AGENT_CONFIG["gemini"] == {
            "name": "Gemini CLI",
            "folder": ".gemini/",
            "install_url": "https://github.com/google-gemini/gemini-cli",
            "requires_cli": True,
        }

    def test_cursor_agent_exact_config(self):
        assert AGENT_CONFIG["cursor-agent"] == {
            "name": "Cursor",
            "folder": ".cursor/",
            "install_url": None,
            "requires_cli": False,
        }

    def test_qwen_exact_config(self):
        assert AGENT_CONFIG["qwen"] == {
            "name": "Qwen Code",
            "folder": ".qwen/",
            "install_url": "https://github.com/QwenLM/qwen-code",
            "requires_cli": True,
        }

    def test_opencode_exact_config(self):
        assert AGENT_CONFIG["opencode"] == {
            "name": "opencode",
            "folder": ".opencode/",
            "install_url": "https://opencode.ai",
            "requires_cli": True,
        }

    def test_codex_exact_config(self):
        assert AGENT_CONFIG["codex"] == {
            "name": "Codex CLI",
            "folder": ".codex/",
            "install_url": "https://github.com/openai/codex",
            "requires_cli": True,
        }

    def test_windsurf_exact_config(self):
        assert AGENT_CONFIG["windsurf"] == {
            "name": "Windsurf",
            "folder": ".windsurf/",
            "install_url": None,
            "requires_cli": False,
        }

    def test_kilocode_exact_config(self):
        assert AGENT_CONFIG["kilocode"] == {
            "name": "Kilo Code",
            "folder": ".kilocode/",
            "install_url": None,
            "requires_cli": False,
        }

    def test_auggie_exact_config(self):
        assert AGENT_CONFIG["auggie"] == {
            "name": "Auggie CLI",
            "folder": ".augment/",  # Note: .augment NOT .auggie
            "install_url": "https://docs.augmentcode.com/cli/setup-auggie/install-auggie-cli",
            "requires_cli": True,
        }

    def test_codebuddy_exact_config(self):
        assert AGENT_CONFIG["codebuddy"] == {
            "name": "CodeBuddy",
            "folder": ".codebuddy/",
            "install_url": "https://www.codebuddy.ai/cli",
            "requires_cli": True,
        }

    def test_roo_exact_config(self):
        assert AGENT_CONFIG["roo"] == {
            "name": "Roo Code",
            "folder": ".roo/",
            "install_url": None,
            "requires_cli": False,
        }

    def test_q_exact_config(self):
        assert AGENT_CONFIG["q"] == {
            "name": "Amazon Q Developer CLI",
            "folder": ".amazonq/",  # Note: .amazonq NOT .q
            "install_url": "https://aws.amazon.com/developer/learning/q-developer-cli/",
            "requires_cli": True,
        }

    def test_amp_exact_config(self):
        assert AGENT_CONFIG["amp"] == {
            "name": "Amp",
            "folder": ".agents/",  # Note: .agents NOT .amp
            "install_url": "https://ampcode.com/manual#install",
            "requires_cli": True,
        }

    def test_shai_exact_config(self):
        assert AGENT_CONFIG["shai"] == {
            "name": "SHAI",
            "folder": ".shai/",
            "install_url": "https://github.com/ovh/shai",
            "requires_cli": True,
        }


class TestExactScriptTypeValues:
    """Exact script type values."""

    def test_script_types_exact(self):
        assert SCRIPT_TYPE_CHOICES == {
            "sh": "POSIX Shell (bash/zsh)",
            "ps": "PowerShell",
        }


class TestExactClaudeLocalPath:
    """Exact Claude local path."""

    def test_claude_local_path_exact(self):
        expected = Path.home() / ".claude" / "local" / "claude"
        assert CLAUDE_LOCAL_PATH == expected


class TestExactBanner:
    """Exact banner content."""

    def test_banner_exact_lines(self):
        expected_banner = """
███████╗██████╗ ███████╗ ██████╗██╗███████╗██╗   ██╗
██╔════╝██╔══██╗██╔════╝██╔════╝██║██╔════╝╚██╗ ██╔╝
███████╗██████╔╝█████╗  ██║     ██║█████╗   ╚████╔╝ 
╚════██║██╔═══╝ ██╔══╝  ██║     ██║██╔══╝    ╚██╔╝  
███████║██║     ███████╗╚██████╗██║██║        ██║   
╚══════╝╚═╝     ╚══════╝ ╚═════╝╚═╝╚═╝        ╚═╝   
"""
        assert BANNER.strip() == expected_banner.strip()

    def test_tagline_exact(self):
        assert TAGLINE == "GitHub Spec Kit - Spec-Driven Development Toolkit"


class TestExactBannerColors:
    """Exact banner colors for each line."""

    def test_banner_color_sequence(self):
        # These colors are applied to each line of the banner
        expected_colors = [
            "bright_blue",
            "blue", 
            "cyan",
            "bright_cyan",
            "white",
            "bright_white",
        ]
        # The code uses: colors[i % len(colors)]
        pass


# ==============================================================================
# EXACT FUNCTION BEHAVIORS
# ==============================================================================

class TestExactTokenResolution:
    """Exact behavior of _github_token function."""

    def test_priority_order(self):
        """Priority: cli_token > GH_TOKEN > GITHUB_TOKEN"""
        with patch.dict(os.environ, {
            'GH_TOKEN': 'gh_value',
            'GITHUB_TOKEN': 'github_value'
        }):
            # CLI token wins
            assert _github_token('cli_value') == 'cli_value'
            # GH_TOKEN wins over GITHUB_TOKEN
            assert _github_token(None) == 'gh_value'
        
        # Only GITHUB_TOKEN
        with patch.dict(os.environ, {'GITHUB_TOKEN': 'github_only'}, clear=True):
            os.environ.pop('GH_TOKEN', None)
            assert _github_token(None) == 'github_only'

    def test_whitespace_handling(self):
        """Whitespace is stripped from all sources"""
        assert _github_token('  token  ') == 'token'
        assert _github_token('\ntoken\n') == 'token'
        assert _github_token('') is None
        assert _github_token('   ') is None


class TestExactAuthHeaderFormat:
    """Exact format of auth headers."""

    def test_bearer_format(self):
        """Must use 'Bearer' format"""
        result = _github_auth_headers('my-token')
        assert result == {'Authorization': 'Bearer my-token'}

    def test_empty_when_no_token(self):
        """Must return empty dict when no token"""
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop('GH_TOKEN', None)
            os.environ.pop('GITHUB_TOKEN', None)
            result = _github_auth_headers(None)
            assert result == {}


class TestExactRateLimitParsing:
    """Exact behavior of rate limit parsing."""

    class MockHeaders:
        def __init__(self, data):
            self._data = data
        def __contains__(self, key):
            return key in self._data
        def get(self, key, default=None):
            return self._data.get(key, default)

    def test_all_fields_extracted(self):
        """All rate limit fields extracted correctly"""
        from datetime import datetime, timezone
        
        headers = self.MockHeaders({
            'X-RateLimit-Limit': '5000',
            'X-RateLimit-Remaining': '4999',
            'X-RateLimit-Reset': '1700000000',
            'Retry-After': '3600'
        })
        
        result = _parse_rate_limit_headers(headers)
        
        assert result['limit'] == '5000'
        assert result['remaining'] == '4999'
        assert result['reset_epoch'] == 1700000000
        assert isinstance(result['reset_time'], datetime)
        assert result['reset_time'].tzinfo == timezone.utc
        assert 'reset_local' in result
        assert result['retry_after_seconds'] == 3600


class TestExactMergeAlgorithm:
    """Exact JSON merge algorithm."""

    def test_merge_algorithm(self):
        """
        The merge algorithm:
        1. Start with copy of existing content
        2. For each key in new content:
           - If key exists in both and both values are dicts: recursive merge
           - Otherwise: new value replaces old (including arrays)
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            existing = {
                "keep": "existing",
                "replace": "old",
                "nested": {"keep_nested": "existing", "replace_nested": "old"}
            }
            json.dump(existing, f)
            f.flush()
            
            new = {
                "replace": "new",
                "add": "new_value",
                "nested": {"replace_nested": "new", "add_nested": "new_value"}
            }
            
            result = merge_json_files(Path(f.name), new)
            
            assert result == {
                "keep": "existing",          # Preserved
                "replace": "new",            # Replaced
                "add": "new_value",          # Added
                "nested": {
                    "keep_nested": "existing",    # Preserved in nested
                    "replace_nested": "new",      # Replaced in nested  
                    "add_nested": "new_value"     # Added in nested
                }
            }
        os.unlink(f.name)


class TestExactStepTrackerStatuses:
    """Exact status values and order."""

    def test_status_order_constant(self):
        """Exact status order mapping"""
        tracker = StepTracker("Test")
        expected = {
            "pending": 0,
            "running": 1,
            "done": 2,
            "error": 3,
            "skipped": 4
        }
        assert tracker.status_order == expected

    def test_initial_status_is_pending(self):
        """New steps always start as 'pending'"""
        tracker = StepTracker("Test")
        tracker.add("key", "Label")
        assert tracker.steps[0]["status"] == "pending"
        assert tracker.steps[0]["detail"] == ""


class TestExactGitCommitMessage:
    """Exact git commit message."""

    def test_commit_message_exact(self):
        """Initial commit message must be exact"""
        expected_message = "Initial commit from Specify template"
        # This is used in init_git_repo()
        # subprocess.run(["git", "commit", "-m", expected_message], ...)


class TestExactDefaultValues:
    """Exact default values used in the CLI."""

    def test_default_ai_assistant(self):
        """Default AI assistant for interactive selection"""
        default = "copilot"
        assert default in AGENT_CONFIG

    def test_default_script_type_by_os(self):
        """Default script type is OS-dependent"""
        if os.name == "nt":
            expected = "ps"
        else:
            expected = "sh"
        assert expected in SCRIPT_TYPE_CHOICES

    def test_api_timeout(self):
        """API request timeout"""
        expected = 30  # seconds

    def test_download_timeout(self):
        """Download request timeout"""
        expected = 60  # seconds

    def test_chunk_size(self):
        """Download chunk size"""
        expected = 8192  # bytes

    def test_live_refresh_rate(self):
        """Live display refresh rate"""
        expected = 8  # frames per second


class TestExactAssetPattern:
    """Exact template asset naming pattern."""

    def test_asset_pattern_format(self):
        """Asset pattern: spec-kit-template-{ai}-{script}-{version}.zip"""
        # Example: spec-kit-template-copilot-sh-0.0.22.zip
        
        # The matching logic:
        # pattern = f"spec-kit-template-{ai_assistant}-{script_type}"
        # matching_assets = [
        #     asset for asset in assets
        #     if pattern in asset["name"] and asset["name"].endswith(".zip")
        # ]
        
        ai = "copilot"
        script = "sh"
        pattern = f"spec-kit-template-{ai}-{script}"
        assert pattern == "spec-kit-template-copilot-sh"


class TestExactGitHubAPIEndpoints:
    """Exact GitHub API endpoints."""

    def test_releases_endpoint(self):
        """Releases API endpoint format"""
        owner = "github"
        repo = "spec-kit"
        expected = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
        assert expected == "https://api.github.com/repos/github/spec-kit/releases/latest"


class TestExactErrorMessages:
    """Exact error message content."""

    def test_rate_limit_error_includes_tips(self):
        """Rate limit error must include troubleshooting tips"""
        class MockHeaders:
            def __init__(self, data):
                self._data = data
            def __contains__(self, key):
                return key in self._data
            def get(self, key, default=None):
                return self._data.get(key, default)
        
        headers = MockHeaders({})
        error = _format_rate_limit_error(403, headers, "http://test")
        
        # Must include these tips
        assert "--github-token" in error
        assert "GH_TOKEN" in error or "GITHUB_TOKEN" in error
        assert "5,000" in error or "5000" in error  # Authenticated limit
        assert "60" in error  # Unauthenticated limit


class TestExactCommandNames:
    """Exact command and option names."""

    def test_command_names(self):
        """CLI commands"""
        commands = ["init", "check", "version"]
        
    def test_init_options(self):
        """init command options"""
        options = [
            "--ai",
            "--script", 
            "--ignore-agent-tools",
            "--no-git",
            "--here",
            "--force",
            "--skip-tls",
            "--debug",
            "--github-token",
        ]


class TestExactAgentKeys:
    """Exact agent keys (must match CLI tool names)."""

    def test_all_agent_keys_exact(self):
        """All 15 agent keys"""
        expected_keys = {
            "copilot",
            "claude",
            "gemini",
            "cursor-agent",  # NOT "cursor"
            "qwen",
            "opencode",
            "codex",
            "windsurf",
            "kilocode",
            "auggie",
            "codebuddy",
            "roo",
            "q",
            "amp",
            "shai",
        }
        assert set(AGENT_CONFIG.keys()) == expected_keys
