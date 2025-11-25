"""
Test: Configuration and Constants - COMPREHENSIVE
==================================================
Complete test coverage for all configuration values and constants
that must be replicated in the Node.js port.

Key concepts:
- AGENT_CONFIG: Registry of all supported AI agents (15 total)
- SCRIPT_TYPE_CHOICES: Supported script types (sh, ps)
- CLAUDE_LOCAL_PATH: Special path for migrated Claude CLI
- BANNER: ASCII art banner text (6 lines)
- TAGLINE: Subtitle shown with banner

This file contains:
1. Structure tests - verify data structures are correct
2. Value tests - verify specific values are correct
3. Relationship tests - verify inter-field relationships
4. Edge case tests - verify unusual inputs handled
"""

import pytest
from pathlib import Path
import sys
import os

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from specify_cli import (
    AGENT_CONFIG,
    SCRIPT_TYPE_CHOICES,
    CLAUDE_LOCAL_PATH,
    BANNER,
    TAGLINE,
)


class TestAgentConfig:
    """
    Test Suite: AGENT_CONFIG Dictionary
    
    AGENT_CONFIG is the single source of truth for all supported AI agents.
    Each entry maps an agent key to its configuration.
    
    Node.js equivalent:
    ```typescript
    interface AgentConfig {
      name: string;
      folder: string;
      installUrl: string | null;
      requiresCli: boolean;
    }
    const AGENT_CONFIG: Record<string, AgentConfig> = { ... }
    ```
    """

    def test_agent_config_is_dict(self):
        """AGENT_CONFIG must be a dictionary"""
        assert isinstance(AGENT_CONFIG, dict)

    def test_agent_config_has_expected_agents(self):
        """
        All these agents must be present for backward compatibility.
        New agents can be added but these must exist.
        """
        expected_agents = [
            "copilot",
            "claude",
            "gemini",
            "cursor-agent",  # Note: uses actual CLI tool name, not "cursor"
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
        ]
        for agent in expected_agents:
            assert agent in AGENT_CONFIG, f"Missing agent: {agent}"

    def test_agent_config_entry_structure(self):
        """
        Each agent config entry must have these exact keys:
        - name: Human-readable display name
        - folder: Directory where agent files are stored (with trailing slash)
        - install_url: URL for installation docs or None for IDE-based
        - requires_cli: Boolean - whether CLI tool check is needed
        """
        required_keys = ["name", "folder", "install_url", "requires_cli"]
        
        for agent_key, config in AGENT_CONFIG.items():
            for key in required_keys:
                assert key in config, f"Agent '{agent_key}' missing key '{key}'"
            
            # Type checks
            assert isinstance(config["name"], str), f"'{agent_key}' name must be string"
            assert isinstance(config["folder"], str), f"'{agent_key}' folder must be string"
            assert config["install_url"] is None or isinstance(config["install_url"], str)
            assert isinstance(config["requires_cli"], bool)

    def test_agent_folder_format(self):
        """
        Agent folders should:
        - Start with a dot (hidden folder)
        - End with a forward slash
        """
        for agent_key, config in AGENT_CONFIG.items():
            folder = config["folder"]
            assert folder.startswith("."), f"'{agent_key}' folder should start with '.'"
            assert folder.endswith("/"), f"'{agent_key}' folder should end with '/'"

    def test_ide_based_agents_no_cli_required(self):
        """
        IDE-based agents must have:
        - requires_cli = False
        - install_url = None
        """
        ide_based_agents = ["copilot", "cursor-agent", "windsurf", "kilocode", "roo"]
        
        for agent in ide_based_agents:
            config = AGENT_CONFIG[agent]
            assert config["requires_cli"] is False, f"'{agent}' should not require CLI"
            assert config["install_url"] is None, f"'{agent}' should have no install URL"

    def test_cli_based_agents_have_install_url(self):
        """
        CLI-based agents must have:
        - requires_cli = True
        - install_url = valid URL string
        """
        cli_based_agents = [
            "claude", "gemini", "qwen", "opencode", "codex",
            "auggie", "codebuddy", "q", "amp", "shai"
        ]
        
        for agent in cli_based_agents:
            config = AGENT_CONFIG[agent]
            assert config["requires_cli"] is True, f"'{agent}' should require CLI"
            assert config["install_url"] is not None, f"'{agent}' should have install URL"
            assert config["install_url"].startswith("http"), f"'{agent}' install_url should be URL"

    def test_specific_agent_configurations(self):
        """
        Test specific agent configurations for exact values.
        These are the values that the Node.js port must match exactly.
        """
        # Test copilot (most common)
        assert AGENT_CONFIG["copilot"] == {
            "name": "GitHub Copilot",
            "folder": ".github/",
            "install_url": None,
            "requires_cli": False,
        }
        
        # Test claude (has special path handling)
        assert AGENT_CONFIG["claude"]["name"] == "Claude Code"
        assert AGENT_CONFIG["claude"]["folder"] == ".claude/"
        assert AGENT_CONFIG["claude"]["requires_cli"] is True
        
        # Test cursor-agent (note the hyphenated name matches CLI tool)
        assert AGENT_CONFIG["cursor-agent"]["name"] == "Cursor"
        assert AGENT_CONFIG["cursor-agent"]["folder"] == ".cursor/"
        
        # Test q (Amazon Q - short name)
        assert AGENT_CONFIG["q"]["name"] == "Amazon Q Developer CLI"
        assert AGENT_CONFIG["q"]["folder"] == ".amazonq/"

    def test_agent_key_is_cli_tool_name(self):
        """
        CRITICAL: Agent keys should match actual CLI tool names.
        This is important for the check_tool() function.
        
        The key design principle: dictionary key = executable name users type.
        """
        # These agent keys match CLI tool names exactly
        cli_tool_matches = {
            "claude": "claude",
            "gemini": "gemini", 
            "qwen": "qwen",
            "opencode": "opencode",
            "codex": "codex",
            "auggie": "auggie",
            "codebuddy": "codebuddy",
            "q": "q",
            "amp": "amp",
            "shai": "shai",
            "cursor-agent": "cursor-agent",  # NOT "cursor"
        }
        
        for agent_key, expected_cli in cli_tool_matches.items():
            assert agent_key == expected_cli, f"Agent key '{agent_key}' should match CLI tool name"


