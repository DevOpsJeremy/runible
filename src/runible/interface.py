from blinker import Signal


class InterfaceSignal(Signal):
    event_sender = "event"
    cancel_sender = "cancel"
    finished_sender = "finished"
    status_sender = "status"
    artifacts_sender = "artifacts"

    def __init__(self):
        super().__init__()

    @classmethod
    def receive(cls, *args, **kwargs):
        if "step" not in kwargs:
            return

        step = kwargs["step"]
        _invoke_args = [*args]
        _invoke_kwargs = kwargs.copy()

        step.plan.interface.invoke(*_invoke_args, **_invoke_kwargs)


class Interface:
    def __init__(self):
        pass

    def invoke(self, sender, *args, **kwargs):
        match sender:
            case "initiate":
                return self.initiate(*args, **kwargs)
            case "event":
                return self.event(*args, **kwargs)
            case "cancel":
                return self.cancel(*args, **kwargs)
            case "finished":
                return self.finished(*args, **kwargs)
            case "status":
                return self.status(*args, **kwargs)
            case "artifacts":
                return self.artifacts(*args, **kwargs)
            case "complete":
                return self.complete(*args, **kwargs)

    def initiate(self, *args, **kwargs):
        pass

    def event(self, event_data, *args, **kwargs):
        pass

    def cancel(self, *args, **kwargs):
        pass

    def finished(self, *args, **kwargs):
        pass

    def status(self, *args, **kwargs):
        pass

    def artifacts(self, *args, **kwargs):
        pass

    def complete(self, *args, **kwargs):
        pass
