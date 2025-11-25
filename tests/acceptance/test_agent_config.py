"""
Acceptance Tests: AGENT_CONFIG Data Structure
==============================================

BEHAVIOR: AGENT_CONFIG is the single source of truth for all supported AI agents.
Each agent entry contains exactly 4 fields with specific values.

The dictionary KEY must match the actual CLI executable name (not a shorthand).
This eliminates the need for special-case mappings throughout the codebase.
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
from specify_cli import AGENT_CONFIG


class TestAgentConfigStructure:
    """BEHAVIOR: AGENT_CONFIG has exactly 15 agents with consistent structure."""

    def test_agent_count_is_exactly_15(self):
        """MUST have exactly 15 agents."""
        assert len(AGENT_CONFIG) == 15

    def test_agent_keys_are_all_lowercase_strings(self):
        """MUST use lowercase string keys matching CLI tool names."""
        for key in AGENT_CONFIG.keys():
            assert isinstance(key, str)
            assert key == key.lower()

    def test_each_agent_has_exactly_4_fields(self):
        """MUST have exactly: name, folder, install_url, requires_cli."""
        required_fields = {"name", "folder", "install_url", "requires_cli"}
        for agent_key, config in AGENT_CONFIG.items():
            assert set(config.keys()) == required_fields, f"{agent_key} missing fields"


class TestAgentConfigExactValues:
    """BEHAVIOR: Each agent has specific exact values that MUST be preserved."""

    def test_copilot_exact_values(self):
        """GitHub Copilot - IDE-based, no CLI."""
        assert AGENT_CONFIG["copilot"] == {
            "name": "GitHub Copilot",
            "folder": ".github/",
            "install_url": None,
            "requires_cli": False,
        }

    def test_claude_exact_values(self):
        """Claude Code - CLI required."""
        assert AGENT_CONFIG["claude"] == {
            "name": "Claude Code",
            "folder": ".claude/",
            "install_url": "https://docs.anthropic.com/en/docs/claude-code/setup",
            "requires_cli": True,
        }

    def test_gemini_exact_values(self):
        """Gemini CLI - CLI required."""
        assert AGENT_CONFIG["gemini"] == {
            "name": "Gemini CLI",
            "folder": ".gemini/",
            "install_url": "https://github.com/google-gemini/gemini-cli",
            "requires_cli": True,
        }

    def test_cursor_agent_exact_values(self):
        """Cursor - IDE-based (key is 'cursor-agent' not 'cursor')."""
        assert AGENT_CONFIG["cursor-agent"] == {
            "name": "Cursor",
            "folder": ".cursor/",
            "install_url": None,
            "requires_cli": False,
        }

    def test_qwen_exact_values(self):
        """Qwen Code - CLI required."""
        assert AGENT_CONFIG["qwen"] == {
            "name": "Qwen Code",
            "folder": ".qwen/",
            "install_url": "https://github.com/QwenLM/qwen-code",
            "requires_cli": True,
        }

    def test_opencode_exact_values(self):
        """opencode - CLI required."""
        assert AGENT_CONFIG["opencode"] == {
            "name": "opencode",
            "folder": ".opencode/",
            "install_url": "https://opencode.ai",
            "requires_cli": True,
        }

    def test_codex_exact_values(self):
        """Codex CLI - CLI required."""
        assert AGENT_CONFIG["codex"] == {
            "name": "Codex CLI",
            "folder": ".codex/",
            "install_url": "https://github.com/openai/codex",
            "requires_cli": True,
        }

    def test_windsurf_exact_values(self):
        """Windsurf - IDE-based."""
        assert AGENT_CONFIG["windsurf"] == {
            "name": "Windsurf",
            "folder": ".windsurf/",
            "install_url": None,
            "requires_cli": False,
        }

    def test_kilocode_exact_values(self):
        """Kilo Code - IDE-based."""
        assert AGENT_CONFIG["kilocode"] == {
            "name": "Kilo Code",
            "folder": ".kilocode/",
            "install_url": None,
            "requires_cli": False,
        }

    def test_auggie_exact_values(self):
        """Auggie CLI - CLI required, folder is .augment/ not .auggie/."""
        assert AGENT_CONFIG["auggie"] == {
            "name": "Auggie CLI",
            "folder": ".augment/",
            "install_url": "https://docs.augmentcode.com/cli/setup-auggie/install-auggie-cli",
            "requires_cli": True,
        }

    def test_codebuddy_exact_values(self):
        """CodeBuddy - CLI required."""
        assert AGENT_CONFIG["codebuddy"] == {
            "name": "CodeBuddy",
            "folder": ".codebuddy/",
            "install_url": "https://www.codebuddy.ai/cli",
            "requires_cli": True,
        }

    def test_roo_exact_values(self):
        """Roo Code - IDE-based."""
        assert AGENT_CONFIG["roo"] == {
            "name": "Roo Code",
            "folder": ".roo/",
            "install_url": None,
            "requires_cli": False,
        }

    def test_q_exact_values(self):
        """Amazon Q Developer CLI - CLI required, folder is .amazonq/."""
        assert AGENT_CONFIG["q"] == {
            "name": "Amazon Q Developer CLI",
            "folder": ".amazonq/",
            "install_url": "https://aws.amazon.com/developer/learning/q-developer-cli/",
            "requires_cli": True,
        }

    def test_amp_exact_values(self):
        """Amp - CLI required, folder is .agents/."""
        assert AGENT_CONFIG["amp"] == {
            "name": "Amp",
            "folder": ".agents/",
            "install_url": "https://ampcode.com/manual#install",
            "requires_cli": True,
        }

    def test_shai_exact_values(self):
        """SHAI - CLI required."""
        assert AGENT_CONFIG["shai"] == {
            "name": "SHAI",
            "folder": ".shai/",
            "install_url": "https://github.com/ovh/shai",
            "requires_cli": True,
        }


class TestAgentConfigFolderNamingMismatches:
    """BEHAVIOR: Some agent keys intentionally don't match folder names."""

    def test_auggie_folder_is_augment(self):
        """Key 'auggie' but folder is '.augment/'."""
        assert AGENT_CONFIG["auggie"]["folder"] == ".augment/"

    def test_q_folder_is_amazonq(self):
        """Key 'q' but folder is '.amazonq/'."""
        assert AGENT_CONFIG["q"]["folder"] == ".amazonq/"

    def test_amp_folder_is_agents(self):
        """Key 'amp' but folder is '.agents/'."""
        assert AGENT_CONFIG["amp"]["folder"] == ".agents/"

    def test_copilot_folder_is_github(self):
        """Key 'copilot' but folder is '.github/'."""
        assert AGENT_CONFIG["copilot"]["folder"] == ".github/"