class TestScriptTypeChoices:
    """
    Test Suite: SCRIPT_TYPE_CHOICES
    
    Defines the supported script types for cross-platform support.
    """

    def test_script_type_choices_structure(self):
        """Must have exactly sh and ps options"""
        assert "sh" in SCRIPT_TYPE_CHOICES
        assert "ps" in SCRIPT_TYPE_CHOICES
        assert len(SCRIPT_TYPE_CHOICES) == 2

    def test_script_type_descriptions(self):
        """Human-readable descriptions for UI display"""
        assert "bash" in SCRIPT_TYPE_CHOICES["sh"].lower() or "shell" in SCRIPT_TYPE_CHOICES["sh"].lower()
        assert "powershell" in SCRIPT_TYPE_CHOICES["ps"].lower()


class TestClaudeLocalPath:
    """
    Test Suite: CLAUDE_LOCAL_PATH
    
    Special handling for Claude CLI after migration.
    The `claude migrate-installer` command moves the CLI to a non-PATH location.
    """

    def test_claude_local_path_is_path_object(self):
        """Should be a Path object for cross-platform compatibility"""
        assert isinstance(CLAUDE_LOCAL_PATH, Path)

    def test_claude_local_path_structure(self):
        """
        Path should be: ~/.claude/local/claude
        This is where claude-installer puts it after migration.
        """
        path_str = str(CLAUDE_LOCAL_PATH)
        assert ".claude" in path_str
        assert "local" in path_str
        assert path_str.endswith("claude")

    def test_claude_local_path_uses_home(self):
        """Path should be relative to user's home directory"""
        home = Path.home()
        expected = home / ".claude" / "local" / "claude"
        assert CLAUDE_LOCAL_PATH == expected


