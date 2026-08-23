from datetime import datetime

from ..engine import Step
from ..interface import Interface


class LogInterface(Interface):
    def event(self, sender: Step, **event_data):
        stdout = event_data.get("stdout")
        if not stdout:
            return

        dt = datetime.now()  # noqa DTZ005
        for line in stdout.splitlines():
            if line != "":
                print(f"{dt} : [RUNIBLE] [{sender.name}] {line}")
