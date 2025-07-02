from tkinter import END as tkEND
from tkinter.ttk import Entry as TtkEntry

from ..abc import TtkWidgetMixin


class Entry(TtkWidgetMixin, TtkEntry):
    def clear(self):
        self.delete(0, tkEND)

    def set_text(self, text: str):
        self.insert(tkEND, text)

    def set_and_lock_text(self, text: str):
        self.enable()
        self.clear()
        self.set_text(text)
        self.disable()
