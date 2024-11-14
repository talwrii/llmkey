import logging
import threading
import tkinter as tk

import keybind
import pyperclip


from . import (gui_first_run, gui_menu, gui_prompt, gui_reply, gui_settings,
               gui_status, gui_tray, llm, runner, tk_tools, config, gui_first_run)

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
    def __init__(self, root, tray, llm_runner):
        self.root = root
        self.tray = tray
        self.llm_runner = llm_runner
        self.query = None

    @staticmethod
    @gui_status.show_errors
    def settings(_):
        gui_settings.settings()

    @gui_status.show_errors
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
            gui_reply.reply(self.query.duration, event.data)
            self.query = None

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
            gui_reply.reply(self.query.duration, event.data)
            self.query = None

    @gui_status.show_errors
    def failed(self, event):
        self.query = None
        gui_status.failed(event.data)

    @gui_status.show_errors
    def peek(self, event):
        del event
        if not self.query:
            gui_status.not_running()
            return

        pyperclip.copy(self.query.peek)
        gui_reply.reply(self.query.duration, self.query.peek)

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
        gui_menu.menu(self.root, running=bool(self.query), conf=config.Config())



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

    keybind.KeyBinder.activate({
        "Ctrl-Alt-O": lambda: tk_root.event_generate("<<one_off>>"),
        "Ctrl-Alt-C": lambda: tk_root.event_generate("<<clipboard>>"),
        "Ctrl-Alt-M": lambda: tk_root.event_generate("<<menu>>")
        }, run_thread=True)

    tray = gui_tray.Tray(tk_root)

    tray_thread = threading.Thread(target=tray.run)
    tray_thread.daemon = True
    tray_thread.start()

    llm_runner = runner.LlmRunner(tk_root)

    callbacks = TkCallbacks(tk_root, tray, llm_runner)
    tk_tools.my_bind(tk_root, "<<settings>>", callbacks.settings)
    tk_tools.my_bind(tk_root, "<<quit>>", callbacks.quit)
    tk_tools.my_bind(tk_root, "<<one_off>>", callbacks.one_off)
    tk_tools.my_bind(tk_root, "<<one_off_finished>>", callbacks.one_off_finished)
    tk_tools.my_bind(tk_root, "<<clipboard>>", callbacks.clipboard)
    tk_tools.my_bind(tk_root, "<<clipboard_finished>>", callbacks.clipboard_finished)
    tk_tools.my_bind(tk_root, "<<menu>>", callbacks.menu)
    tk_tools.my_bind(tk_root, "<<cancel>>", callbacks.cancel)
    tk_tools.my_bind(tk_root, "<<failed>>", callbacks.failed)
    tk_tools.my_bind(tk_root, "<<peek>>", callbacks.peek)
    tk_tools.my_bind(tk_root, "<<about>>", callbacks.about)

    tk_root.mainloop()
