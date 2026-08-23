from datetime import datetime

from ..engine import Step
from ..interface import Interface


class LogInterface(Interface):
    """The ``log`` Runible interface logs each output
    to the console with a timestamp and the associated step.
    """

    def event(self, sender: Step, **event_data):
        """Handle an ``event`` emitted by the running playbook.

        ``event_data`` contains the event payload forwarded from ansible-runner.
        On each event, this interface prints to stdout with a log format indicating
        the datetime and which step triggered the event. The output is in the following
        format:

        ``<datetime> : [RUNIBLE] [<step name>] <stdout>``
        """

        stdout = event_data.get("stdout")
        if not stdout:
            return

        dt = datetime.now()  # noqa DTZ005
        for line in stdout.splitlines():
            if line != "":
                print(f"{dt} : [RUNIBLE] [{sender.name}] {line}")
