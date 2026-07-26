from datetime import datetime

from runible.engine import Step
from runible.interface import Interface


class LogInterface(Interface):
    def __init__(self):
        super().__init__()

    def event(self, sender: Step, **event_data):
        stdout = event_data["stdout"]
        dt = datetime.now()  # noqa
        for line in stdout.splitlines():
            if line != "":
                print(f"{dt} : [RUNIBLE] [{sender.name}] {line}")
