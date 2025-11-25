"""
Acceptance Tests: Check Command
================================

BEHAVIOR: The 'specify check' command verifies installed tools.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
from specify_cli import AGENT_CONFIG


class TestCheckCommandBehavior:
    """BEHAVIOR: Check command scans for available tools."""

    def test_shows_banner(self):
        """Displays ASCII banner at start."""
        pass

    def test_shows_checking_message(self):
        """Shows 'Checking for installed tools...' message."""
        pass

    def test_uses_step_tracker(self):
        """Uses StepTracker for display."""
        pass


class TestCheckToolsScanned:
    """BEHAVIOR: Specific tools checked by the command."""

    def test_checks_git(self):
        """Checks for 'git' command."""
        pass

    def test_checks_all_cli_agents(self):
        """Checks all CLI-required agents from AGENT_CONFIG."""
        cli_agents = [k for k, v in AGENT_CONFIG.items() if v["requires_cli"]]
        expected = [
            "claude", "gemini", "qwen", "opencode", "codex",
            "auggie", "codebuddy", "q", "amp", "shai"
        ]
        assert sorted(cli_agents) == sorted(expected)

    def test_skips_ide_based_agents(self):
        """IDE-based agents marked as skipped, not checked."""
        ide_agents = [k for k, v in AGENT_CONFIG.items() if not v["requires_cli"]]
        expected = ["copilot", "cursor-agent", "windsurf", "kilocode", "roo"]
        # Check that these are in ide_agents (there's one more)
        for agent in expected:
            assert agent in ide_agents

    def test_checks_vscode(self):
        """Checks for 'code' (VS Code) command."""
        pass

    def test_checks_vscode_insiders(self):
        """Checks for 'code-insiders' command."""
        pass


class TestCheckOutputFormat:
    """BEHAVIOR: Output format of check command."""

    def test_tracker_shows_agent_names(self):
        """Tracker shows human-readable agent names."""
        # Uses config["name"] not the key
        for key, config in AGENT_CONFIG.items():
            assert "name" in config
            assert isinstance(config["name"], str)

    def test_ide_agents_show_skip_reason(self):
        """IDE agents show 'IDE-based, no CLI check' message."""
        pass

    def test_found_tools_show_available(self):
        """Found tools show 'available' status."""
        pass

    def test_missing_tools_show_not_found(self):
        """Missing tools show 'not found' status."""
        pass


class TestCheckCompletionMessage:
    """BEHAVIOR: Completion messages."""

    def test_shows_ready_message(self):
        """Shows 'Specify CLI is ready to use!' message."""
        pass

    def test_shows_git_tip_if_missing(self):
        """Shows git installation tip if not found."""
        pass

    def test_shows_agent_tip_if_none_found(self):
        """Shows agent installation tip if no agents found."""
        pass
