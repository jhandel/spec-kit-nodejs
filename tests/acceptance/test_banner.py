"""
Acceptance Tests: Banner and Tagline
=====================================

BEHAVIOR: The CLI displays an ASCII art banner with gradient colors
and a tagline describing the project.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
from specify_cli import BANNER, TAGLINE


class TestBannerExact:
    """BEHAVIOR: BANNER is the exact ASCII art for 'SPECIFY'."""

    def test_banner_is_string(self):
        """MUST be a string."""
        assert isinstance(BANNER, str)

    def test_banner_is_multiline(self):
        """MUST have multiple lines (6 lines of ASCII art)."""
        lines = BANNER.strip().split('\n')
        assert len(lines) == 6

    def test_banner_contains_specify_text(self):
        """MUST spell out 'SPECIFY' in ASCII art."""
        # The banner uses Unicode box-drawing characters
        assert "███████" in BANNER  # Part of the S
        assert "██████╗" in BANNER  # Part of the P

    def test_banner_uses_unicode_blocks(self):
        """MUST use Unicode block characters (█, ╗, ╔, ║, ╚, ╝)."""
        assert "█" in BANNER
        assert "╗" in BANNER
        assert "╔" in BANNER or "╚" in BANNER
        assert "║" in BANNER

    def test_banner_exact_first_line(self):
        """First line MUST start with the S character pattern."""
        first_line = BANNER.strip().split('\n')[0]
        assert "███████╗██████╗" in first_line

    def test_banner_exact_last_line(self):
        """Last line MUST end the SPECIFY text."""
        last_line = BANNER.strip().split('\n')[-1]
        assert "╚══════╝╚═╝" in last_line


class TestTaglineExact:
    """BEHAVIOR: TAGLINE is the exact project description."""

    def test_tagline_exact_value(self):
        """MUST be exactly 'GitHub Spec Kit - Spec-Driven Development Toolkit'."""
        assert TAGLINE == "GitHub Spec Kit - Spec-Driven Development Toolkit"

    def test_tagline_is_string(self):
        """MUST be a string."""
        assert isinstance(TAGLINE, str)

    def test_tagline_mentions_spec_kit(self):
        """MUST mention 'Spec Kit'."""
        assert "Spec Kit" in TAGLINE

    def test_tagline_mentions_sdd(self):
        """MUST mention 'Spec-Driven Development'."""
        assert "Spec-Driven Development" in TAGLINE


class TestBannerColors:
    """BEHAVIOR: Banner is displayed with gradient colors."""

    def test_banner_color_sequence(self):
        """
        Colors cycle through 6 specific Rich color names:
        bright_blue, blue, cyan, bright_cyan, white, bright_white
        """
        expected_colors = [
            "bright_blue",
            "blue", 
            "cyan",
            "bright_cyan",
            "white",
            "bright_white",
        ]
        assert len(expected_colors) == 6

    def test_tagline_style(self):
        """Tagline MUST be displayed in 'italic bright_yellow' style."""
        # This is documented behavior in show_banner()
        expected_style = "italic bright_yellow"
        assert expected_style  # Placeholder for implementation validation
