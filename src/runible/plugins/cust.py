from runible.interface import Interface
from datetime import datetime


class CustInterface(Interface):
    def __init__(self):
        super().__init__()

    def event(self, step, *args, **kwargs):
        stdout = kwargs["stdout"]
        dt = datetime.now()
        for line in stdout.splitlines():
            if line != "":
                print(f"{datetime.now()} : [RUNIBLE] [{step.name}] {line}")
