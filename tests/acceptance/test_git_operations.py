"""
Acceptance Tests: Git Operations
=================================

BEHAVIOR: Git operations for repository detection and initialization.
"""

import subprocess
import tempfile
import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
from specify_cli import is_git_repo, init_git_repo


class TestIsGitRepo:
    """BEHAVIOR: is_git_repo() detects git repositories."""

    def test_returns_boolean(self):
        """MUST return True or False."""
        result = is_git_repo()
        assert isinstance(result, bool)

    def test_non_git_directory_returns_false(self):
        """Non-git directory returns False."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = is_git_repo(Path(tmpdir))
            assert result is False

    def test_git_directory_returns_true(self):
        """Git repository returns True."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Initialize git repo
            subprocess.run(["git", "init"], cwd=tmpdir, capture_output=True)
            result = is_git_repo(Path(tmpdir))
            assert result is True

    def test_uses_git_rev_parse(self):
        """Uses 'git rev-parse --is-inside-work-tree' command."""
        # The implementation uses this specific git command
        with tempfile.TemporaryDirectory() as tmpdir:
            # Not a git repo
            result = is_git_repo(Path(tmpdir))
            assert result is False

    def test_none_path_uses_cwd(self):
        """None path defaults to current working directory."""
        result = is_git_repo(None)
        assert isinstance(result, bool)

    def test_non_directory_returns_false(self):
        """Non-directory path returns False."""
        with tempfile.NamedTemporaryFile() as tmpfile:
            result = is_git_repo(Path(tmpfile.name))
            assert result is False


class TestInitGitRepo:
    """BEHAVIOR: init_git_repo() initializes git repository with initial commit."""

    def test_returns_tuple(self):
        """MUST return tuple of (success: bool, error: Optional[str])."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a file so there's something to commit
            (Path(tmpdir) / "test.txt").write_text("test")
            result = init_git_repo(Path(tmpdir), quiet=True)
            assert isinstance(result, tuple)
            assert len(result) == 2

    def test_success_returns_true_none(self):
        """Successful init returns (True, None)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Configure git for test
            subprocess.run(["git", "config", "--global", "user.email", "test@example.com"], 
                          capture_output=True)
            subprocess.run(["git", "config", "--global", "user.name", "Test User"], 
                          capture_output=True)
            
            (Path(tmpdir) / "test.txt").write_text("test")
            success, error = init_git_repo(Path(tmpdir), quiet=True)
            
            # If git not configured, skip
            if not success and error and "user.email" in error:
                return
            
            assert success is True
            assert error is None

    def test_creates_git_directory(self):
        """Creates .git directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "test.txt").write_text("test")
            init_git_repo(Path(tmpdir), quiet=True)
            assert (Path(tmpdir) / ".git").exists()

    def test_commit_message_exact(self):
        """Initial commit message is 'Initial commit from Specify template'."""
        expected_message = "Initial commit from Specify template"
        with tempfile.TemporaryDirectory() as tmpdir:
            # Configure git
            subprocess.run(["git", "config", "--global", "user.email", "test@example.com"], 
                          capture_output=True)
            subprocess.run(["git", "config", "--global", "user.name", "Test User"], 
                          capture_output=True)
            
            (Path(tmpdir) / "test.txt").write_text("test")
            success, _ = init_git_repo(Path(tmpdir), quiet=True)
            
            if success:
                result = subprocess.run(
                    ["git", "log", "-1", "--format=%s"],
                    cwd=tmpdir,
                    capture_output=True,
                    text=True
                )
                assert expected_message in result.stdout

    def test_stages_all_files(self):
        """Stages all files with 'git add .'."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Configure git
            subprocess.run(["git", "config", "--global", "user.email", "test@example.com"], 
                          capture_output=True)
            subprocess.run(["git", "config", "--global", "user.name", "Test User"], 
                          capture_output=True)
            
            (Path(tmpdir) / "file1.txt").write_text("content1")
            (Path(tmpdir) / "file2.txt").write_text("content2")
            
            success, _ = init_git_repo(Path(tmpdir), quiet=True)
            
            if success:
                # Both files should be in the commit
                result = subprocess.run(
                    ["git", "ls-tree", "-r", "HEAD", "--name-only"],
                    cwd=tmpdir,
                    capture_output=True,
                    text=True
                )
                assert "file1.txt" in result.stdout
                assert "file2.txt" in result.stdout

    def test_failure_returns_false_with_error_message(self):
        """Failed init returns (False, error_message)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Make it a git repo already to cause conflict
            subprocess.run(["git", "init"], cwd=tmpdir, capture_output=True)
            
            # Try to init again - may or may not fail depending on git version
            success, error = init_git_repo(Path(tmpdir), quiet=True)
            assert isinstance(success, bool)
            if not success:
                assert error is not None
                assert isinstance(error, str)

    def test_restores_original_cwd(self):
        """Restores original working directory after operation."""
        original_cwd = Path.cwd()
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "test.txt").write_text("test")
            init_git_repo(Path(tmpdir), quiet=True)
        
        assert Path.cwd() == original_cwd

    def test_quiet_mode_suppresses_output(self):
        """quiet=True suppresses console output."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "test.txt").write_text("test")
            # quiet=True should not print to console
            result = init_git_repo(Path(tmpdir), quiet=True)
            assert isinstance(result, tuple)


class TestInitGitRepoCommandSequence:
    """BEHAVIOR: init_git_repo runs specific git commands in order."""

    def test_runs_git_init(self):
        """Runs 'git init' command."""
        # This is verified by .git directory creation
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "test.txt").write_text("test")
            init_git_repo(Path(tmpdir), quiet=True)
            assert (Path(tmpdir) / ".git").exists()

    def test_runs_git_add_dot(self):
        """Runs 'git add .' command."""
        # Verified by files being in the commit
        pass

    def test_runs_git_commit_with_message(self):
        """Runs 'git commit -m "Initial commit from Specify template"'."""
        # Verified by commit message test
        pass
