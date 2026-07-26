from ..interface import Interface


class DefaultInterface(Interface):
    def __init__(self):
        super().__init__(quiet=False)
