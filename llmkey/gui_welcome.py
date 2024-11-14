
import tkinter as tk

TEXT = """

This is LLM Popup. A desktop integration of LLMs designed for linux.

It focuses on integration rather than being a separate app.

To configure and control click on the "L" icon in the system tray. This will remind you of shortcuts.


"""

def welcome():
    window = tk.Tk()
    window.title("About LLMPopup")


    label = tk.Label(window, text=TEXT)
    label.pack()

    return window



if __name__ == '__main__':
    welcome().mainloop()
