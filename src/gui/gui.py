import tkinter as tk
import tkinter.filedialog as filedialog
from src import xml_parser

from src.gui.grid import GridDisplay
from src.gui.tile_settings import TileSettings
from src.gui.tiles import Rail


class Application(tk.Frame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.pack()
        self.create_widgets()

    def create_widgets(self):
        self.grid_display = GridDisplay(
            self, create_tile=self._create_tile, size=(5, 5)
        )
        self.grid_display.pack(side=tk.LEFT)

        right_panel = tk.Frame(self)
        right_panel.pack(side=tk.RIGHT)

        self.rows_entry = tk.Entry(right_panel)
        self.cols_entry = tk.Entry(right_panel)
        set_size_button = tk.Button(
            right_panel, text="Set Size", command=self._handle_set_size
        )
        self.rows_entry.pack()
        self.cols_entry.pack()
        set_size_button.pack()

        self.tile_settings = TileSettings(
            right_panel,
        )
        self.tile_settings.pack()

        import_ = tk.Button(right_panel, text="Import", command=self._handle_import)
        import_.pack()
        export = tk.Button(right_panel, text="Export", command=self._handle_export)
        export.pack()

    def _handle_set_size(self):
        size = int(self.rows_entry.get()), int(self.cols_entry.get())
        self.grid_display.set_grid_size(size)

    def _handle_import(self):
        f = filedialog.askopenfile(
            mode="r", filetypes=[("XML FIles", ".xml")], defaultextension=".xml"
        )
        if f is None:
            return
        xml = f.read()
        data = xml_parser.import_xml(xml)
        self.grid_display.import_(**data)
        f.close()

    def _handle_export(self):
        f = filedialog.asksaveasfile(
            mode="w", filetypes=[("XML FIles", ".xml")], defaultextension=".xml"
        )
        if f is None:
            return
        xml = self.grid_display.export()
        f.write(xml)
        f.close()

    def _create_tile(self, parent):
        return self.tile_settings.get_tile(parent)
