import tkinter as tk

from src.gui.page import Page
from src.gui.tiles import Alien, Empty, Entrance, Exit, House, Obstacle, Rail


class TileSettings(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.tile_type_string = tk.StringVar()

        self.tile_options = {
            "alien": Alien,
            "house": House,
            "obstacle": Obstacle,
            "rail": Rail,
            "entrance": Entrance,
            "exit": Exit,
            "empty": Empty,
        }

        self.tile_type_string.set("alien")

        for option in self.tile_options:
            r = tk.Radiobutton(
                self,
                text=option.title(),
                variable=self.tile_type_string,
                value=option,
                command=self.handle_click,
            )
            r.pack(anchor=tk.N)

        self.page = Page(
            self,
            {
                "alien": AlienSettings(self),
                "house": AlienSettings(self),
                "rail": RailSettings(self),
            },
            default="alien",
            width=150,
        )
        self.page.pack()

    def handle_click(self):
        self.page.select(self.tile_type_string.get())

    def get_tile(self, parent):
        cls = self.tile_options[self.tile_type_string.get()]
        if self.page.display_widget:
            args, kwargs = self.page.display_widget.get_args_and_kwargs()
        else:
            args, kwargs = tuple(), dict()

        tile = cls(parent, *args, **kwargs)
        return tile


class TileSpecificSettings(tk.Frame):
    def get_args_and_kwargs(self):
        return tuple(), dict()


class AlienSettings(TileSpecificSettings):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.color = tk.StringVar()
        self.color.set("0")

        tk.Label(self, text="Color").grid(row=0, column=0)
        self.entry = tk.Entry(self, textvariable=self.color)
        self.entry.grid(row=0, column=1)

    def get_args_and_kwargs(self):
        return tuple(), {"color": int(self.color.get())}


class RailSettings(TileSpecificSettings):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.in_direction = tk.StringVar()
        self.in_direction.set("N")

        self.out_direction = tk.StringVar()
        self.out_direction.set("S")

        tk.Label(self, text="In direction").grid(row=0, column=0)
        tk.Label(self, text="Out direction").grid(row=1, column=0)
        self.in_entry = tk.Entry(self, textvariable=self.in_direction)
        self.out_entry = tk.Entry(self, textvariable=self.out_direction)

        self.in_entry.grid(row=0, column=1)
        self.out_entry.grid(row=1, column=1)

    def get_args_and_kwargs(self):
        return tuple(), {
            "in_direction": self.in_direction.get(),
            "out_direction": self.out_direction.get(),
        }
