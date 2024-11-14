import tkinter as tk
import traceback
from typing import Callable, ParamSpec, TypeVar

from . import tk_tools
from .tk_tools import drop_args


def private_status_window(title, text):
    window = tk.Tk()
    window.title(title)
    window.geometry("400x200")

    text = text + "\n\nPress Enter or q to close."

    tk.Label(window, text=text).pack(padx=10, pady=10)

    ok = tk.Button(window, takefocus=tk.YES, text="OK")
    ok.pack(padx=10, pady=10)

    tk_tools.bind_click(ok, window.destroy)

    window.bind("<Return>", drop_args(window.destroy))
    window.bind("<Shift-Return>", drop_args(window.destroy))
    window.bind("q", drop_args(window.destroy))

    return window


def running(count, duration):
    return private_status_window(
        "LLM already running",
        f"A query is already running.\n{count} bytes in {duration:.1f}s")


def not_running():
    return private_status_window("LLM is not running",
                          "No query is running")

def warn(s):
    return private_status_window("Warning", s)

def error(s):
    return private_status_window("Error", s)

def failed(message):
    return private_status_window("LLM query failed", f"The query failed: {message}")

P = ParamSpec("P")
T = TypeVar("T")

def show_errors(f: Callable[P, T]) -> Callable[P, T]:
    def inner(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception:
            err = traceback.format_exc()
            error(err)
            raise
    return inner

if __name__ == '__main__':
    running().mainloop()
