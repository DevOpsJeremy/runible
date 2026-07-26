from runible.interface import Interface
from runible.engine import Step
from datetime import datetime


class LogInterface(Interface):
    def __init__(self):
        super().__init__()

    def event(self, sender: Step, **event_data):
        stdout = event_data["stdout"]
        dt = datetime.now()
        for line in stdout.splitlines():
            if line != "":
                print(f"{dt} : [RUNIBLE] [{sender.name}] {line}")
