from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, Tree
from textual.binding import Binding

class MyTree(Tree):
    BINDINGS = [
        Binding("j", "cursor_down", "Cursor Down", priority=True, show=False),
        Binding("k", "cursor_up", "Cursor Up", priority=True, show=False),
        Binding("l", "cursor_right", "Cursor Right", priority=True, show=False),
        Binding("h", "cursor_left", "Cursor Left", priority=True, show=False),
    ]

class StopwatchApp(App):
    BINDINGS = [
        Binding("d", "toggle_dark", "Toggle dark mode"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        tree: MyTree[str] = MyTree("Node1")
        tree.auto_expand = True
        node2 = tree.root.add("Node2")
        node2.add_leaf("Node3")
        node4 = node2.add("Node4")
        node4.add_leaf("Node6")
        node2.add_leaf("Node5")
        yield tree
        yield Footer()

    def action_toggle_dark(self) -> None:
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )

if __name__ == "__main__":
    app = StopwatchApp()
    app.run()
