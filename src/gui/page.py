import tkinter as tk
from typing import Any, Optional


class Page(tk.Frame):
    def __init__(
        self,
        parent,
        widgets: dict[str, tk.Widget],
        default: Optional[str] = None,
        *args,
        **kwargs
    ):
        super().__init__(parent, *args, **kwargs)
        self.widgets = widgets
        self.select(default)

    def select(self, widget: Optional[str]):
        self.display_widget = self.widgets.get(widget)

        for w in self.widgets.values():
            w.pack_forget()

        if self.display_widget:
            self.display_widget.pack()
