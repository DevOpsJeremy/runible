from runible.interface import Interface
from datetime import datetime


class CustInterface(Interface):
    def __init__(self):
        super().__init__()

    def event(self, event_data, step):
        stdout = event_data["stdout"]
        dt = datetime.now()
        for line in stdout.splitlines():
            if line != "":
                print(f"{datetime.now()} : [RUNIBLE] [{step.name}] {line}")


def main():
    return CustInterface


if __name__ == "__main__":
    main()
