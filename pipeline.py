from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.widgets import Static
from textual.widget import Widget

class Stage(Widget):
    def __init__(self, name: str, status: str, jobs: list[str], subtitle: str = ""):
        # status classes: passed, running, failed, pending
        super().__init__(classes=f"stage {status}")
        self.name = name
        self.status = status
        self.jobs = jobs
        self.subtitle = subtitle

    def compose(self) -> ComposeResult:
        icons = {"passed": "🟢", "running": "🔄", "failed": "🔴", "pending": "⚪"}
        icon = icons.get(self.status, "⚪")
        header = f"{icon}  [b]{self.name}[/b]\n[dim]{self.status.upper()}[/dim]"
        yield Static(header, classes="stage-header")
        jobs_text = "\n".join(f"• {j}" for j in self.jobs)
        yield Static(jobs_text, classes="stage-body")
        yield Static(self.subtitle, classes="stage-footer")

class PipelineApp(App):
    CSS_PATH = "pipeline.css"
    TITLE = "CI/CD Pipeline (Mock)"

    def compose(self) -> ComposeResult:
        yield Static("[b]Project: runible[/b]\n[dim]branch: main · build #124[/dim]", classes="title")
        with Horizontal(classes="pipeline"):
            yield Stage("Build", "passed", ["Install deps", "Lint", "Compile"], "2m 12s")
            yield Static("⟶", classes="connector")
            yield Stage("Test", "running", ["Unit tests", "Integration tests"], "running · 34/120")
            yield Static("⟶", classes="connector")
            yield Stage("Deploy", "pending", ["Package", "Push image", "Apply"], "queued")
        yield Static("", classes="spacer")

if __name__ == "__main__":
    PipelineApp().run()
