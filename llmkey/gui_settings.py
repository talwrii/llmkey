import logging
import tkinter as tk

import openai
from typing import Optional as O

from . import config, errors, gui_status, llm, tk_tools
from . tk_tools import fill_menu


SETTINGS = None

def settings():
    global SETTINGS #pylint: disable=global-statement

    if SETTINGS is None:
        SETTINGS = Settings()
        SETTINGS.build()

    SETTINGS.reload()


class Settings:
    def __init__(self):
        self.window: O[tk.Tk]   = None
        self.conf: O[Conf]  = None
        self.state: O[State]   = None
        self.gui: O[Gui] = None
        self.logic: O[Logic]  = None

    def build(self):
        self.conf = config.Config()
        self.conf.load()
        self.conf.backend = self.conf.backend or llm.Backends.default

        self.window = tk.Tk()
        self.state = State(self.window)
        self.state.load(self.conf)

        self.gui = Gui(self.window, self.state)
        self.logic = Logic(window=self.window, gui=self.gui, state=self.state, conf=self.conf)
        self.gui.build()
        self.logic.bind()

    def reload(self):
        # tkraise and lift notify "settings are ready" - which is weird. Use this work around
        self.window.attributes('-topmost', 1)
        self.window.attributes('-topmost', 0)

        self.conf.load()
        self.logic.backend_changed()

class Logic:
    def __init__(self, *, window, gui, state, conf):
        self.window = window
        self.gui = gui
        self.state = state
        self.conf = conf

    def bind(self):
        tk_tools.bind_click(self.gui.ok, self.close)
        self.gui.window.bind("<Return>", self.close)
        self.gui.window.bind("<Shift-Return>", self.close)
        self.gui.window.protocol("WM_DELETE_WINDOW", self.close)

        self.gui.key_entry.bind("<KeyRelease>", self.key_changed)

        fill_menu(
            self.gui.backend_menu,
            self.state.backend_var,
            llm.Backends.backends,
            self.backend_changed)

    def backend_changed(self, *_):
        self.conf.backend = self.state.backend_var.get()
        self.conf.save()
        self.update_models()

        backend = llm.get(self.conf.backend)
        if backend.needs_credentials:
            self.gui.key_entry["state"] = "normal"
            key = self.conf.backend_keys.get(self.conf.backend, "")
            self.state.key_variable.set(key)
        else:
            self.gui.key_entry["state"] = "disabled"
            self.state.key_variable.set("NOT NEEDED")

    def update_models(self, *_):
        logging.info("Reloading models...")
        self.conf.load()

        backend = llm.get(self.conf.backend)

        try:
            models = backend.models
        except errors.NoKey:
            logging.exception("no key")
            models = ["no key provided"]
        except openai.AuthentificationError:
            logging.exception("Key is wrong")
            models = ["key is incorrect"]

        fill_menu(self.gui.model, self.state.model_var, models, self.model_changed)
        model = self.conf.backend_models.get(backend.name, backend.default_model)
        self.state.model_var.set(model)


    def key_changed(self, *_):
        if not self.assert_backend_unchanged():
            return

        self.conf.backend_keys[self.conf.backend] = self.state.key_variable.get()
        self.conf.save()
        self.update_models()


    def model_changed(self, *_):
        if not self.assert_backend_unchanged():
            return

        self.conf.backend_models[self.conf.backend] = self.state.model_var.get()
        self.conf.save()

    def close(self, *_):
        global SETTINGS #pylint: disable=global-statement
        SETTINGS = None
        self.window.destroy()

    def assert_backend_unchanged(self):
        backend = self.conf.backend
        self.conf.load()
        if self.conf.backend != backend:
            gui_status.warn("Backend changed")
            self.backend_changed()
            return False
        else:
            return True


class State:
    def __init__(self, window):
        self.backend_var = tk.StringVar(master=window)
        self.key_variable = tk.StringVar(master=window)
        self.model_var = tk.StringVar(master=window)

    def load(self, conf):
        self.backend_var.set(conf.backend)
        self.model_var.set(conf.model)


class Gui:
    def __init__(self, window, state):
        self.window = window
        self.state = state
        self.backend_menu = None
        self.key_entry = None
        self.model = None
        self.ok = None

    def build(self):
        self.window.title("LLM Key settings")

        frame = tk.Frame(self.window, borderwidth=25)
        frame.pack(fill="both", expand=True)

        row = 0
        label = tk.Label(frame, text="Shortcut to ask a one off question: CTRL-ALT-O")
        label.grid(columnspan=2)

        row += 1
        label = tk.Label(frame, text="Shortcut to run a query on the clipboard: CTRL-ALT-C")
        label.grid(columnspan=2)

        row += 1
        label = tk.Label(frame, text="Open menu: CTRL-ALT-M")
        label.grid(columnspan=2)

        row += 1
        backend_label = tk.Label(frame, text="Backend:")

        self.backend_menu = tk.OptionMenu(frame, self.state.backend_var, [])

        backend_label.grid(row=row, column=0)
        self.backend_menu.grid(row=row, column=1)

        row += 1
        key_label = tk.Label(frame, text="Key:")

        self.key_entry = tk.Entry(frame, textvariable=self.state.key_variable)

        key_label.grid(row=row, column=0)
        self.key_entry.grid(row=row, column=1)

        row += 1
        model_label = tk.Label(frame, text="Model:")

        self.model = tk.OptionMenu(frame, self.state.model_var, [])
        model_label.grid(column=0, row=row)
        self.model.grid(column=1, row=row)

        row += 1
        self.ok = tk.Button(self.window, takefocus=tk.NO, text="OK")
        self.ok.pack(side=tk.BOTTOM, pady=10)




if __name__ == "__main__":
    settings().mainloop()
