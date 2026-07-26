from blinker import Signal


class InterfaceSignal(Signal):
    event_sender = "event"
    cancel_sender = "cancel"
    finished_sender = "finished"
    status_sender = "status"
    artifacts_sender = "artifacts"

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
                self.send(
                    sender=sender_value, step=step, event_args=args, event_kwargs=kwargs
                )

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
        #print(f"RECEIVED: args - {args}, kwargs - {kwargs}")
        if "step" not in kwargs:
            return

        step = kwargs["step"]
        if 'sender' in kwargs and kwargs['sender'] == 'event':
            step.plan.interface.event(step.plan.interface, step=step, event_data=kwargs['event_args'][0])

        interface = step.get_interface()
        _invoke_args = []
        if "event_args" in kwargs and kwargs["event_args"]:
            _invoke_args.extend(kwargs["event_args"])

        _invoke_kwargs = {'signal': kwargs.get("sender")}
        if "event_kwargs" in kwargs and kwargs["event_kwargs"]:
            _invoke_kwargs = {**_invoke_kwargs, **kwargs["event_kwargs"]}

        #interface.invoke(*_invoke_args, **_invoke_kwargs)

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

    def invoke(self, signal, *args, **kwargs):
        match signal:
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

    def event(self, event_data):
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