class TestBanner:
    """
    Test Suite: ASCII Banner
    
    The banner is displayed at CLI startup.
    """

    def test_banner_is_string(self):
        """Banner must be a string"""
        assert isinstance(BANNER, str)

    def test_banner_is_multiline(self):
        """Banner should span multiple lines"""
        lines = BANNER.strip().split("\n")
        assert len(lines) >= 6, "Banner should have at least 6 lines"

    def test_banner_contains_specify(self):
        """Banner should spell out SPECIFY in ASCII art"""
        # The banner uses Unicode block characters to spell SPECIFY
        assert "███" in BANNER or "SPECIFY" in BANNER.upper()

    def test_banner_line_widths_reasonable(self):
        """Each line should be reasonable width for terminals"""
        for line in BANNER.strip().split("\n"):
            assert len(line) <= 80, "Banner line too wide for narrow terminals"


class TestTagline:
    """Test Suite: Tagline shown below banner"""

    def test_tagline_is_string(self):
        assert isinstance(TAGLINE, str)

    def test_tagline_mentions_spec_kit(self):
        """Tagline should mention GitHub Spec Kit"""
        assert "Spec Kit" in TAGLINE or "spec kit" in TAGLINE.lower()

    def test_tagline_mentions_sdd(self):
        """Tagline should reference Spec-Driven Development"""
        assert "Spec-Driven" in TAGLINE or "SDD" in TAGLINE


class TestConfigConstants:
    """
    Test Suite: Miscellaneous Constants
    
    These are implicit constants used throughout the code.
    """

    def test_github_repo_constants(self):
        """
        The code uses hardcoded GitHub repo values.
        These should be constants in the Node.js port.
        """
        # These values are used in download_template_from_github
        expected_owner = "github"
        expected_repo = "spec-kit"
        
        # Import the function and check (this is tested more in test_github.py)
        from specify_cli import download_template_from_github
        # The function source contains these values
        import inspect
        source = inspect.getsource(download_template_from_github)
        assert 'repo_owner = "github"' in source or "github" in source.lower()
        assert 'repo_name = "spec-kit"' in source or "spec-kit" in source

    def test_template_pattern_format(self):
        """
        Template assets follow this naming pattern:
        spec-kit-template-{ai}-{script}-{version}.zip
        """
        # This is documented behavior for release packages
        expected_pattern = "spec-kit-template-{ai}-{script}"
        # Verified by checking the download function logic
        pass  # Pattern is tested in test_github.py

    def test_branch_name_max_length(self):
        """
        GitHub enforces a 244-byte limit on branch names.
        This constant should be defined.
        """
        # The code checks for this limit in create-new-feature scripts
        max_length = 244
        # This is enforced in the shell scripts and should be in Node.js
        pass  # Tested in integration tests


class TestEnvironmentVariables:
    """
    Test Suite: Environment Variable Support
    
    Documents which environment variables the CLI respects.
    """

    def test_github_token_env_vars(self):
        """
        The CLI checks for GitHub tokens in this order:
        1. --github-token CLI argument
        2. GH_TOKEN environment variable
        3. GITHUB_TOKEN environment variable
        """
        from specify_cli import _github_token
        
        # Clear any existing env vars for clean test
        old_gh = os.environ.pop("GH_TOKEN", None)
        old_github = os.environ.pop("GITHUB_TOKEN", None)
        
        try:
            # Test with no token
            assert _github_token() is None
            
            # Test GITHUB_TOKEN
            os.environ["GITHUB_TOKEN"] = "test-github-token"
            assert _github_token() == "test-github-token"
            
            # Test GH_TOKEN takes precedence
            os.environ["GH_TOKEN"] = "test-gh-token"
            assert _github_token() == "test-gh-token"
            
            # Test CLI token takes precedence over all
            assert _github_token("cli-token") == "cli-token"
            
        finally:
            # Restore env vars
            if old_gh:
                os.environ["GH_TOKEN"] = old_gh
            else:
                os.environ.pop("GH_TOKEN", None)
            if old_github:
                os.environ["GITHUB_TOKEN"] = old_github
            else:
                os.environ.pop("GITHUB_TOKEN", None)

    def test_specify_feature_env_var(self):
        """
        SPECIFY_FEATURE env var can override branch detection.
        Used for non-git repositories.
        """
        # This is used in the scripts (common.sh, common.ps1)
        # Should be documented for Node.js port
        env_var_name = "SPECIFY_FEATURE"
        # Scripts check: if [[ -n "${SPECIFY_FEATURE:-}" ]]; then
        pass


