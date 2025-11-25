"""
Acceptance Tests: Tool Detection
=================================

BEHAVIOR: check_tool() detects if CLI tools are installed.
Uses shutil.which() with special handling for Claude CLI.
"""

import shutil
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
from specify_cli import check_tool, CLAUDE_LOCAL_PATH, AGENT_CONFIG


class TestCheckToolBasicBehavior:
    """BEHAVIOR: check_tool() uses shutil.which() for detection."""

    def test_returns_boolean(self):
        """MUST return True or False."""
        result = check_tool("nonexistent_tool_xyz")
        assert isinstance(result, bool)

    def test_nonexistent_tool_returns_false(self):
        """Nonexistent tool returns False."""
        result = check_tool("this_tool_definitely_does_not_exist_12345")
        assert result is False

    def test_existing_tool_returns_true(self):
        """Existing tool (like git) returns True."""
        # Git is almost always available
        if shutil.which("git"):
            result = check_tool("git")
            assert result is True

    def test_uses_shutil_which_internally(self):
        """Uses shutil.which() for non-Claude tools."""
        with patch('specify_cli.shutil.which', return_value='/usr/bin/git') as mock:
            check_tool("git")
            mock.assert_called_with("git")


class TestClaudeSpecialHandling:
    """BEHAVIOR: Claude CLI has special path handling."""

    def test_claude_checks_local_path_first(self):
        """Claude checks ~/.claude/local/claude before PATH."""
        with patch('specify_cli.CLAUDE_LOCAL_PATH') as mock_path:
            mock_path.exists.return_value = True
            mock_path.is_file.return_value = True
            with patch('specify_cli.shutil.which', return_value=None):
                result = check_tool("claude")
                assert result is True

    def test_claude_falls_back_to_path(self):
        """Claude checks PATH if local path doesn't exist."""
        with patch('specify_cli.CLAUDE_LOCAL_PATH') as mock_path:
            mock_path.exists.return_value = False
            with patch('specify_cli.shutil.which', return_value='/usr/bin/claude'):
                result = check_tool("claude")
                assert result is True

    def test_claude_local_path_must_be_file(self):
        """Claude local path must be a file, not directory."""
        with patch('specify_cli.CLAUDE_LOCAL_PATH') as mock_path:
            mock_path.exists.return_value = True
            mock_path.is_file.return_value = False  # It's a directory
            with patch('specify_cli.shutil.which', return_value=None):
                result = check_tool("claude")
                assert result is False

    def test_claude_local_path_exact_location(self):
        """CLAUDE_LOCAL_PATH is ~/.claude/local/claude."""
        expected = Path.home() / ".claude" / "local" / "claude"
        assert CLAUDE_LOCAL_PATH == expected


class TestCheckToolWithTracker:
    """BEHAVIOR: check_tool() updates StepTracker when provided."""

    def test_tracker_complete_when_found(self):
        """Tracker.complete() called when tool found."""
        tracker = MagicMock()
        with patch('specify_cli.shutil.which', return_value='/usr/bin/git'):
            check_tool("git", tracker=tracker)
            tracker.complete.assert_called_once_with("git", "available")

    def test_tracker_error_when_not_found(self):
        """Tracker.error() called when tool not found."""
        tracker = MagicMock()
        with patch('specify_cli.shutil.which', return_value=None):
            check_tool("nonexistent", tracker=tracker)
            tracker.error.assert_called_once_with("nonexistent", "not found")

    def test_no_tracker_doesnt_crash(self):
        """Works fine without tracker parameter."""
        with patch('specify_cli.shutil.which', return_value=None):
            result = check_tool("nonexistent")
            assert result is False


class TestOtherToolsNoSpecialHandling:
    """BEHAVIOR: Non-Claude tools use standard shutil.which()."""

    def test_gemini_uses_standard_check(self):
        """Gemini uses standard shutil.which()."""
        with patch('specify_cli.shutil.which', return_value=None) as mock:
            check_tool("gemini")
            mock.assert_called_with("gemini")

    def test_copilot_uses_standard_check(self):
        """Copilot uses standard shutil.which()."""
        with patch('specify_cli.shutil.which', return_value=None) as mock:
            check_tool("copilot")
            mock.assert_called_with("copilot")

    def test_qwen_uses_standard_check(self):
        """Qwen uses standard shutil.which()."""
        with patch('specify_cli.shutil.which', return_value=None) as mock:
            check_tool("qwen")
            mock.assert_called_with("qwen")


class TestAllAgentToolChecks:
    """BEHAVIOR: All CLI agents can be checked."""

    def test_all_cli_agents_checkable(self):
        """All CLI-required agents can be checked without error."""
        cli_agents = [
            agent for agent, config in AGENT_CONFIG.items()
            if config["requires_cli"]
        ]
        
        for agent in cli_agents:
            with patch('specify_cli.shutil.which', return_value=None):
                if agent == "claude":
                    with patch('specify_cli.CLAUDE_LOCAL_PATH') as mock_path:
                        mock_path.exists.return_value = False
                        result = check_tool(agent)
                else:
                    result = check_tool(agent)
                assert isinstance(result, bool)


class TestVSCodeToolChecks:
    """BEHAVIOR: VS Code variants can be checked."""

    def test_code_tool_checkable(self):
        """'code' (VS Code) can be checked."""
        with patch('specify_cli.shutil.which', return_value=None):
            result = check_tool("code")
            assert isinstance(result, bool)

    def test_code_insiders_tool_checkable(self):
        """'code-insiders' can be checked."""
        with patch('specify_cli.shutil.which', return_value=None):
            result = check_tool("code-insiders")
            assert isinstance(result, bool)
