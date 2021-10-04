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
        self.tile_settings = TileSettings(
            self, handle_import=self._handle_import, handle_export=self._handle_export
        )
        self.tile_settings.pack(side=tk.RIGHT)

        self.grid_display = GridDisplay(
            self, create_tile=self._create_tile, size=(5, 5)
        )
        self.grid_display.pack(side=tk.LEFT)

    def _handle_import(self):
        f = filedialog.askopenfile(
            mode="r", filetypes=[("XML FIles", ".xml")], defaultextension=".xml"
        )
        if f is None:
            return
        xml = f.read()
        print(xml)
        data = xml_parser.import_xml(xml)
        print(data)
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
