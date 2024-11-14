import threading
import logging
import traceback

class LlmRunner:
    "Single threaded worker to run queries"

    def __init__(self, tk_root):
        self.tk_root = tk_root
        self.thread = None

    @property
    def running(self):
        return self.thread is not None

    def run(self, f, event):
        def wrapped():
            try:
                result = f()
            except Exception: #pylint: disable=broad-except
                logging.exception("LLM command failed")
                message = traceback.format_exc()
                self.tk_root.event_generate("<<failed>>", data=message)
                self.thread = None
            else:
                self.thread = None
                self.tk_root.event_generate(event, data=result)


        if not self.thread:
            self.thread = threading.Thread(target=wrapped)
            self.thread.daemon = True
            self.thread.start()
            return True
        else:
            return False
