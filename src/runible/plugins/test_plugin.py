from runible.interface import Interface


class TestInterface(Interface):
    def __init__(self):
        super().__init__()


def main():
    return TestInterface


if __name__ == "__main__":
    main()
