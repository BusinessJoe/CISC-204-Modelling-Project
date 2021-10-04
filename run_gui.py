import tkinter as tk

from src.gui.grid import GridDisplay
from src.gui.gui import Application
from src.gui.tiles import Rail

root = tk.Tk()
app = Application(parent=root)
app.pack()
app.mainloop()
