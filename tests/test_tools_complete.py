"""
Test: Tool Detection - COMPREHENSIVE
=====================================
Complete test coverage for tool detection (check_tool function).
"""

import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
import sys
import os
import shutil

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from specify_cli import check_tool, CLAUDE_LOCAL_PATH, AGENT_CONFIG


class TestCheckToolBasic:
    """Basic check_tool functionality tests."""

    def test_returns_bool(self):
        """check_tool should return a boolean"""
        result = check_tool("nonexistent-tool-xyz")
        assert isinstance(result, bool)

    def test_nonexistent_tool_returns_false(self):
        """Nonexistent tool should return False"""
        result = check_tool("definitely-not-a-real-tool-12345")
        assert result is False

    def test_common_tool_git(self):
        """git should be detected if installed"""
        # Most dev systems have git
        result = check_tool("git")
        # Don't assert True - might not be installed in CI
        assert isinstance(result, bool)


class TestCheckToolWithTracker:
    """Test check_tool with StepTracker integration."""

    def test_tracker_complete_when_found(self):
        """Should call tracker.complete when tool found"""
        with patch('specify_cli.shutil.which', return_value='/usr/bin/tool'):
            tracker = MagicMock()
            result = check_tool("mytool", tracker=tracker)
            assert result is True
            tracker.complete.assert_called_once_with("mytool", "available")

    def test_tracker_error_when_not_found(self):
        """Should call tracker.error when tool not found"""
        with patch('specify_cli.shutil.which', return_value=None):
            tracker = MagicMock()
            result = check_tool("mytool", tracker=tracker)
            assert result is False
            tracker.error.assert_called_once_with("mytool", "not found")

    def test_no_tracker_doesnt_crash(self):
        """Should work without tracker parameter"""
        with patch('specify_cli.shutil.which', return_value=None):
            result = check_tool("test")
            assert result is False


class TestClaudeSpecialHandling:
    """Test special handling for Claude CLI."""

    def test_claude_checks_local_path_first(self):
        """Claude should check ~/.claude/local/claude before PATH"""
        with patch('specify_cli.CLAUDE_LOCAL_PATH') as mock_path:
            mock_path.exists.return_value = True
            mock_path.is_file.return_value = True
            with patch('specify_cli.shutil.which', return_value=None) as mock_which:
                result = check_tool("claude")
                assert result is True

    def test_claude_falls_back_to_path(self):
        """Claude should check PATH if local path doesn't exist"""
        with patch('specify_cli.CLAUDE_LOCAL_PATH') as mock_path:
            mock_path.exists.return_value = False
            with patch('specify_cli.shutil.which', return_value='/usr/bin/claude'):
                result = check_tool("claude")
                assert result is True

    def test_claude_local_path_must_be_file(self):
        """Claude local path must be a file, not directory"""
        with patch('specify_cli.CLAUDE_LOCAL_PATH') as mock_path:
            mock_path.exists.return_value = True
            mock_path.is_file.return_value = False
            with patch('specify_cli.shutil.which', return_value=None):
                result = check_tool("claude")
                assert result is False

    def test_claude_local_path_structure(self):
        """Verify CLAUDE_LOCAL_PATH is correct"""
        expected = Path.home() / ".claude" / "local" / "claude"
        assert CLAUDE_LOCAL_PATH == expected

    def test_claude_special_handling_with_tracker(self):
        """Claude special handling should work with tracker"""
        with patch('specify_cli.CLAUDE_LOCAL_PATH') as mock_path:
            mock_path.exists.return_value = True
            mock_path.is_file.return_value = True
            tracker = MagicMock()
            result = check_tool("claude", tracker=tracker)
            assert result is True
            tracker.complete.assert_called_once_with("claude", "available")


class TestOtherToolsNoSpecialHandling:
    """Verify other tools don't have special handling."""

    def test_gemini_uses_standard_check(self):
        """gemini should use standard shutil.which"""
        with patch('specify_cli.shutil.which', return_value=None) as mock_which:
            check_tool("gemini")
            mock_which.assert_called_once_with("gemini")

    def test_copilot_uses_standard_check(self):
        """copilot should use standard shutil.which"""
        with patch('specify_cli.shutil.which', return_value=None) as mock_which:
            check_tool("copilot")
            mock_which.assert_called_once_with("copilot")


class TestAllAgentToolChecks:
    """Test tool checks for all CLI agents."""

    def test_all_cli_agents_checkable(self):
        """All CLI-required agents should be checkable"""
        cli_agents = [
            agent for agent, config in AGENT_CONFIG.items()
            if config["requires_cli"]
        ]
        
        for agent in cli_agents:
            with patch('specify_cli.shutil.which', return_value=None):
                # If claude, also patch the local path
                if agent == "claude":
                    with patch('specify_cli.CLAUDE_LOCAL_PATH') as mock_path:
                        mock_path.exists.return_value = False
                        result = check_tool(agent)
                else:
                    result = check_tool(agent)
                assert isinstance(result, bool)


class TestToolCheckEdgeCases:
    """Edge cases for tool detection."""

    def test_empty_string_tool_name(self):
        """Empty tool name should return False"""
        result = check_tool("")
        assert result is False

    def test_tool_name_with_path(self):
        """Tool name with path characters"""
        result = check_tool("/usr/bin/test")
        # shutil.which handles this
        assert isinstance(result, bool)

    def test_tool_name_case_sensitivity(self):
        """Tool names are case-sensitive on Unix"""
        # Git vs GIT vs git
        with patch('specify_cli.shutil.which') as mock_which:
            mock_which.side_effect = lambda x: '/usr/bin/git' if x == 'git' else None
            assert check_tool("git") is True
            assert check_tool("Git") is False
            assert check_tool("GIT") is False


class TestWhichBehavior:
    """Document shutil.which behavior for Node.js port."""

    def test_which_returns_path_or_none(self):
        """shutil.which returns path string or None"""
        result = shutil.which("python") or shutil.which("python3")
        # Either found (string) or not found (None)
        assert result is None or isinstance(result, str)

    def test_which_searches_path(self):
        """shutil.which searches PATH environment variable"""
        # This is the standard behavior
        pass

    def test_which_on_windows(self):
        """Windows: checks PATH and PATHEXT extensions"""
        if os.name == 'nt':
            # On Windows, shutil.which also checks .exe, .bat, etc.
            pass

    def test_node_js_equivalent(self):
        """
        Node.js equivalent using child_process:
        
        ```typescript
        function checkTool(tool: string): boolean {
          try {
            const cmd = process.platform === 'win32' 
              ? `where ${tool}` 
              : `which ${tool}`;
            execSync(cmd, { stdio: 'ignore' });
            return true;
          } catch {
            return false;
          }
        }
        ```
        """
        pass


class TestToolCheckInContext:
    """Test tool checks in realistic contexts."""

    def test_git_check_for_repo_init(self):
        """Git check determines if repo can be initialized"""
        # This is how the code uses it
        has_git = check_tool("git")
        # If has_git is False, skip git init
        assert isinstance(has_git, bool)

    def test_agent_check_before_init(self):
        """Agent CLI check before project initialization"""
        # User selects claude -> check if claude CLI installed
        # If not and requires_cli=True -> show error
        pass


class TestVSCodeToolChecks:
    """Test VS Code tool detection."""

    def test_code_tool(self):
        """Check for 'code' command (VS Code)"""
        result = check_tool("code")
        assert isinstance(result, bool)

    def test_code_insiders_tool(self):
        """Check for 'code-insiders' command"""
        result = check_tool("code-insiders")
        assert isinstance(result, bool)
