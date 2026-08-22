from ansible_runner.runner import Runner
from ansible_runner.runner_config import RunnerConfig
from blinker import signal

from .engine import Step


class Interface:
    """The base Interface class which other interfaces will extend"""

    def __init__(self, quiet: bool = True):
        self.quiet = quiet
        self.register_listeners()

    def register_listeners(self):
        """Connects listener callbacks to specific signals"""

        signal("start").connect(self.start)
        signal("event").connect(self.event)
        signal("finished").connect(self.finished)
        signal("artifacts").connect(self.artifacts)
        signal("status").connect(self.status)
        signal("cancel").connect(self.cancel)
        signal("end").connect(self.end)

    def start(self, sender: Step):
        """Handle the ``start`` signal for a step.

        ``sender`` is the `Step` instance that emitted the signal.
        This is the default ``start`` method from the ``Interface`` class.
        Override in subclasses to provide the behavior when the callback is triggered.
        """

    def event(self, sender: Step, **event_data):
        """Handle an ``event`` emitted by the running playbook.

        ``event_data`` contains the event payload forwarded from ansible-runner.
        This is the default ``event`` method from the ``Interface`` class.
        Override in subclasses to provide the behavior when the callback is triggered.
        """

    def cancel(self, sender: Step):
        """Called when a step is cancelled.

        ``sender`` is the Step which initiated the event.
        This is the default ``cancel`` method from the ``Interface`` class.
        Override in subclasses to provide the behavior when the callback is triggered.
        """

    def finished(self, sender: Step, runner: Runner):
        """Called when a step finishes.

        ``sender`` is the Step which initiated the event.
        ``runner`` is the underlying Runner instance from ansible-runner.
        This is the default ``finished`` method from the ``Interface`` class.
        Override in subclasses to provide the behavior when the callback is triggered.
        """

    def status(self, sender: Step, status_data: dict, runner_config: RunnerConfig):
        """Receive status updates from ansible-runner.

        ``status_data`` is a dict describing the status; ``runner_config`` is the
        RunnerConfig used for the invocation.
        This is the default ``status`` method from the ``Interface`` class.
        Override in subclasses to provide the behavior when the callback is triggered.
        """

    def artifacts(self, sender: Step, artifact_dir: str):
        """Handle artifact directory notifications for a finished run.

        This is the default ``artifacts`` method from the ``Interface`` class.
        Override in subclasses to provide the behavior when the callback is triggered.
        """

    def end(self, sender: Step):
        """Handle the end of a step's lifecycle.

        This is the default ``end`` method from the ``Interface`` class.
        Override in subclasses to provide the behavior when the callback is triggered.
        """
