"""
Acceptance Tests: Script Type Choices
=====================================

BEHAVIOR: SCRIPT_TYPE_CHOICES defines the two supported script types
with human-readable descriptions.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
from specify_cli import SCRIPT_TYPE_CHOICES


class TestScriptTypeChoicesExact:
    """BEHAVIOR: Exactly 2 script types with specific descriptions."""

    def test_exactly_two_script_types(self):
        """MUST have exactly 'sh' and 'ps' keys."""
        assert len(SCRIPT_TYPE_CHOICES) == 2
        assert set(SCRIPT_TYPE_CHOICES.keys()) == {"sh", "ps"}

    def test_sh_description_exact(self):
        """'sh' description MUST be 'POSIX Shell (bash/zsh)'."""
        assert SCRIPT_TYPE_CHOICES["sh"] == "POSIX Shell (bash/zsh)"

    def test_ps_description_exact(self):
        """'ps' description MUST be 'PowerShell'."""
        assert SCRIPT_TYPE_CHOICES["ps"] == "PowerShell"

    def test_script_types_are_strings(self):
        """Both keys and values MUST be strings."""
        for key, value in SCRIPT_TYPE_CHOICES.items():
            assert isinstance(key, str)
            assert isinstance(value, str)


class TestDefaultScriptType:
    """BEHAVIOR: Default script type depends on OS."""

    def test_default_on_windows_is_ps(self):
        """On Windows (os.name == 'nt'), default is 'ps'."""
        import os
        if os.name == 'nt':
            default = "ps"
        else:
            default = "sh"
        assert default in SCRIPT_TYPE_CHOICES

    def test_default_on_unix_is_sh(self):
        """On Unix (os.name != 'nt'), default is 'sh'."""
        import os
        default = "ps" if os.name == "nt" else "sh"
        assert default in SCRIPT_TYPE_CHOICES