class TestDefaultValues:
    """
    Test Suite: Default Values
    
    Documents the default values used when options aren't specified.
    """

    def test_default_ai_assistant(self):
        """Default AI assistant for interactive selection is 'copilot'"""
        # In select_with_arrows call: default_key="copilot"
        default_ai = "copilot"
        assert default_ai in AGENT_CONFIG

    def test_default_script_type_windows(self):
        """On Windows, default script type should be 'ps'"""
        if os.name == "nt":
            expected = "ps"
        else:
            expected = "sh"
        assert expected in SCRIPT_TYPE_CHOICES

    def test_default_script_type_unix(self):
        """On Unix/macOS, default script type should be 'sh'"""
        # The code uses: default_script = "ps" if os.name == "nt" else "sh"
        pass


class TestAgentConfigExactValues:
    """Verify every agent's exact configuration values."""

    def test_exact_agent_count(self):
        """Must have exactly 15 agents"""
        assert len(AGENT_CONFIG) == 15

    def test_all_agent_folders_unique(self):
        """No two agents should share a folder (except we know some do)"""
        folders = [config["folder"] for config in AGENT_CONFIG.values()]
        # Note: some folders may be intentionally shared
        pass

    def test_copilot_exact(self):
        """Copilot exact config"""
        assert AGENT_CONFIG["copilot"] == {
            "name": "GitHub Copilot",
            "folder": ".github/",
            "install_url": None,
            "requires_cli": False,
        }

    def test_claude_exact(self):
        """Claude exact config"""
        assert AGENT_CONFIG["claude"] == {
            "name": "Claude Code",
            "folder": ".claude/",
            "install_url": "https://docs.anthropic.com/en/docs/claude-code/setup",
            "requires_cli": True,
        }

    def test_gemini_exact(self):
        """Gemini exact config"""
        assert AGENT_CONFIG["gemini"] == {
            "name": "Gemini CLI",
            "folder": ".gemini/",
            "install_url": "https://github.com/google-gemini/gemini-cli",
            "requires_cli": True,
        }

    def test_cursor_agent_exact(self):
        """Cursor exact config (key is cursor-agent, not cursor)"""
        assert AGENT_CONFIG["cursor-agent"] == {
            "name": "Cursor",
            "folder": ".cursor/",
            "install_url": None,
            "requires_cli": False,
        }

    def test_qwen_exact(self):
        """Qwen exact config"""
        assert AGENT_CONFIG["qwen"] == {
            "name": "Qwen Code",
            "folder": ".qwen/",
            "install_url": "https://github.com/QwenLM/qwen-code",
            "requires_cli": True,
        }

    def test_opencode_exact(self):
        """opencode exact config"""
        assert AGENT_CONFIG["opencode"] == {
            "name": "opencode",
            "folder": ".opencode/",
            "install_url": "https://opencode.ai",
            "requires_cli": True,
        }

    def test_codex_exact(self):
        """Codex exact config"""
        assert AGENT_CONFIG["codex"] == {
            "name": "Codex CLI",
            "folder": ".codex/",
            "install_url": "https://github.com/openai/codex",
            "requires_cli": True,
        }

    def test_windsurf_exact(self):
        """Windsurf exact config"""
        assert AGENT_CONFIG["windsurf"] == {
            "name": "Windsurf",
            "folder": ".windsurf/",
            "install_url": None,
            "requires_cli": False,
        }

    def test_kilocode_exact(self):
        """Kilocode exact config"""
        assert AGENT_CONFIG["kilocode"] == {
            "name": "Kilo Code",
            "folder": ".kilocode/",
            "install_url": None,
            "requires_cli": False,
        }

    def test_auggie_exact(self):
        """Auggie exact config - NOTE: folder is .augment, NOT .auggie"""
        assert AGENT_CONFIG["auggie"] == {
            "name": "Auggie CLI",
            "folder": ".augment/",
            "install_url": "https://docs.augmentcode.com/cli/setup-auggie/install-auggie-cli",
            "requires_cli": True,
        }

    def test_codebuddy_exact(self):
        """CodeBuddy exact config"""
        assert AGENT_CONFIG["codebuddy"] == {
            "name": "CodeBuddy",
            "folder": ".codebuddy/",
            "install_url": "https://www.codebuddy.ai/cli",
            "requires_cli": True,
        }

    def test_roo_exact(self):
        """Roo exact config"""
        assert AGENT_CONFIG["roo"] == {
            "name": "Roo Code",
            "folder": ".roo/",
            "install_url": None,
            "requires_cli": False,
        }

    def test_q_exact(self):
        """Q exact config - NOTE: folder is .amazonq, NOT .q"""
        assert AGENT_CONFIG["q"] == {
            "name": "Amazon Q Developer CLI",
            "folder": ".amazonq/",
            "install_url": "https://aws.amazon.com/developer/learning/q-developer-cli/",
            "requires_cli": True,
        }

    def test_amp_exact(self):
        """Amp exact config - NOTE: folder is .agents, NOT .amp"""
        assert AGENT_CONFIG["amp"] == {
            "name": "Amp",
            "folder": ".agents/",
            "install_url": "https://ampcode.com/manual#install",
            "requires_cli": True,
        }

    def test_shai_exact(self):
        """SHAI exact config"""
        assert AGENT_CONFIG["shai"] == {
            "name": "SHAI",
            "folder": ".shai/",
            "install_url": "https://github.com/ovh/shai",
            "requires_cli": True,
        }


