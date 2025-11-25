"""
Acceptance Tests: Error Messages
=================================

BEHAVIOR: User-facing error messages with actionable guidance.
"""


class TestErrorMessageStructure:
    """BEHAVIOR: Error message structure and formatting."""

    def test_uses_rich_panel(self):
        """Errors displayed in Rich Panel."""
        pass

    def test_red_border_for_errors(self):
        """Error panels have red border."""
        pass

    def test_includes_error_prefix(self):
        """Messages include 'Error:' prefix."""
        pass


class TestDirectoryErrors:
    """BEHAVIOR: Directory-related error messages."""

    def test_existing_directory_message(self):
        """Error for existing directory includes path."""
        pass

    def test_suggests_here_flag(self):
        """Suggests using --here flag for existing directory."""
        pass

    def test_nonempty_directory_warning(self):
        """Warning for non-empty directory."""
        pass


class TestToolMissingErrors:
    """BEHAVIOR: Missing tool error messages."""

    def test_includes_tool_name(self):
        """Error includes the missing tool name."""
        pass

    def test_includes_install_url(self):
        """Error includes install URL from AGENT_CONFIG."""
        pass

    def test_suggests_ignore_flag(self):
        """Suggests --ignore-agent-tools flag."""
        pass


class TestGitHubAPIErrors:
    """BEHAVIOR: GitHub API error messages."""

    def test_rate_limit_detailed_message(self):
        """Rate limit error includes detailed information."""
        pass

    def test_includes_troubleshooting_tips(self):
        """Includes troubleshooting tips section."""
        pass

    def test_mentions_token_options(self):
        """Mentions --github-token and env var options."""
        pass

    def test_mentions_rate_limits(self):
        """Mentions authenticated vs unauthenticated limits."""
        pass


class TestAssetNotFoundErrors:
    """BEHAVIOR: Release asset not found errors."""

    def test_shows_requested_pattern(self):
        """Shows the asset pattern that was searched."""
        pass

    def test_shows_available_assets(self):
        """Shows list of available assets."""
        pass


class TestBranchValidationErrors:
    """BEHAVIOR: Branch validation error messages."""

    def test_shows_current_branch(self):
        """Shows current branch name."""
        pass

    def test_shows_expected_format(self):
        """Shows expected branch format (###-feature-name)."""
        pass


class TestFileNotFoundErrors:
    """BEHAVIOR: Missing file error messages."""

    def test_plan_not_found_message(self):
        """plan.md not found suggests /speckit.plan."""
        pass

    def test_tasks_not_found_message(self):
        """tasks.md not found suggests /speckit.tasks."""
        pass

    def test_spec_not_found_message(self):
        """spec.md not found suggests /speckit.specify."""
        pass
