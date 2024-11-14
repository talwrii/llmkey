import textwrap
import tkinter as tk

from . import tk_tools
from .tk_tools import drop_args


def reply(duration, s):
    s = textwrap.fill(s, 120, replace_whitespace=False)
    s = f"This query took {duration:.1f}s.\nThis answer has been written to the clipboard.\n\n" + s

    window = tk.Tk()
    window.title("LLM reply")
    window.minsize(400, 400)

    frame = tk.Frame(window, width=600)
    frame.pack(expand=1, fill="both")

    reply = tk.Text(frame)
    reply.pack(expand=1, fill="both", padx=10, pady=10)
    reply.insert("1.0", s)
    reply.configure(state="disabled")

    ok = tk.Button(frame, takefocus=tk.YES, text="OK")
    ok.pack()

    tk_tools.bind_click(ok, window.destroy)

    window.bind("<Return>", drop_args(window.destroy))
    window.bind("<Shift-Return>", drop_args(window.destroy))
    return window


if __name__ == "__main__":
    reply(10, "This is a message").mainloop()
