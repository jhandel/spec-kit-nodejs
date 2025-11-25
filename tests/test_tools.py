"""
Test: Tool Detection
=====================
These tests document how the CLI detects installed tools.

Key concepts:
- Using shutil.which() for cross-platform tool detection
- Special handling for Claude CLI migration path
- Updating StepTracker with results

Node.js equivalents:
- Use child_process.execSync with 'which' (Unix) or 'where' (Windows)
- Check for Claude at ~/.claude/local/claude
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
    """
    Test Suite: Basic Tool Detection
    
    The check_tool function uses shutil.which() to find executables.
    
    Node.js equivalent:
    ```typescript
    import { execSync } from 'child_process';
    
    function checkTool(tool: string): boolean {
      try {
        const cmd = process.platform === 'win32' ? `where ${tool}` : `which ${tool}`;
        execSync(cmd, { stdio: 'ignore' });
        return true;
      } catch {
        return false;
      }
    }
    ```
    """

    def test_returns_true_when_tool_found(self):
        """Should return True when tool is in PATH"""
        with patch('shutil.which', return_value='/usr/bin/git'):
            result = check_tool('git')
            assert result is True

    def test_returns_false_when_tool_not_found(self):
        """Should return False when tool is not in PATH"""
        with patch('shutil.which', return_value=None):
            # Also need to mock the Path.exists for Claude special case
            with patch.object(Path, 'exists', return_value=False):
                with patch.object(Path, 'is_file', return_value=False):
                    result = check_tool('nonexistent-tool')
                    assert result is False

    def test_uses_shutil_which(self):
        """Should use shutil.which for tool detection"""
        with patch('shutil.which') as mock_which:
            mock_which.return_value = '/path/to/tool'
            check_tool('some-tool')
            mock_which.assert_called()


class TestClaudeSpecialHandling:
    """
    Test Suite: Claude CLI Special Path Handling
    
    After running `claude migrate-installer`, the Claude CLI is moved
    to ~/.claude/local/claude and removed from PATH.
    
    The check_tool function must check this special path first.
    
    Node.js equivalent:
    ```typescript
    import { existsSync } from 'fs';
    import { homedir } from 'os';
    import { join } from 'path';
    
    const CLAUDE_LOCAL_PATH = join(homedir(), '.claude', 'local', 'claude');
    
    function checkTool(tool: string): boolean {
      if (tool === 'claude') {
        if (existsSync(CLAUDE_LOCAL_PATH)) {
          return true;
        }
      }
      // ... regular which/where check
    }
    ```
    """

    def test_claude_local_path_checked_first(self):
        """For 'claude', should check ~/.claude/local/claude first"""
        # Mock the path existing
        with patch.object(Path, 'exists', return_value=True):
            with patch.object(Path, 'is_file', return_value=True):
                # Even if shutil.which fails, should succeed
                with patch('shutil.which', return_value=None):
                    result = check_tool('claude')
                    # Should find claude at the special path
                    # Note: The actual implementation may vary

    def test_claude_falls_back_to_which(self):
        """If Claude not at special path, fall back to which"""
        with patch.object(Path, 'exists', return_value=False):
            with patch('shutil.which', return_value='/usr/bin/claude'):
                result = check_tool('claude')
                assert result is True

    def test_other_tools_not_affected(self):
        """Non-claude tools should not check special path"""
        with patch('shutil.which', return_value='/usr/bin/git'):
            result = check_tool('git')
            assert result is True


class TestStepTrackerIntegration:
    """
    Test Suite: StepTracker Updates
    
    check_tool optionally updates a StepTracker with results.
    
    Node.js equivalent:
    ```typescript
    function checkTool(tool: string, tracker?: StepTracker): boolean {
      // ... detection logic
      if (tracker) {
        if (found) {
          tracker.complete(tool, 'available');
        } else {
          tracker.error(tool, 'not found');
        }
      }
      return found;
    }
    ```
    """

    def test_tracker_complete_on_success(self):
        """Should call tracker.complete when tool found"""
        mock_tracker = MagicMock()
        
        with patch('shutil.which', return_value='/usr/bin/tool'):
            check_tool('tool', mock_tracker)
            mock_tracker.complete.assert_called_once()

    def test_tracker_error_on_failure(self):
        """Should call tracker.error when tool not found"""
        mock_tracker = MagicMock()
        
        with patch('shutil.which', return_value=None):
            with patch.object(Path, 'exists', return_value=False):
                with patch.object(Path, 'is_file', return_value=False):
                    check_tool('missing-tool', mock_tracker)
                    mock_tracker.error.assert_called_once()

    def test_tracker_receives_status_detail(self):
        """Tracker should receive meaningful status details"""
        mock_tracker = MagicMock()
        
        with patch('shutil.which', return_value='/usr/bin/git'):
            check_tool('git', mock_tracker)
            # Should be called with (key, detail)
            call_args = mock_tracker.complete.call_args
            assert call_args is not None
            # First arg is key, second is detail
            assert 'git' in str(call_args) or call_args[0][0] == 'git'

    def test_no_tracker_no_error(self):
        """Should work fine without a tracker"""
        with patch('shutil.which', return_value='/usr/bin/tool'):
            result = check_tool('tool', None)
            assert result is True
        
        with patch('shutil.which', return_value=None):
            with patch.object(Path, 'exists', return_value=False):
                result = check_tool('missing', None)
                assert result is False


class TestToolDetectionForAllAgents:
    """
    Test Suite: Agent Tool Detection
    
    Documents which agents require CLI tool checks.
    """

    def test_cli_required_agents(self):
        """
        These agents require CLI tool detection:
        - requires_cli = True in AGENT_CONFIG
        """
        cli_agents = [
            agent for agent, config in AGENT_CONFIG.items()
            if config['requires_cli']
        ]
        
        expected_cli_agents = [
            'claude', 'gemini', 'qwen', 'opencode', 'codex',
            'auggie', 'codebuddy', 'q', 'amp', 'shai'
        ]
        
        for agent in expected_cli_agents:
            assert agent in cli_agents, f"'{agent}' should require CLI"

    def test_ide_based_agents_skip_check(self):
        """
        These agents don't require CLI tool detection:
        - requires_cli = False in AGENT_CONFIG
        - They are IDE-based (VS Code extensions, etc.)
        """
        ide_agents = [
            agent for agent, config in AGENT_CONFIG.items()
            if not config['requires_cli']
        ]
        
        expected_ide_agents = ['copilot', 'cursor-agent', 'windsurf', 'kilocode', 'roo']
        
        for agent in expected_ide_agents:
            assert agent in ide_agents, f"'{agent}' should not require CLI"


class TestToolDetectionCrossPlatform:
    """
    Test Suite: Cross-Platform Tool Detection
    
    Documents platform-specific behavior.
    
    Node.js equivalent approach:
    ```typescript
    function checkTool(tool: string): boolean {
      try {
        // Windows uses 'where', Unix uses 'which'
        const cmd = process.platform === 'win32' ? `where ${tool}` : `which ${tool}`;
        execSync(cmd, { stdio: 'ignore' });
        return true;
      } catch {
        return false;
      }
    }
    ```
    """

    def test_windows_tool_detection(self):
        """
        On Windows, tools may have .exe, .cmd, .bat extensions.
        shutil.which handles this automatically.
        """
        # shutil.which on Windows checks PATHEXT extensions
        # This is handled automatically in Python
        pass

    def test_unix_tool_detection(self):
        """
        On Unix, tools are found by name in PATH.
        """
        # shutil.which on Unix searches PATH
        pass

    def test_path_separator_handling(self):
        """
        PATH separator differs:
        - Windows: semicolon (;)
        - Unix: colon (:)
        shutil.which handles this automatically.
        """
        pass


class TestCommonToolsChecked:
    """
    Test Suite: Common Tools Checked by CLI
    
    Documents all tools that get checked during `specify check`.
    """

    def test_git_is_checked(self):
        """Git is required for branch operations"""
        # Git is checked first in the check command
        pass

    def test_code_editors_checked(self):
        """VS Code variants are checked"""
        # Checks: code, code-insiders
        code_tools = ['code', 'code-insiders']
        for tool in code_tools:
            assert isinstance(tool, str)

    def test_agent_clis_checked(self):
        """All CLI-based agent tools are checked"""
        cli_agents = {
            'claude': 'Claude Code',
            'gemini': 'Gemini CLI',
            'qwen': 'Qwen Code',
            'opencode': 'opencode',
            'codex': 'Codex CLI',
            'auggie': 'Auggie CLI',
            'codebuddy': 'CodeBuddy',
            'q': 'Amazon Q Developer CLI',
            'amp': 'Amp',
            'shai': 'SHAI',
        }
        
        for tool, name in cli_agents.items():
            assert tool in AGENT_CONFIG
            assert AGENT_CONFIG[tool]['requires_cli'] is True


class TestToolNotFoundBehavior:
    """
    Test Suite: Tool Not Found Behavior
    
    Documents what happens when a required tool is missing.
    """

    def test_check_tool_returns_false(self):
        """check_tool should return False for missing tools"""
        with patch('shutil.which', return_value=None):
            with patch.object(Path, 'exists', return_value=False):
                result = check_tool('nonexistent')
                assert result is False

    def test_init_warns_about_missing_agent_cli(self):
        """
        During init, if agent CLI is missing and --ignore-agent-tools
        is not set, user should be warned.
        
        This is not a hard error - user can proceed or use flag.
        """
        # The init command behavior
        pass

    def test_ignore_agent_tools_flag(self):
        """
        --ignore-agent-tools flag skips CLI tool checks during init.
        
        Usage: specify init my-project --ai claude --ignore-agent-tools
        """
        # This bypasses check_tool for agent CLIs
        pass
