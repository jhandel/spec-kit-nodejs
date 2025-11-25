"""
Acceptance Tests: Claude Local Path
====================================

BEHAVIOR: Claude CLI has special path handling after `claude migrate-installer`.
The migrate-installer command REMOVES the original executable from PATH
and creates an alias at ~/.claude/local/claude instead.
This path should be prioritized over other claude executables in PATH.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
from specify_cli import CLAUDE_LOCAL_PATH


class TestClaudeLocalPathExact:
    """BEHAVIOR: CLAUDE_LOCAL_PATH is exactly ~/.claude/local/claude."""

    def test_is_pathlib_path_object(self):
        """MUST be a pathlib.Path object, not a string."""
        assert isinstance(CLAUDE_LOCAL_PATH, Path)

    def test_exact_path_structure(self):
        """MUST be exactly: <home>/.claude/local/claude."""
        expected = Path.home() / ".claude" / "local" / "claude"
        assert CLAUDE_LOCAL_PATH == expected

    def test_path_is_absolute(self):
        """MUST be an absolute path."""
        assert CLAUDE_LOCAL_PATH.is_absolute()

    def test_path_parts_order(self):
        """Path parts MUST be in order: home, .claude, local, claude."""
        parts = CLAUDE_LOCAL_PATH.parts
        # Find index of .claude
        claude_idx = None
        for i, part in enumerate(parts):
            if part == ".claude":
                claude_idx = i
                break
        
        assert claude_idx is not None, ".claude not found in path"
        assert parts[claude_idx] == ".claude"
        assert parts[claude_idx + 1] == "local"
        assert parts[claude_idx + 2] == "claude"

    def test_uses_pathlib_home(self):
        """MUST use Path.home() as base, not hardcoded path."""
        home = Path.home()
        assert str(CLAUDE_LOCAL_PATH).startswith(str(home))
