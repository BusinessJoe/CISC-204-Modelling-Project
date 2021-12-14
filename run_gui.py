import tkinter as tk

from src.gui.gui import Application

root = tk.Tk()
root.title("When the editor is sus ඞ")
root.iconphoto(False, tk.PhotoImage(file="data/icons/alien.png"))
app = Application(parent=root)
app.pack()
app.mainloop()
