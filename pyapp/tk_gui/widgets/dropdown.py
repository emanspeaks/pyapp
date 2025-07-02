from tkinter import Event
from tkinter.ttk import Combobox

from ..abc import TtkWidgetMixin


class Dropdown(TtkWidgetMixin, Combobox):
    def enable(self):
        self.configure(state='readonly')

    def disable(self, emit: bool = True):
        self['values'] = ['']
        self.item_select(emit=emit)
        TtkWidgetMixin.disable(self)

    def populate(self, items: list, emit: bool = True):
        self['values'] = [''] + [str(x) for x in items]
        self.item_select(emit=emit)

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

    def clear_text_select(self, e: Event = None):
        self.selection_clear()
