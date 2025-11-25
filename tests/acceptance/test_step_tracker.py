"""
Acceptance Tests: StepTracker UI Component
==========================================

BEHAVIOR: StepTracker manages progress display with tree-style rendering.
Each step has a status: pending, running, done, error, skipped.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
from specify_cli import StepTracker


class TestStepTrackerInitialization:
    """BEHAVIOR: StepTracker initialization and structure."""

    def test_accepts_title_string(self):
        """Constructor accepts a title string."""
        tracker = StepTracker("My Title")
        assert tracker.title == "My Title"

    def test_steps_starts_empty(self):
        """Steps list is initially empty."""
        tracker = StepTracker("Test")
        assert tracker.steps == []

    def test_status_order_defined(self):
        """Status order is defined for sorting."""
        tracker = StepTracker("Test")
        expected_statuses = {"pending", "running", "done", "error", "skipped"}
        assert set(tracker.status_order.keys()) == expected_statuses


class TestStepTrackerAddStep:
    """BEHAVIOR: add() creates new steps in pending state."""

    def test_add_creates_step(self):
        """add() creates a step with key and label."""
        tracker = StepTracker("Test")
        tracker.add("step1", "Step One")
        assert len(tracker.steps) == 1

    def test_step_has_correct_structure(self):
        """Step has key, label, status, detail fields."""
        tracker = StepTracker("Test")
        tracker.add("step1", "Step One")
        step = tracker.steps[0]
        assert step["key"] == "step1"
        assert step["label"] == "Step One"
        assert step["status"] == "pending"
        assert step["detail"] == ""

    def test_add_same_key_is_noop(self):
        """Adding same key twice is a no-op."""
        tracker = StepTracker("Test")
        tracker.add("step1", "First Label")
        tracker.add("step1", "Second Label")  # Should be ignored
        assert len(tracker.steps) == 1
        assert tracker.steps[0]["label"] == "First Label"

    def test_add_multiple_steps(self):
        """Can add multiple steps."""
        tracker = StepTracker("Test")
        tracker.add("step1", "One")
        tracker.add("step2", "Two")
        tracker.add("step3", "Three")
        assert len(tracker.steps) == 3


class TestStepTrackerStatusTransitions:
    """BEHAVIOR: Status transition methods."""

    def test_start_sets_running(self):
        """start() sets status to 'running'."""
        tracker = StepTracker("Test")
        tracker.add("step1", "Step One")
        tracker.start("step1")
        assert tracker.steps[0]["status"] == "running"

    def test_complete_sets_done(self):
        """complete() sets status to 'done'."""
        tracker = StepTracker("Test")
        tracker.add("step1", "Step One")
        tracker.complete("step1")
        assert tracker.steps[0]["status"] == "done"

    def test_error_sets_error(self):
        """error() sets status to 'error'."""
        tracker = StepTracker("Test")
        tracker.add("step1", "Step One")
        tracker.error("step1")
        assert tracker.steps[0]["status"] == "error"

    def test_skip_sets_skipped(self):
        """skip() sets status to 'skipped'."""
        tracker = StepTracker("Test")
        tracker.add("step1", "Step One")
        tracker.skip("step1")
        assert tracker.steps[0]["status"] == "skipped"

    def test_start_with_detail(self):
        """start() can set detail text."""
        tracker = StepTracker("Test")
        tracker.add("step1", "Step One")
        tracker.start("step1", "working...")
        assert tracker.steps[0]["detail"] == "working..."

    def test_complete_with_detail(self):
        """complete() can set detail text."""
        tracker = StepTracker("Test")
        tracker.add("step1", "Step One")
        tracker.complete("step1", "all done")
        assert tracker.steps[0]["detail"] == "all done"


class TestStepTrackerAutoCreate:
    """BEHAVIOR: Status methods auto-create steps if key not found."""

    def test_update_creates_step_if_not_exists(self):
        """Updating unknown key creates the step."""
        tracker = StepTracker("Test")
        tracker.complete("new_step", "created on complete")
        assert len(tracker.steps) == 1
        assert tracker.steps[0]["key"] == "new_step"
        assert tracker.steps[0]["status"] == "done"


class TestStepTrackerRefreshCallback:
    """BEHAVIOR: attach_refresh() enables live updates."""

    def test_attach_refresh_stores_callback(self):
        """attach_refresh() stores callback function."""
        tracker = StepTracker("Test")
        callback_called = []
        tracker.attach_refresh(lambda: callback_called.append(True))
        tracker.add("step1", "One")
        assert len(callback_called) > 0

    def test_callback_triggered_on_add(self):
        """Callback triggered when step added."""
        tracker = StepTracker("Test")
        calls = []
        tracker.attach_refresh(lambda: calls.append("add"))
        tracker.add("step1", "One")
        assert "add" in calls

    def test_callback_triggered_on_status_change(self):
        """Callback triggered on status change."""
        tracker = StepTracker("Test")
        calls = []
        tracker.attach_refresh(lambda: calls.append("change"))
        tracker.add("step1", "One")
        calls.clear()
        tracker.complete("step1")
        assert "change" in calls

    def test_callback_exception_ignored(self):
        """Callback exceptions are silently ignored."""
        tracker = StepTracker("Test")
        tracker.attach_refresh(lambda: 1/0)  # Will raise ZeroDivisionError
        # Should not raise
        tracker.add("step1", "One")


class TestStepTrackerRender:
    """BEHAVIOR: render() produces Rich Tree output."""

    def test_render_returns_tree(self):
        """render() returns a Rich Tree object."""
        from rich.tree import Tree
        tracker = StepTracker("Test")
        result = tracker.render()
        assert isinstance(result, Tree)

    def test_render_includes_title(self):
        """Rendered tree includes title."""
        tracker = StepTracker("My Title")
        tree = tracker.render()
        assert "My Title" in str(tree.label)


class TestStepTrackerStatusSymbols:
    """BEHAVIOR: Status symbols in rendered output."""

    # These are the exact symbols used:
    # done: [green]●[/green]
    # pending: [green dim]○[/green dim]  
    # running: [cyan]○[/cyan]
    # error: [red]●[/red]
    # skipped: [yellow]○[/yellow]

    def test_done_uses_green_filled_circle(self):
        """Done status uses green filled circle (●)."""
        tracker = StepTracker("Test")
        tracker.add("step1", "One")
        tracker.complete("step1")
        # Symbol is [green]●[/green]

    def test_pending_uses_dim_green_circle(self):
        """Pending status uses dim green circle (○)."""
        tracker = StepTracker("Test")
        tracker.add("step1", "One")
        # Symbol is [green dim]○[/green dim]

    def test_running_uses_cyan_circle(self):
        """Running status uses cyan circle (○)."""
        tracker = StepTracker("Test")
        tracker.add("step1", "One")
        tracker.start("step1")
        # Symbol is [cyan]○[/cyan]

    def test_error_uses_red_filled_circle(self):
        """Error status uses red filled circle (●)."""
        tracker = StepTracker("Test")
        tracker.add("step1", "One")
        tracker.error("step1")
        # Symbol is [red]●[/red]

    def test_skipped_uses_yellow_circle(self):
        """Skipped status uses yellow circle (○)."""
        tracker = StepTracker("Test")
        tracker.add("step1", "One")
        tracker.skip("step1")
        # Symbol is [yellow]○[/yellow]


class TestStepTrackerDetailFormatting:
    """BEHAVIOR: Detail text formatting in rendered output."""

    def test_detail_shown_in_parentheses(self):
        """Detail text shown in parentheses after label."""
        tracker = StepTracker("Test")
        tracker.add("step1", "Step One")
        tracker.complete("step1", "completed successfully")
        # Format: symbol label (detail)

    def test_empty_detail_no_parentheses(self):
        """Empty detail doesn't show parentheses."""
        tracker = StepTracker("Test")
        tracker.add("step1", "Step One")
        tracker.complete("step1")
        # Format: symbol label (no parentheses)

    def test_pending_shows_dim_text(self):
        """Pending steps show entire line in dim gray."""
        tracker = StepTracker("Test")
        tracker.add("step1", "Step One")
        # Uses [bright_black] for dim text
