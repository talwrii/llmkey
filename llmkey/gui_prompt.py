"""

.. moduleauthor:: easygui developers and Stephen Raymond Ferg
.. default-domain:: py
.. highlight:: python

Version |release|
"""

import tkinter as tk  # python 3
import tkinter.font as tk_Font

import pyperclip

STANDARD_SELECTION_EVENTS = ["Return", "space"]
STANDARD_SELECTION_EVENTS_MOUSE = ["Enter", "Leave", "ButtonRelease-1"]

def mouse_click_handlers(callback):
    ns = {"mouse_on_button": True}

    def handler_enter(event):
        ns["mouse_on_button"] = True

    def handler_leave(event):
        ns["mouse_on_button"] = False

    def handler_button(event):
        if ns["mouse_on_button"]:
            return callback(event)

        return None

    return {"Enter": handler_enter,
            "Leave": handler_leave,
            "ButtonRelease-1": handler_button}



def textbox(msg="", title=" ", text="",
            codebox=False, callback=None, run=True, pos=None):
    """Displays a dialog box with a large, multi-line text box, and returns
    the entered text as a string. The message text is displayed in a
    proportional font and wraps.

    Parameters
    ----------
    msg : string
        text displayed in the message area (instructions...)
    title : str
        the window title
    text: str, list or tuple
        text displayed in textAreas (editable)
    codebox: bool
        if True, don't wrap and width is set to 80 chars
    callback: function
        if set, this function will be called when OK is pressed
    run: bool
        if True, a box object will be created and returned, but not run

    Returns
    -------
    None
        If cancel is pressed
    str
        If OK is pressed returns the contents of textArea

    """

    tb = TextBox(msg=msg, title=title, text=text,
                 codebox=codebox, callback=callback, pos=pos)
    if not run:
        return tb
    else:
        reply = tb.run()
        return reply


class TextBox(object):

    """ Display a message and a text to edit

    This object separates user from ui, defines which methods can
    the user invoke and which properties can he change.

    It also calls the ui in defined ways, so if other gui
    library can be used (wx, qt) without breaking anything for the user.
    """

    def __init__(self, msg, title, text, codebox, pos=None, callback=lambda *args, **kwargs: True):
        """ Create box object

        Parameters
        ----------
        msg : string
            text displayed in the message area (instructions...)
        title : str
            the window title
        text: str, list or tuple
            text displayed in textAres (editable)
        codebox: bool
            if True, don't wrap and width is set to 80 chars
        callback: function
            if set, this function will be called when OK is pressed

        Returns
        -------
        object
            The box object
        """

        self.callback = callback
        self.ui = GUItk(msg, title, text, codebox, self.callback_ui)
        self.text = text
        if pos:
            self.ui.textArea.mark_set("insert", pos)

    def run(self):
        """ Start the ui """
        self.ui.run()
        self.ui = None
        return self._text

    def stop(self):
        """ Stop the ui """
        self.ui.stop()

    def callback_ui(self, ui, command, text):
        """ This method is executed when ok, cancel, or x is pressed in the ui.
        """
        if command == 'update':  # OK was pressed
            self._text = text
            if self.callback:
                # If a callback was set, call main process
                self.callback(self)
            else:
                self.stop()
        elif command == 'x':
            self.stop()
            self._text = None
        elif command == 'cancel':
            self.stop()
            self._text = None

    # methods to change properties --------------
    @property
    def text(self):
        """Text in text Area"""
        return self._text

    @text.setter
    def text(self, text):
        self._text = self.to_string(text)
        self.ui.set_text(self._text)

    @text.deleter
    def text(self):
        self._text = ""
        self.ui.set_text(self._text)

    @property
    def msg(self):
        """Text in msg Area"""
        return self._msg

    @msg.setter
    def msg(self, msg):
        self._msg = self.to_string(msg)
        self.ui.set_msg(self._msg)

    @msg.deleter
    def msg(self):
        self._msg = ""
        self.ui.set_msg(self._msg)

    # Methods to validate what will be sent to ui ---------

    def to_string(self, something):
        try:
            basestring  # python 2
        except NameError:
            basestring = str  # Python 3

        if isinstance(something, basestring):
            return something
        try:
            text = "".join(something)  # convert a list or a tuple to a string
        except:
            textbox(
                "Exception when trying to convert {} to text in self.textArea"
                .format(type(something)))
            sys.exit(16)
        return text


