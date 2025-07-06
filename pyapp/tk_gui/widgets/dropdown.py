from tkinter import Event
from tkinter.ttk import Combobox

from ...logging import log_func_call
from ..abc import TtkWidgetMixin


class Dropdown(TtkWidgetMixin, Combobox):
    @log_func_call
    def enable(self):
        self.configure(state='readonly')

    @log_func_call
    def disable(self, emit: bool = True):
        self['values'] = ['']
        self.item_select(emit=emit)
        TtkWidgetMixin.disable(self)

    @log_func_call
    def populate(self, items: list, emit: bool = True):
        self['values'] = [''] + [str(x) for x in items]
        self.item_select(emit=emit)

    @log_func_call
    def item_select(self, item: str | int = 0, emit: bool = True,
                    clear_select: bool = True):
        if isinstance(item, int):
            self.current(item)

        else:
            self.set(item)

        if emit:
            self.event_generate("<<ComboboxSelected>>")

        elif clear_select:
            self.clear_text_select()

    @log_func_call
    def clear_text_select(self, e: Event = None):
        self.selection_clear()
