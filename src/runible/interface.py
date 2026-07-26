from .engine import Step
from ansible_runner.runner import Runner
from ansible_runner.runner_config import RunnerConfig
from blinker import signal


class Interface:
    def __init__(self):
        self.register_listeners()

    def register_listeners(self):
        signal("start").connect(self.start)
        signal("event").connect(self.event)
        signal("finished").connect(self.finished)
        signal("artifacts").connect(self.artifacts)
        signal("status").connect(self.status)
        signal("cancel").connect(self.cancel)
        signal("end").connect(self.end)

    def start(self, sender: Step):
        pass

    def event(self, sender: Step, **event_data):
        pass

    def cancel(self, sender: Step):
        pass

    def finished(self, sender: Step, runner: Runner):
        pass

    def status(self, sender: Step, status_data: dict, runner_config: RunnerConfig):
        pass

    def artifacts(self, sender: Step, artifact_dir: str):
        pass

    def end(self, sender: Step):
        pass
