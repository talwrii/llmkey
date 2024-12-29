import tkinter as tk

from . import tk_tools, llm, gui_settings
from .gui_status import show_errors

def menu(bus, running, conf):
    #pylint: disable=too-many-locals,too-many-statements
    conf.load()
    window = tk.Tk()
    window.title("LLM Popup")

    frame = tk.Frame(window, borderwidth=25)
    frame.pack(fill="both", expand=True)

    @show_errors
    def cancel(_):
        bus.send("<<cancel>>")
        window.destroy()

    tk.Label(frame, text="Running..." if running else "No query running").pack(anchor="w")

    b = tk.Button(frame, text="Cancel current query (x)")
    b.pack(fill="both")
    tk_tools.bind_click(b, cancel)
    window.bind("c", cancel)

    @show_errors
    def peek(_):
        bus.send("<<peek>>")
        window.destroy()
    p = tk.Button(frame, text="Peek at the results so far (p)")
    p.pack(fill="both")
    tk_tools.bind_click(p, peek)
    window.bind("p", peek)

    @show_errors
    def show_window(_):
        bus.send("<<cycle_replies>>")
        window.destroy()
    p = tk.Button(frame, text="Cycle/show result windows (w)")
    p.pack(fill="both")
    tk_tools.bind_click(p, show_window)
    window.bind("w", show_window)

    @show_errors
    def close_last(_):
        print("close last called")
        bus.send("<<close_last>>")
        window.destroy()
    p = tk.Button(frame, text="Close the last window (d)")
    p.pack(fill="both")
    tk_tools.bind_click(p, close_last)
    window.bind("d", close_last)

    @show_errors
    def change_backend(*_):
        conf.load()
        conf.backend = llm.Backends.next(conf.backend or "openai")
        conf.save()
        backend_label["text"] = format_backend()
        update_model()

    def update_model():
        model_label["text"] = "Model: " + get_model(conf)

    @show_errors
    def format_backend():
        return f"Backend: {conf.backend}"

    label_frame = tk.Frame(frame)
    label_frame.pack(fill="both", expand=True)
    backend_label = tk.Label(label_frame, text=format_backend())
    b = tk.Button(label_frame, text="Change backend (b)")
    b.grid(row=0, column=0)
    backend_label.grid(row=0, column=1)
    tk_tools.bind_click(b, change_backend)
    window.bind("b", change_backend)

    @show_errors
    def change_model(*_):
        conf.load()
        backend = get_backend(conf)
        model = backend.next_model(get_model(conf))
        print("Setting model to", model)
        conf.backend_models[backend.name] = model
        conf.save()
        update_model()
    model_label = tk.Label(label_frame)
    m = tk.Button(label_frame, text="Change model (m)")
    m.grid(row=1, column=0)
    model_label.grid(row=1, column=1)
    tk_tools.bind_click(p, change_model)
    window.bind("m", change_model)
    update_model()

    window.bind("<Return>", lambda _: window.destroy())
    window.bind("<Shift-Return>", lambda _: window.destroy())

    @show_errors
    def settings(*_):
        gui_settings.settings()
        window.destroy()

    b = tk.Button(frame, text="Settings (s)")
    b.pack(fill="both")
    tk_tools.bind_click(b, settings)
    window.bind("s", settings)

    @show_errors
    def quit_app(*_):
        root.event_generate("<<quit>>")
    b = tk.Button(frame, text="Quit app (Q)")
    b.pack(fill="both")
    tk_tools.bind_click(b, quit_app)
    window.bind("Q", quit_app)

    b = tk.Button(frame, text="Quit menu (q)")
    b.pack(fill="both")
    tk_tools.bind_click(b, lambda *_: window.destroy())
    window.bind("q", lambda _: window.destroy())

    ok_button_frame = tk.Frame(frame)
    ok_button_frame.pack(fill="both", expand=True)
    ok = tk.Button(ok_button_frame, takefocus=tk.YES, text="OK")
    ok.pack(side=tk.LEFT, pady=10, padx=10)
    tk_tools.bind_click(ok, lambda *_: window.destroy())

def get_model(conf):
    backend = get_backend(conf)
    return conf.backend_models.get(backend.name, backend.default_model)

def get_backend(conf):
    return llm.get(conf.backend or "openai")

if __name__ == '__main__':
    from . import config
    from . import bus
    def main():
        root = tk.Tk()
        root.withdraw()

        conf = {}
        store = config.mock_config(conf)
        bus = bus.MockBus()
        menu(bus, False, store)
        root.mainloop()

    main()
