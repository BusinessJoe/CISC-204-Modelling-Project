import tkinter as tk
from PIL import Image, ImageTk


class Tile(tk.Frame):
    width = 128
    height = 128

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.canvas = tk.Canvas(
            self, width=self.width, height=self.height, bd=0, highlightthickness=0
        )
        self.border_image = ImageTk.PhotoImage(Image.open("data/icons/border.png"))

        self.canvas.create_image(
            self.width / 2, self.height / 2, image=self.border_image
        )

        self.add_image()

        self.canvas.pack()

    def add_image(self) -> None:
        pass

    def bind(self, *args, **kwargs):
        """Forward bind to canvas"""
        self.canvas.bind(*args, **kwargs)


class Empty(Tile):
    ...


class Alien(Tile):
    def __init__(self, parent, color: int, *args, **kwargs):
        self.color = color
        self.color_string = ["purple", "orange", "red"][color]
        super().__init__(parent, *args, **kwargs)

    def add_image(self) -> None:
        self.canvas.configure(background=self.color_string)
        self.image = ImageTk.PhotoImage(Image.open("data/icons/alien.png"))
        self.canvas.create_image(self.width / 2, self.height / 2, image=self.image)


class House(Tile):
    def __init__(self, parent, color: int, *args, **kwargs):
        self.color = color
        self.color_string = ["purple", "orange", "red"][color]
        super().__init__(parent, *args, **kwargs)

    def add_image(self) -> None:
        self.canvas.configure(bg=self.color_string)
        self.image = ImageTk.PhotoImage(Image.open("data/icons/house.png"))
        self.canvas.create_image(self.width / 2, self.height / 2, image=self.image)


class Obstacle(Tile):
    def add_image(self) -> None:
        self.image = ImageTk.PhotoImage(Image.open("data/icons/obstacle.png"))
        self.canvas.create_image(self.width / 2, self.height / 2, image=self.image)


class Rail(Tile):
    def __init__(self, parent, in_direction, out_direction, *args, **kwargs):
        self.in_direction = in_direction
        self.out_direction = out_direction
        super().__init__(parent, *args, **kwargs)

    def add_image(self) -> None:
        self.in_image = ImageTk.PhotoImage(
            self.rotate_image(
                self.in_direction, Image.open("data/icons/rail_half_in.png")
            )
        )
        self.out_image = ImageTk.PhotoImage(
            self.rotate_image(
                self.out_direction, Image.open("data/icons/rail_half_out.png")
            )
        )
        self.canvas.create_image(self.width / 2, self.height / 2, image=self.in_image)
        self.canvas.create_image(self.width / 2, self.height / 2, image=self.out_image)

    def rotate_image(self, direction, image):
        degrees = {"N": 0, "E": 270, "S": 180, "W": 90}[direction]
        return image.rotate(degrees)


class Entrance(Tile):
    def add_image(self) -> None:
        self.image = ImageTk.PhotoImage(Image.open("data/icons/entrance.png"))
        self.canvas.create_image(self.width / 2, self.height / 2, image=self.image)


class Exit(Tile):
    def add_image(self) -> None:
        self.image = ImageTk.PhotoImage(Image.open("data/icons/exit.png"))
        self.canvas.create_image(self.width / 2, self.height / 2, image=self.image)
