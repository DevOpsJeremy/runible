from runible.interface import Interface


class DefaultInterface(Interface):
    def __init__(self):
        super().__init__()


def main():
    return DefaultInterface


if __name__ == "__main__":
    main()
