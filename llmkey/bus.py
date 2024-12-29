from . import tk_tools

class Bus:
    def __init__(self, tk_root):
        self.tk_root = tk_root

    def send(self, event, *, data=None):
        self.tk_root.event_generate(event, data=data)

    def bind(self, event, callback):
        tk_tools.my_bind(self.tk_root, event, callback)


class MockBus:
    def send(self, event, *, data=None):
        print("Sending", event, data)


    def bind(self, *_):
        raise NotImplementedError()