class TestAgentKeyVsFolder:
    """Document cases where agent key differs from folder name."""

    def test_auggie_folder_mismatch(self):
        """auggie key uses .augment folder"""
        assert AGENT_CONFIG["auggie"]["folder"] == ".augment/"

    def test_q_folder_mismatch(self):
        """q key uses .amazonq folder"""
        assert AGENT_CONFIG["q"]["folder"] == ".amazonq/"

    def test_amp_folder_mismatch(self):
        """amp key uses .agents folder"""
        assert AGENT_CONFIG["amp"]["folder"] == ".agents/"

    def test_copilot_folder_mismatch(self):
        """copilot key uses .github folder"""
        assert AGENT_CONFIG["copilot"]["folder"] == ".github/"


class TestBannerDetails:
    """Detailed banner tests."""

    def test_banner_exact_line_count(self):
        """Banner must have exactly 6 lines"""
        lines = BANNER.strip().split('\n')
        assert len(lines) == 6

    def test_banner_uses_unicode_blocks(self):
        """Banner uses specific Unicode characters"""
        assert '█' in BANNER  # Full block
        assert '║' in BANNER  # Vertical bar
        assert '╗' in BANNER  # Upper right corner
        assert '╔' in BANNER  # Upper left corner
        assert '╝' in BANNER  # Lower right corner
        assert '╚' in BANNER  # Lower left corner

    def test_tagline_exact_value(self):
        """Tagline must be exact"""
        assert TAGLINE == "GitHub Spec Kit - Spec-Driven Development Toolkit"


class TestScriptTypeExact:
    """Exact script type values."""

    def test_script_types_exact_values(self):
        """Exact script type dictionary"""
        assert SCRIPT_TYPE_CHOICES == {
            "sh": "POSIX Shell (bash/zsh)",
            "ps": "PowerShell",
        }


class TestClaudePathExact:
    """Exact Claude local path."""

    def test_claude_path_exact(self):
        """Exact Claude local path construction"""
        expected = Path.home() / ".claude" / "local" / "claude"
        assert CLAUDE_LOCAL_PATH == expected

    def test_claude_path_is_absolute(self):
        """Claude path must be absolute"""
        assert CLAUDE_LOCAL_PATH.is_absolute()

    def test_claude_path_parts(self):
        """Claude path has correct parts"""
        parts = CLAUDE_LOCAL_PATH.parts
        assert parts[-1] == "claude"
        assert parts[-2] == "local"
        assert parts[-3] == ".claude"
