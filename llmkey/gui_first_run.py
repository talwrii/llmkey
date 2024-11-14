
import tkinter as tk

from tkhtmlview import HTMLLabel

from . import tk_tools

def first_run():
    window = tk.Tk()
    window.title("LLM Key")
    frame = tk.Frame(window, borderwidth=25)
    frame.pack(expand=True, fill="both")

    l = HTMLLabel(frame, html="""
<p style="font-size:10px">
Welcome to LLM Popup.
A tool which lets you use AI everywhere on your
desktop with a single keypress. Rather than shuffling
between windows whenever you have a question.
</p>

<p style="font-size:10px">
It gives you keyboard shortcuts to:
    <ul>
  <li>Ask an AI a one off question</li>
  <li>Ask an AI about text that you have copied</li>
    </ul>
</p>

<p style="font-size:10px">
and writes the result into the clipboard for immediate pasting.
</p>

<p style="font-size:10px">
<b>Click on the "L" icon in the system tray for shortcuts.</b>
<p>


<p style="font-size:10px">
If you find this tool useful, you can:
</p>

<p>
<ul style="font-size:10px">
<li>Follow me on twitter <a href="https://x.com/readwithai">@readwithai</a></li>
<li>Read what I have to say <a href="https://readwithai.substack.com">on substack</a></li>
<li>Pay me 5 dollars on substack: <a href="https://ko-fi.com/readwithai">ko-fi.com</a></li>
</ul>
</p>

""")
    l.pack()


    ok = tk.Button(frame, takefocus=tk.YES, text="OK")
    ok.pack()
    tk_tools.bind_click(ok, window.destroy)

    return window

if __name__ == '__main__':
    first_run().mainloop()
