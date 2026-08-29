from ..interface import Interface
from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, Markdown, Placeholder

class StopwatchApp(App):
    """A Textual app to manage stopwatches."""

    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]
    MARKDOWN2 = """
<style>
.graph {
  p {
    display: inline;
  }
}
.success {
  color: green;
  content: ●;
}
.pending {
  color: gray;
}
.running {
  color: yellow;
}
</style>
<div class="graph">
<pre>
   ╭─<p class="success">●</p>───────╮
   │         ├──<p class="pending">●</p>
<p class="success">●</p>──┤    ╭─<p class="pending">●</p>──╯
   ╰─<p class="running">●</p>──┤
        ╰─<p class="pending">●</p>
</pre>
</div>
"""
    MARKDOWN = """
```text
   ╭─●───────╮
   │         ├──●
●──┤    ╭─●──╯
   ╰─●──┤
        ╰─●
```
"""

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        markdown = Markdown(self.MARKDOWN)
        yield Header()
        yield markdown
        yield Footer()

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )

class WorkflowInterface2(Interface):
    def start(self, sender: Step):
        app = StopwatchApp()
        app.run()

class WorkflowInterface(Interface):
    def __init__(self):
        app = StopwatchApp()
        app.run()

