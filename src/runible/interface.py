from blinker import Signal
from importlib.metadata import entry_points

class Interface:
    entry_group = "runible"
    signaler = Signal()

    def __init__(self):
        self.initialize_plugins()

    def initialize_plugins(self):
        plugins = entry_points(group=self.entry_group)
        for ep in plugins:
            print(ep)

