from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, Tree

class StopwatchApp(App):
    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]

    def compose(self) -> ComposeResult:
        yield Header()
        tree: Tree[str] = Tree("Node1")
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