class GUItk(object):

    """ This is the object that contains the tk root object"""

    def __init__(self, msg, title, text, codebox, callback):
        """ Create ui object

        Parameters
        ----------
        msg : string
            text displayed in the message area (instructions...)
        title : str
            the window title
        text: str, list or tuple
            text displayed in textAres (editable)
        codebox: bool
            if True, don't wrap, and width is set to 80 chars
        callback: function
            if set, this function will be called when OK is pressed

        Returns
        -------
        object
            The ui object
        """

        self.callback = callback

        self.boxRoot = tk.Tk()
        # self.boxFont = tk_Font.Font(
        #     family=global_state.PROPORTIONAL_FONT_FAMILY,
        #     size=global_state.PROPORTIONAL_FONT_SIZE)

        wrap_text = not codebox
        if wrap_text:
            self.boxFont = tk_Font.nametofont("TkTextFont")
            self.width_in_chars = 120
        else:
            self.boxFont = tk_Font.nametofont("TkFixedFont")
            self.width_in_chars = 120

        # default_font.configure(size=global_state.PROPORTIONAL_FONT_SIZE)

        self.configure_root(title)

        self.create_msg_widget(msg)

        self.create_text_area(wrap_text)

        self.create_buttons_frame()

        self.create_cancel_button()

        self.create_ok_button()

    # Run and stop methods ---------------------------------------

    def run(self):
        self.boxRoot.mainloop()
        self.boxRoot.destroy()

    def stop(self):
        # Get the current position before quitting
        self.get_pos()
        self.boxRoot.quit()

    # Methods to change content ---------------------------------------

    def set_msg(self, msg):
        self.messageArea.config(state=tk.NORMAL)
        self.messageArea.delete(1.0, tk.END)
        self.messageArea.insert(tk.END, msg)
        self.messageArea.config(state=tk.DISABLED)
        # Adjust msg height
        self.messageArea.update()
        numlines = self.get_num_lines(self.messageArea)
        self.set_msg_height(numlines)
        self.messageArea.update()

    def set_msg_height(self, numlines):
        self.messageArea.configure(height=numlines)

    def get_num_lines(self, widget):
        end_position = widget.index(tk.END)  # '4.0'
        end_line = end_position.split('.')[0]  # 4
        return int(end_line)  # 5

    def set_text(self, text):
        self.textArea.delete(1.0, tk.END)
        self.textArea.insert(tk.END, text, "normal")
        self.textArea.focus()

    def set_pos(self, pos):
        self.boxRoot.geometry(pos)

    def get_pos(self):
        # The geometry() method sets a size for the window and positions it on
        # the screen. The first two parameters are width and height of
        # the window. The last two parameters are x and y screen coordinates.
        # geometry("250x150+300+300")
        geom = self.boxRoot.geometry()  # "628x672+300+200"

    def get_text(self):
        return self.textArea.get(0.0, 'end-1c')

    # Methods executing when a key is pressed -------------------------------
    def x_pressed(self):
        self.callback(self, command='x', text=self.get_text())

    def cancel_pressed(self, event):
        self.callback(self, command='cancel', text=self.get_text())

    def ok_button_pressed(self, event):
        self.callback(self, command='update', text=self.get_text())

    # Auxiliary methods -----------------------------------------------
    def calc_character_width(self):
        char_width = self.boxFont.measure('W')
        return char_width

    # Initial configuration methods ---------------------------------------
    # These ones are just called once, at setting.

    def configure_root(self, title):

        self.boxRoot.title(title)

        # self.set_pos()

        # Quit when x button pressed
        self.boxRoot.protocol('WM_DELETE_WINDOW', self.x_pressed)
        self.boxRoot.bind("<Escape>", self.cancel_pressed)
        self.boxRoot.bind("<Control-g>", self.cancel_pressed)

        self.boxRoot.iconname('Dialog')

        self.boxRoot.attributes("-topmost", True)  # Put the dialog box in focus.

    def create_msg_widget(self, msg):

        if msg is None:
            msg = ""

        self.msgFrame = tk.Frame(
            self.boxRoot,
            padx=1.25 * self.calc_character_width(),
        )
        self.messageArea = tk.Text(
            self.msgFrame,
            width=self.width_in_chars,
            state=tk.DISABLED,
            padx=7 * self.calc_character_width(),
            pady=self.calc_character_width(),
            wrap=tk.WORD
        )
        self.set_msg(msg)

        self.msgFrame.pack(fill='x')

        self.messageArea.pack(fill='x')

    def create_text_area(self, wrap_text):
        """
        Put a textArea in the top frame
        Put and configure scrollbars
        """

        self.textFrame = tk.Frame(
            self.boxRoot,
            padx=1.25 * self.calc_character_width(),
        )

        self.textFrame.pack(side=tk.TOP)
        # self.textFrame.grid(row=1, column=0, sticky=tk.EW)

        self.textArea = tk.Text(
            self.textFrame,
            padx= 8 * self.calc_character_width(),
            pady= 8 * self.calc_character_width(),
            height=25,  # lines. Note: a user-set arg would be preferable to hardcoded value
            width=self.width_in_chars,   # chars of the current font
        )

        if wrap_text:
            self.textArea.configure(wrap=tk.WORD)
        else:
            self.textArea.configure(wrap=tk.NONE)

        # some simple keybindings for scrolling
        self.boxRoot.bind("<Next>", self.textArea.yview_scroll(1, tk.PAGES))
        self.boxRoot.bind(
            "<Prior>", self.textArea.yview_scroll(-1, tk.PAGES))

        self.boxRoot.bind("<Right>", self.textArea.xview_scroll(1, tk.PAGES))
        self.boxRoot.bind("<Left>", self.textArea.xview_scroll(-1, tk.PAGES))

        self.boxRoot.bind("<Down>", self.textArea.yview_scroll(1, tk.UNITS))
        self.boxRoot.bind("<Up>", self.textArea.yview_scroll(-1, tk.UNITS))

        self.textArea.bind("<Shift-Return>", self.ok_button_pressed)

        # add a vertical scrollbar to the frame
        rightScrollbar = tk.Scrollbar(
            self.textFrame, orient=tk.VERTICAL, command=self.textArea.yview)
        self.textArea.configure(yscrollcommand=rightScrollbar.set)

        # add a horizontal scrollbar to the frame
        bottomScrollbar = tk.Scrollbar(
            self.textFrame, orient=tk.HORIZONTAL, command=self.textArea.xview)
        self.textArea.configure(xscrollcommand=bottomScrollbar.set)

        # pack the textArea and the scrollbars.  Note that although
        # we must define the textArea first, we must pack it last,
        # so that the bottomScrollbar will be located properly.

        # Note that we need a bottom scrollbar only for code.
        # Text will be displayed with wordwrap, so we don't need to have
        # a horizontal scroll for it.

        if not wrap_text:
            bottomScrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        rightScrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.textArea.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.YES)

    def create_buttons_frame(self):

        self.buttonsFrame = tk.Frame(self.boxRoot)
        self.buttonsFrame.pack(side=tk.TOP)

    def create_cancel_button(self):
        # put the buttons in the buttonsFrame
        self.cancelButton = tk.Button(
            self.buttonsFrame, takefocus=tk.YES, text="Cancel",
            height=1, width=6)
        self.cancelButton.pack(
            expand=tk.NO, side=tk.LEFT, padx='2m', pady='1m', ipady="1m",
            ipadx="2m")

        # for the commandButton, bind activation events to the activation event
        # handler
        self.cancelButton.bind("<Escape>", self.cancel_pressed)
        mouse_handlers = mouse_click_handlers(self.cancel_pressed)
        for selectionEvent in STANDARD_SELECTION_EVENTS_MOUSE:
            self.cancelButton.bind("<%s>" % selectionEvent, mouse_handlers[selectionEvent])

    def create_ok_button(self):
        # put the buttons in the buttonsFrame
        self.okButton = tk.Button(
            self.buttonsFrame, takefocus=tk.YES, text="OK", height=1, width=6)
        self.okButton.pack(
            expand=tk.NO, side=tk.LEFT, padx='2m', pady='1m', ipady="1m",
            ipadx="2m")

        # for the commandButton, bind activation events to the activation event
        # handler
        self.okButton.bind("<Return>", self.ok_button_pressed)
        mouse_handlers = mouse_click_handlers(self.ok_button_pressed)
        for selectionEvent in STANDARD_SELECTION_EVENTS_MOUSE:
            self.okButton.bind("<%s>" % selectionEvent, mouse_handlers[selectionEvent])

def prompt_one_off(backend, model):
    title = "One-off LLM Prompt"
    text = ""
    msg = \
f"""Using {model} on {backend}

Enter a one-off LLM prompt then press shift-enter.
Esc to cancel.
"""
    return textbox(msg, title, text)


def prompt_clipboard():
    title = "Clipboard one-off LLM Prompt"
    text = "\n\n" + pyperclip.paste()
    msg = "Type a command to run against the clipboard"
    return textbox(msg, title, text, pos="1.0")


if __name__ == '__main__':
    prompt_one_off("MODEL")