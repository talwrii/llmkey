from pynput import keyboard

class KeyBinder:
    def __init__(self, bindings):
        self.bindings = bindings
        self.hotkeys = [make_hotkey(k, v) for k, v in bindings.items()]
        self.listener = keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release)

    def on_press(self, k):
        for key in self.hotkeys:
            key.press(self.listener.canonical(k))

    def on_release(self, k):
        for key in self.hotkeys:
            key.release(self.listener.canonical(k))

    def __enter__(self):
        self.listener.__enter__()
        return self

    def __exit__(self, exc_type, exc_value, tb):
        return self.listener.__exit__(exc_type, exc_value, tb)

    def join(self):
        self.listener.join()


if __name__ == '__main__':
    def click():
        print("pressed")

    with KeyBinder({
        "<ctrl>+<alt>+h": click
    }) as b:
        b.join()


def make_hotkey(k, f):
    return keyboard.HotKey(
        keyboard.HotKey.parse(k),
        f)
