import networkx as nx
from textual.widget import Widget

di_graph = nx.DiGraph()

di_graph.add_edges_from([
    ("checkout", "build"),
    ("build", "test"),
    ("build", "lint"),
    ("test", "deploy"),
    ("lint", "deploy"),
])

di_graph.nodes["build"]["label"] = "Build"
di_graph.nodes["build"]["status"] = "running"
di_graph.nodes["build"]["duration"] = "42s"

class Graph(Widget):
    DEFAULT_CSS = """
    Graph {
        width: 40;
        height: 9;
        padding: 1 2;
        background: $panel;
        color: $text;
        border: $secondary tall;
        content-align: center middle;
    }
    """
    GLYPHS = {
        "PENDING": "○",
        "SUCCESS": "●",
        "FAILED": "×",
        "CANCELED": "⊘",
    }
    LINES: dict[str, tuple[str, str, str, str]] = { # https://en.wikipedia.org/wiki/Box_Drawing
        "default": (
            " ",
            "│",
            "└",
            "├",
            "┴",
            "┼",
            "╭",
            "╰",
            "╮",
            "╯"
        ),
        "bold": (
            "  ",
            "┃ ",
            "┗━",
            "┣━",
        ),
        "double": (
            "  ",
            "║ ",
            "╚═",
            "╠═",
        ),
    }
    def __init__(
        self,
        di_graph: nx.DiGraph
    ):
        self.di_graph = di_graph
        super().__init__()

    def render(self):
        return f"{self.GLYPHS['PENDING']}"

from textual.app import App, ComposeResult
from textual.widgets import Footer, Header

class MyApp(App):
    def compose(self) -> ComposeResult:
        yield Header()
        graph_widget = Graph(di_graph)
        yield graph_widget
        yield Footer()

if __name__ == "__main__":
    app = MyApp()
    app.run()
