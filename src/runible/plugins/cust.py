from runible.interface import Interface
from datetime import datetime


class CustInterface(Interface):
    def __init__(self):
        super().__init__()

    @classmethod
    def event_handler(cls, event_data):
        stdout = event_data['stdout']
        dt = datetime.now()
        for line in stdout.splitlines():
            if line != '':
                print(f"{datetime.now()} : [RUNIBLE] {line}")


def main():
    return CustInterface


if __name__ == "__main__":
    main()