class TestAgentConfigCategorization:
    """BEHAVIOR: Agents are categorized by requires_cli field."""

    def test_ide_based_agents_do_not_require_cli(self):
        """IDE-based agents have requires_cli=False and install_url=None."""
        ide_agents = ["copilot", "cursor-agent", "windsurf", "kilocode", "roo"]
        for agent in ide_agents:
            assert AGENT_CONFIG[agent]["requires_cli"] is False
            assert AGENT_CONFIG[agent]["install_url"] is None

    def test_cli_based_agents_require_cli(self):
        """CLI-based agents have requires_cli=True and install_url set."""
        cli_agents = [
            "claude", "gemini", "qwen", "opencode", "codex",
            "auggie", "codebuddy", "q", "amp", "shai"
        ]
        for agent in cli_agents:
            assert AGENT_CONFIG[agent]["requires_cli"] is True
            assert AGENT_CONFIG[agent]["install_url"] is not None
            assert AGENT_CONFIG[agent]["install_url"].startswith("http")


class TestAgentConfigFolderFormat:
    """BEHAVIOR: All folders end with / and start with ."""

    def test_all_folders_start_with_dot(self):
        """All agent folders start with '.'."""
        for agent_key, config in AGENT_CONFIG.items():
            folder = config["folder"]
            assert folder.startswith("."), f"{agent_key} folder doesn't start with ."

    def test_all_folders_end_with_slash(self):
        """All agent folders end with '/'."""
        for agent_key, config in AGENT_CONFIG.items():
            folder = config["folder"]
            assert folder.endswith("/"), f"{agent_key} folder doesn't end with /"

    def test_all_folders_are_unique(self):
        """All agent folders are unique."""
        folders = [config["folder"] for config in AGENT_CONFIG.values()]
        assert len(folders) == len(set(folders)), "Duplicate folders found"


class TestAgentConfigCompleteList:
    """BEHAVIOR: Complete list of all supported agent keys."""

    def test_all_agent_keys_present(self):
        """All 15 agent keys must be present."""
        expected_keys = {
            "copilot",
            "claude",
            "gemini",
            "cursor-agent",
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
        actual_keys = set(AGENT_CONFIG.keys())
        assert actual_keys == expected_keys
        assert len(actual_keys) == 15
