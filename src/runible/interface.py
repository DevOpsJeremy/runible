from blinker import Signal
from ansible_runner.runner import Runner
from ansible_runner.config.runner import RunnerConfig


class Interface:
    signaler = Signal()

    def __init__(self):
        pass

    def get_handlers(self):
        return {
            "quiet": True,
            "event_handler": self.event_handler,
            "cancel_callback": self.cancel_callback,
            "finished_callback": self.finished_callback,
            "status_handler": self.status_handler,
            "artifacts_handler": self.artifacts_handler,
        }

    @classmethod
    def signal(cls, sender: str):
        cls.signaler.send(sender)

    @classmethod
    def event_handler(cls, event_data: dict):
        return True

    @classmethod
    def cancel_callback(cls):
        return False

    @classmethod
    def finished_callback(cls, runner: Runner):
        pass

    @classmethod
    def status_handler(cls, status_data: dict, runner_config: RunnerConfig):
        pass

    @classmethod
    def artifacts_handler(cls, artifact_dir: str):
        pass
