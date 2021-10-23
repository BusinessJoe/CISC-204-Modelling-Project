import tkinter as tk
from tkinter.messagebox import showerror
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
        self.grid_display.pack(side=tk.LEFT, padx=20, pady=20)

        right_panel = tk.Frame(self)
        right_panel.pack(side=tk.RIGHT)

        size_panel = tk.Frame(right_panel)
        size_panel.pack(padx=(0, 20), pady=20)

        tk.Label(size_panel, text="Rows").grid(row=0, column=0)
        tk.Label(size_panel, text="Cols").grid(row=1, column=0)
        self.rows_entry = tk.Entry(size_panel)
        self.cols_entry = tk.Entry(size_panel)
        set_size_button = tk.Button(
            size_panel, text="Set Size", command=self._handle_set_size
        )
        self.rows_entry.grid(row=0, column=1)
        self.cols_entry.grid(row=1, column=1)
        set_size_button.grid(row=2, column=0, columnspan=2)

        self.tile_settings = TileSettings(
            right_panel,
        )
        self.tile_settings.pack()

        file_frame = tk.Frame(right_panel)
        import_ = tk.Button(file_frame, text="Import", command=self._handle_import)
        import_.grid(row=0, column=0)
        export = tk.Button(file_frame, text="Export", command=self._handle_export)
        export.grid(row=0, column=1)
        file_frame.pack(pady=(30, 10))

    def _handle_set_size(self):
        size = int(self.rows_entry.get()), int(self.cols_entry.get())
        self.grid_display.set_grid_size(size)

    def _handle_import(self):
        try:
            f = filedialog.askopenfile(
                mode="r", filetypes=[("XML FIles", ".xml")], defaultextension=".xml"
            )
            if f is None:
                return
            xml = f.read()
            data = xml_parser.import_xml(xml)
            self.grid_display.import_(**data)
            f.close()
        except Exception as e:
            showerror("Error", str(e))
            raise

    def _handle_export(self):
        try:
            f = filedialog.asksaveasfile(
                mode="w", filetypes=[("XML FIles", ".xml")], defaultextension=".xml"
            )
            if f is None:
                return
            xml = self.grid_display.export()
            f.write(xml)
            f.close()
        except Exception as e:
            showerror("Error", str(e))
            raise

    def _create_tile(self, parent):
        return self.tile_settings.get_tile(parent)
