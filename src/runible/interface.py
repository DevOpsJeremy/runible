from blinker import Signal


class InterfaceSignal(Signal):
    event_sender = "runner_event"
    cancel_sender = "runner_cancel"
    finished_sender = "runner_finished"
    status_sender = "runner_status"
    artifacts_sender = "runner_artifacts"

    def __init__(self):
        super().__init__()

    def get_handlers(self, step=None):
        """Return a mapping of handler names to callables bound to this signaler.

        Each handler captures the `step` that initiated the runner and forwards
        the original positional and keyword arguments from ansible_runner by
        embedding them as `event_args` and `event_kwargs` in the signal.
        """

        def _make_handler(sender_attr):
            sender_value = getattr(self, sender_attr)

            def _handler(*args, **kwargs):
                # Send the signal with the Step context and the original args/kwargs
                self.send(sender=sender_value, step=step, event_args=args, event_kwargs=kwargs)

            return _handler

        return {
            "event_handler": _make_handler("event_sender"),
            "cancel_callback": _make_handler("cancel_sender"),
            "finished_callback": _make_handler("finished_sender"),
            "status_handler": _make_handler("status_sender"),
            "artifacts_handler": _make_handler("artifacts_sender"),
        }

    @classmethod
    def receive(cls, *args, **kwargs):
        print(f"RECEIVED: args - {args}, kwargs - {kwargs}")

    @classmethod
    def signal_event(cls, *args, **kwargs):
        cls().send(sender=cls.event_sender, *args, **kwargs)

    @classmethod
    def signal_cancel(cls, *args, **kwargs):
        cls().send(sender=cls.cancel_sender, *args, **kwargs)

    @classmethod
    def signal_finished(cls, *args, **kwargs):
        cls().send(sender=cls.finished_sender, *args, **kwargs)

    @classmethod
    def signal_status(cls, *args, **kwargs):
        cls().send(sender=cls.status_sender, *args, **kwargs)

    @classmethod
    def signal_artifacts(cls, *args, **kwargs):
        cls().send(sender=cls.artifacts_sender, *args, **kwargs)


class Interface:
    def __init__(self):
        pass

    def event(self):
        pass

    def cancel(self):
        pass
 
    def finished(self):
        pass

    def status(self):
        pass

    def artifacts(self):
        pass

