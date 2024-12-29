import time

def bind_click(button, callback):
    "Bind a click event for a button"
    state = {"mouse_on_button": True}

    def handle_enter(_):
        state["mouse_on_button"] = True

    def handle_leave(_):
        state["mouse_on_button"] = False

    def handle_click(_):
        if state["mouse_on_button"]:
            return callback()

        return None

    button.bind("<Enter>", handle_enter)
    button.bind("<Leave>", handle_leave)
    button.bind("<ButtonRelease-1>", handle_click)


def drop_args(f):
    def inner(*_):
        return f()
    return inner

def my_bind(widget, sequence, func):
    # Hack to include data
    # https://stackoverflow.com/questions/16369947/python-tkinterhow-can-i-fetch-the-value-of-data-which-was-set-in-function-eve
    def _substitute(*args):
        e = lambda: None #simplest object with __dict__
        e.data = args[0]
        e.widget = widget
        return (e,)

    funcid = widget._register(func, _substitute, needcleanup=1) #pylint: disable=protected-access
    cmd = 'if {{"[{} %d]" == "break"}} break\n'.format(funcid)
    widget.tk.call('bind', widget._w, sequence, cmd) #pylint: disable=protected-access


def fill_menu(menu, var, new: list[str], callback):
    "Populate a dropdown menu with new."
    options = menu["menu"]
    options.delete(0, "end")

    # Add new options
    for option in new:
        def make_callback(option):
            def cb():
                var.set(option)
                callback()
            return cb

        options.add_command(label=option, command=make_callback(option))



def raise_window(window):
    # tkraise and lift notify "settings are ready" - which is weird. Use this work around
    # https://stackoverflow.com/questions/1892339/how-to-make-a-tkinter-window-jump-to-the-front
    window.lift()
    window.attributes('-topmost',True)
    window.after_idle(window.attributes,'-topmost',False)
