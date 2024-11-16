import pathlib

import pystray
from pystray import MenuItem
import PIL.Image
import tkinter as tk

HERE = (pathlib.Path(__file__) / "..").resolve()

class Tray:
    def __init__(self, tk_root:tk.Tk):
        self.tk_root = tk_root
        self._icon = None
        self.status = "No query Running"
        self._menu = None

    def set_status(self, s):
        self.status = s
        self._icon.update_menu()

    def run(self):
        image = PIL.Image.open(HERE / "icon.ico")

        def status(*_, **__):
            # only called with update_status
            return self.status

        menu = (
            MenuItem(status, lambda: None),
            MenuItem('Ctrl-Alt-O runs a one-off query', lambda: None),
            MenuItem('Ctrl-Alt-C runs a one-off query on what is in the clipboard', lambda: None),
            MenuItem('Ctrl-Alt-M opens a menu of other commands with keybindings', lambda: None),
            MenuItem('About', lambda: self.send_event("<<about>>")),
            MenuItem('Settings', lambda: self.send_event("<<settings>>")),
            MenuItem('Quit', lambda: self.send_event("<<quit>>")))
        self._icon = pystray.Icon("name", image, "My System Tray Icon", menu)
        self._icon.run()

    def send_event(self, event):
        self.tk_root.event_generate(event)
