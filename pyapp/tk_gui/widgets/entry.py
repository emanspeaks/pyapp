from tkinter import END as tkEND
from tkinter.ttk import Entry as TtkEntry

from ...logging import log_func_call
from ..abc import TtkWidgetMixin


class Entry(TtkWidgetMixin, TtkEntry):
    @log_func_call
    def clear(self):
        self.delete(0, tkEND)

    @log_func_call
    def set_text(self, text: str):
        self.insert(tkEND, text)

    @log_func_call
    def set_and_lock_text(self, text: str):
        self.enable()
        self.clear()
        self.set_text(text)
        self.disable()
