from __future__ import annotations

import sys
import threading
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Optional

from ..interface import Interface


class StepState(Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"
    UNKNOWN = "unknown"


@dataclass
class StepViewModel:
    name: str
    after: List[str] = field(default_factory=list)
    status: StepState = StepState.PENDING
    runner_result: Optional[dict] = None
    latest_event: Optional[str] = None
    artifacts: Optional[str] = None
    timestamps: Dict[str, float] = field(default_factory=dict)

    def set_running(self):
        if self.status in (StepState.SUCCESS, StepState.FAILED, StepState.CANCELLED):
            return
        self.status = StepState.RUNNING

    def set_event(self, summary: str):
        self.latest_event = summary

    def set_status(self, status: str):
        # Map runner status strings conservatively
        if status in ("successful", "success"):
            self.status = StepState.SUCCESS
        elif status in ("failed", "fail"):
            self.status = StepState.FAILED
        elif status in ("cancelled", "canceled"):
            self.status = StepState.CANCELLED

    def set_finished(self, result: dict):
        # Respect existing terminal states
        if self.status in (StepState.SUCCESS, StepState.FAILED, StepState.CANCELLED):
            return
        rc = None
        if isinstance(result, dict):
            rc = result.get("rc")
            status = result.get("status")
            if status is not None:
                self.set_status(status)
                return
        if rc is None:
            self.status = StepState.SUCCESS
        else:
            self.status = StepState.SUCCESS if rc == 0 else StepState.FAILED
        self.runner_result = result

    def set_cancelled(self):
        if self.status in (StepState.SUCCESS, StepState.FAILED):
            return
        self.status = StepState.CANCELLED

    def set_unknown(self):
        if self.status in (StepState.SUCCESS, StepState.FAILED, StepState.CANCELLED):
            return
        self.status = StepState.UNKNOWN


@dataclass
class WorkflowViewModel:
    steps: Dict[str, StepViewModel] = field(default_factory=dict)
    declaration_order: List[str] = field(default_factory=list)
    selected: Optional[str] = None
    initialized: bool = False

    def initialize_from_plan(self, plan_sender) -> None:
        # plan_sender.plan.steps is expected to be an ordered iterable of Step
        self.steps.clear()
        self.declaration_order.clear()
        for s in getattr(plan_sender.plan, "steps", []):
            name = getattr(s, "name", None)
            if name is None:
                continue
            after = list(getattr(s, "after", []) or [])
            self.steps[name] = StepViewModel(name=name, after=after)
            self.declaration_order.append(name)
        if self.declaration_order:
            self.selected = self.declaration_order[0]
        self.initialized = True


class WorkflowInterface(Interface):
    """A conservative, testable workflow interface skeleton.

    This implementation follows the documented integration contract but does not
    require Textual at import time. When running in a TTY and Textual is
    available, a dedicated UI thread can be launched later. Otherwise the
    interface falls back to a concise textual-summary behavior so it is safe in
    non-interactive runs.
    """

    def __init__(self):
        super().__init__(quiet=True)
        self._lock = threading.Lock()
        self._model = WorkflowViewModel()
        self._ui_thread: Optional[threading.Thread] = None
        self._started = False
        self._tty = sys.stdout.isatty()

    # -- Helper methods -------------------------------------------------
    def _ensure_model(self, sender) -> None:
        # Initialize model exactly once, guarded by a lock
        with self._lock:
            if not self._model.initialized:
                self._model.initialize_from_plan(sender)

    def _maybe_start_ui(self):
        # Attempt to import textual and launch a UI in a background thread when
        # running in a TTY. This is optional and best-effort; failures are
        # logged to stderr but do not raise.
        if not self._tty or self._ui_thread is not None:
            return
        try:
            from textual.app import App  # type: ignore

            # Minimal no-op UI placeholder. Actual UI will be implemented later.
            class _NoopApp(App):
                async def on_mount(self):
                    pass

            def _run_app():
                try:
                    _NoopApp().run()
                except Exception as exc:  # pragma: no cover - fallback runtime
                    print("[runible:workflow] UI thread failed:", exc, file=sys.stderr)

            self._ui_thread = threading.Thread(target=_run_app, daemon=True)
            self._ui_thread.start()
        except Exception:
            # Textual not available; ignore and fallback to non-UI output
            print("[runible:workflow] textual not available; running in fallback mode", file=sys.stderr)

    def _summarize_step(self, step: StepViewModel) -> str:
        return f"{step.name}: {step.status.value}{' (' + step.latest_event + ')' if step.latest_event else ''}"

    def _print_summary(self):
        # Print a compact summary of all steps; used when no TTY or textual
        with self._lock:
            lines = [self._summarize_step(s) for n, s in self._model.steps.items()]
        for l in lines:
            print(f"[runible] {l}")

    # -- Signal handlers ------------------------------------------------
    def start(self, sender):
        """Called when a Step starts. Initialize the model and mark the step running."""
        self._ensure_model(sender)
        name = getattr(sender, "name", None)
        if name is None:
            return
        with self._lock:
            step = self._model.steps.get(name)
            if step is None:
                # Defensive: add unknown step
                step = StepViewModel(name=name)
                self._model.steps[name] = step
                self._model.declaration_order.append(name)
            step.set_running()
        # Start the UI lazily if appropriate
        self._maybe_start_ui()
        if not self._tty:
            # Immediate feedback for non-TTY runs
            print(f"[runible] start: {name}")

    def event(self, sender, **event_data):
        """Handle ansible-runner events; retain a short summary."""
        self._ensure_model(sender)
        name = getattr(sender, "name", None)
        if name is None:
            return
        # Extract stable fields
        ev = event_data.get("event") or event_data.get("event_data") or ""
        task = None
        try:
            task = event_data.get("event_data", {}).get("task")
        except Exception:
            task = None
        host = event_data.get("event_data", {}).get("host") if event_data.get("event_data") else None
        stdout = event_data.get("stdout")
        summary_parts = []
        if ev:
            summary_parts.append(str(ev))
        if task:
            summary_parts.append(str(task))
        if host:
            summary_parts.append(str(host))
        if stdout:
            # keep only first non-empty line
            for line in str(stdout).splitlines():
                if line.strip():
                    summary_parts.append(line.strip())
                    break
        summary = " ".join(summary_parts) if summary_parts else None
        with self._lock:
            step = self._model.steps.get(name)
            if step:
                if summary:
                    step.set_event(summary)
        if not self._tty:
            # For non-TTY, print a terse event line
            if summary:
                print(f"[runible:event] [{name}] {summary}")

    def status(self, sender, status_data, runner_config):
        """Store concise runner status and map early terminal states."""
        self._ensure_model(sender)
        name = getattr(sender, "name", None)
        if name is None:
            return
        status_str = None
        try:
            status_str = status_data.get("status")
        except Exception:
            status_str = None
        with self._lock:
            step = self._model.steps.get(name)
            if step and status_str:
                step.set_status(status_str)
        if not self._tty and status_str:
            print(f"[runible:status] [{name}] {status_str}")

    def finished(self, sender, runner):
        """Map runner outcome to terminal state and record result."""
        self._ensure_model(sender)
        name = getattr(sender, "name", None)
        result = None
        try:
            # runner can be a Runner instance or an ad-hoc dict-like
            if hasattr(runner, "rc") or hasattr(runner, "status"):
                result = {"rc": getattr(runner, "rc", None), "status": getattr(runner, "status", None)}
            elif isinstance(runner, dict):
                result = runner
        except Exception:
            result = None
        with self._lock:
            step = self._model.steps.get(name)
            if step:
                step.set_finished(result or {})
        if not self._tty:
            print(f"[runible:finished] [{name}] result={result}")

    def cancel(self, sender):
        self._ensure_model(sender)
        name = getattr(sender, "name", None)
        if name is None:
            return
        with self._lock:
            step = self._model.steps.get(name)
            if step:
                step.set_cancelled()
        if not self._tty:
            print(f"[runible:cancel] [{name}]")

    def artifacts(self, sender, artifact_dir: str):
        self._ensure_model(sender)
        name = getattr(sender, "name", None)
        if name is None:
            return
        with self._lock:
            step = self._model.steps.get(name)
            if step:
                step.artifacts = artifact_dir
        if not self._tty:
            print(f"[runible:artifacts] [{name}] {artifact_dir}")

    def end(self, sender):
        """Finalise a step that returned without a more specific terminal state."""
        self._ensure_model(sender)
        name = getattr(sender, "name", None)
        if name is None:
            return
        with self._lock:
            step = self._model.steps.get(name)
            if step and step.status == StepState.RUNNING:
                # If no terminal callback arrived, mark as unknown
                step.set_unknown()
        if not self._tty:
            print(f"[runible:end] [{name}] state={self._model.steps.get(name).status if name in self._model.steps else 'unknown'}")


# Expose plugin entrypoint name in module for convenience
workflow = "runible.plugins.workflow:WorkflowInterface"
