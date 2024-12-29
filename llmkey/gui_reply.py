import textwrap
import tkinter as tk
import uuid

from . import tk_tools

def reply(bus, duration, s):
    s = textwrap.fill(s, 120, replace_whitespace=False)
    s = f"This query took {duration:.1f}s.\nThis answer has been written to the clipboard.\n\n" + s

    window = tk.Tk()
    window.closed = False
    window.id = str(uuid.uuid4())
    window.title("LLM reply")
    window.minsize(400, 400)

    frame = tk.Frame(window, width=600)
    frame.pack(expand=1, fill="both")

    reply_text = tk.Text(frame)
    reply_text.pack(expand=1, fill="both", padx=10, pady=10)
    reply_text.insert("1.0", s)
    reply_text.configure(state="disabled")

    ok = tk.Button(frame, takefocus=tk.YES, text="OK")
    ok.pack()

    def destroy(*_):
        bus.send("<<reply_closed>>", data=dict(id=window.id))
        window.closed = True
        window.destroy()

    tk_tools.bind_click(ok, destroy)
    window.bind("<Return>", destroy)
    window.bind("<Shift-Return>", destroy)
    return window


if __name__ == "__main__":
    def main():
        from . import bus
        reply(bus.MockBus(), 10, "This is a message").mainloop()
    main()
