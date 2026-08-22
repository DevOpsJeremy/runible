from ..interface import Interface


class DefaultInterface(Interface):
    """Default interface. This disables all output."""

    def __init__(self):
        super().__init__(quiet=False)
