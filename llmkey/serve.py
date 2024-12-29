import logging
import threading
import tkinter as tk

import pyperclip


from . import (gui_first_run, gui_menu, gui_prompt, gui_reply, gui_settings,
               gui_status, gui_tray, llm, runner, tk_tools, config, gui_first_run,
               hotkeys, bus as bus_module)

from .config import Config

@config.with_config
def one_off(conf, query):
    backend, model = get_model_and_backend(conf)
    logging.info("Sending one-off to %s %r", model, query)
    return backend.query(model=model, query=query)

def get_model_and_backend(conf: Config):
    conf.load()
    backend = llm.get(conf.backend)
    model = conf.backend_models.get(backend.name, backend.default_model)
    return backend, model


class TkCallbacks:
    def __init__(self, root, bus, tray, llm_runner):
        self.root = root
        self.bus = bus
        self.tray = tray
        self.llm_runner = llm_runner
        self.query = None
        self.reply_windows = []
        self.display_window = None

    @staticmethod
    @gui_status.show_errors
    def settings(_):
        gui_settings.settings()

    def quit(self, _):
        self.root.quit()

    @gui_status.show_errors
    def one_off(self, _):
        if not ensure_settings_ready():
            return

        if self.query:
            gui_status.running(self.query.bytes, self.query.duration)
            return

        conf = config.Config()
        conf.load()

        backend = llm.get(conf.backend)
        model = conf.backend_models.get(conf.backend, backend.default_model)

        query = gui_prompt.prompt_one_off(conf.backend, model)

        if query is None:
            return

        self.query = one_off(query)
        self.llm_runner.run(self.query.run, "<<one_off_finished>>")

    @gui_status.show_errors
    def one_off_finished(self, event):
        if self.query:
            pyperclip.copy(event.data)
            window = gui_reply.reply(self.bus, self.query.duration, event.data)
            self.query = None
            self.new_window(window)

    def new_window(self, window):
        self.reply_windows.append(window)
        self.display_window = window

    @gui_status.show_errors
    def clipboard(self, _):
        if self.query:
            gui_status.running(self.query.bytes, self.query.duration)
            return

        message = gui_prompt.prompt_clipboard()
        print("Got message: %s", message)

        self.query = one_off(message)
        self.llm_runner.run(self.query.run, "<<clipboard_finished>>")

    @gui_status.show_errors
    def clipboard_finished(self, event):
        if self.query:
            pyperclip.copy(event.data)
            window = gui_reply.reply(self.bus, self.query.duration, event.data)
            self.query = None
            self.new_window(window)

    @gui_status.show_errors
    def failed(self, event):
        self.query = None
        gui_status.failed(event.data)

    @gui_status.show_errors
    def close_last(self, event):
        del event
        if self.reply_windows:
            window = self.reply_windows.pop()
            if not window.closed:
                window.destroy()

            if self.reply_windows:
                self.display_window = self.reply_windows[-1]
            else:
                self.display_window = None

    @gui_status.show_errors
    def close_reply(self, event):
        id_ = event.data["id"]
        i, windows = [(i, w) for i, w in enumerate(self.reply_windows) if w.id == id_]
        if windows:
            windows[0].destroy()

        self.reply_windows.pop(i)


    @gui_status.show_errors
    def cycle_replies(self, event):
        del event
        if self.display_window:
            tk_tools.raise_window(self.display_window)
            index, = [i for i, w in enumerate(self.reply_windows) if w.id == self.display_window.id]
            new_index = (index - 1) % len(self.reply_windows)
            self.display_window = self.reply_windows[new_index]


    @gui_status.show_errors
    def peek(self, event):
        del event
        if not self.query:
            gui_status.not_running()
            return

        pyperclip.copy(self.query.peek)
        window = gui_reply.reply(self.bus, self.query.duration, self.query.peek)
        self.reply_windows.append(window)

    @gui_status.show_errors
    def cancel(self, _):
        logging.info("Cancelling")
        query = self.query
        self.query = None
        if query:
            query.cancel()

    @gui_status.show_errors
    def about(self, _):
        gui_first_run.first_run()

    @gui_status.show_errors
    def menu(self, event):
        del event
        gui_menu.menu(self.bus, running=bool(self.query), conf=config.Config())



def ensure_settings_ready():
    conf = config.Config()
    conf.load()
    if conf.backend is None:
        gui_status.warn("No backend specified")
        gui_settings.settings()
        return False

    backend = llm.get(conf.backend)
    if backend.needs_credentials and backend.name not in conf.backend_keys:
        gui_status.warn(f"{backend.name} needs a key")
        gui_settings.settings()
        return False
    return True


def main():
    logging.basicConfig(level=logging.INFO)
    logging.info("Starting...")

    conf = config.Config()
    conf.load()
    if conf.first_run:
        gui_first_run.first_run()
        conf.first_run = False
        conf.save()

    tk_root = tk.Tk()

    tk_root.withdraw()

    tray = gui_tray.Tray(tk_root)
    tray_thread = threading.Thread(target=tray.run)
    tray_thread.daemon = True
    tray_thread.start()


    llm_runner = runner.LlmRunner(tk_root)

    bus = bus_module.Bus(tk_root)
    callbacks = TkCallbacks(tk_root, bus, tray, llm_runner)

    bus.bind("<<one_off>>", callbacks.one_off)
    bus.bind("<<quit>>", callbacks.quit)
    bus.bind("<<settings>>", callbacks.settings)
    bus.bind("<<clipboard>>", callbacks.clipboard)
    bus.bind("<<menu>>", callbacks.menu)
    bus.bind("<<peek>>", callbacks.peek)
    bus.bind("<<about>>", callbacks.about)
    bus.bind("<<cancel>>", callbacks.cancel)

    bus.bind("<<one_off_finished>>", callbacks.one_off_finished)
    bus.bind("<<clipboard_finished>>", callbacks.clipboard_finished)
    bus.bind("<<failed>>", callbacks.failed)
    bus.bind("<<close_last>>", callbacks.close_last)
    bus.bind("<<reply_closed>>", callbacks.close_reply)
    bus.bind("<<cycle_replies>>", callbacks.cycle_replies)


    with hotkeys.KeyBinder({
        "<ctrl>+<alt>+o": lambda: bus.send("<<one_off>>"),
        "<ctrl>+<alt>+c": lambda: bus.send("<<clipboard>>"),
        "<ctrl>+<alt>+m": lambda: bus.send("<<menu>>")
        }):
        tk_root.mainloop()
