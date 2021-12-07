import tkinter as tk
from PIL import Image, ImageTk
import numpy as np


COLORS = [
    "#c71111",
    "#132fd2",
    "#10802d",
    "#ee55ba",
    "#f17d0e",
    "#f6f757",
    "#3f484e",
    "#d6e1f0",
    "#6b30bc",
    "#72491c",
]


def hex2rgb(hexcode):
    hexcode = hexcode[1:]
    r = int(hexcode[:2], 16)
    g = int(hexcode[2:4], 16)
    b = int(hexcode[4:6], 16)
    return r, g, b


def _recolor_image(im, to_change, result, tolerance=0):
    if isinstance(to_change, str):
        to_change = hex2rgb(to_change)
    if isinstance(result, str):
        result = hex2rgb(result)

    im = im.convert("RGBA")

    data = np.array(im)  # "data" is a height x width x 4 numpy array
    red, green, blue, alpha = data.T  # Temporarily unpack the bands for readability

    # Replace white with red... (leaves alpha values alone...)
    areas = (
        np.isclose(red, np.full(red.shape, to_change[0]), atol=tolerance)
        & np.isclose(green, np.full(green.shape, to_change[1]), atol=tolerance)
        & np.isclose(blue, np.full(blue.shape, to_change[2]), atol=tolerance)
    )

    data[..., :-1][areas.T] = result  # Transpose back needed

    im2 = Image.fromarray(data)
    return im2


class Tile(tk.Frame):
    width = 128 // 2
    height = 128 // 2

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.canvas = tk.Canvas(
            self, width=self.width, height=self.height, bd=0, highlightthickness=0
        )
        self.canvas.pack()

        self.reload()

    def add_image(self) -> None:
        pass

    def add_border(self):
        self.border_image = ImageTk.PhotoImage(
            Image.open("data/icons/border.png").resize((self.width, self.height))
        )

        self.canvas.create_image(
            self.width / 2, self.height / 2, image=self.border_image
        )

    def bind(self, *args, **kwargs):
        """Forward bind to canvas"""
        self.canvas.bind(*args, **kwargs)

    def reload(self):
        self.canvas.delete("all")
        self.add_image()
        self.add_border()


class Empty(Tile):
    ...


class Alien(Tile):
    def __init__(self, parent, color: int, *args, **kwargs):
        self.color = color
        self.color_string = COLORS[color]
        super().__init__(parent, *args, **kwargs)

    def add_image(self) -> None:
        self.image = ImageTk.PhotoImage(
            _recolor_image(
                Image.open("data/icons/alien_green.png").resize(
                    (self.width, self.height)
                ),
                (0, 255, 0),
                self.color_string,
                130,
            )
        )
        self.canvas.create_image(self.width / 2, self.height / 2, image=self.image)


class House(Tile):
    def __init__(self, parent, color: int, *args, **kwargs):
        self.color = color
        self.color_string = COLORS[color]
        super().__init__(parent, *args, **kwargs)

    def add_image(self) -> None:
        self.canvas.configure(bg=self.color_string)
        self.image = ImageTk.PhotoImage(
            Image.open("data/icons/house.png").resize((self.width, self.height))
        )
        self.canvas.create_image(self.width / 2, self.height / 2, image=self.image)


class Obstacle(Tile):
    def add_image(self) -> None:
        self.image = ImageTk.PhotoImage(
            Image.open("data/icons/obstacle.png").resize((self.width, self.height))
        )
        self.canvas.create_image(self.width / 2, self.height / 2, image=self.image)


class Rail(Tile):
    def __init__(
        self,
        parent,
        in_direction,
        out_direction,
        in_color=None,
        out_color=None,
        *args,
        **kwargs
    ):
        self.in_direction = in_direction
        self.out_direction = out_direction
        self.in_color = in_color
        self.out_color = out_color
        super().__init__(parent, *args, **kwargs)

    def add_image(self) -> None:
        im = Image.open("data/icons/rail_half_in.png").resize((self.width, self.height))
        if self.in_color:
            im = _recolor_image(im, (0, 0, 0), self.in_color)
        self.in_image = ImageTk.PhotoImage(self.rotate_image(self.in_direction, im))

        im = Image.open("data/icons/rail_half_out.png").resize(
            (self.width, self.height)
        )
        if self.out_color:
            im = _recolor_image(im, (0, 0, 0), self.out_color)
        self.out_image = ImageTk.PhotoImage(self.rotate_image(self.out_direction, im))
        self.canvas.create_image(self.width / 2, self.height / 2, image=self.in_image)
        self.canvas.create_image(self.width / 2, self.height / 2, image=self.out_image)

    def rotate_image(self, direction, image):
        degrees = {"N": 0, "E": 270, "S": 180, "W": 90}[direction]
        return image.rotate(degrees)


class Entrance(Tile):
    def add_image(self) -> None:
        self.image = ImageTk.PhotoImage(
            Image.open("data/icons/entrance.png").resize((self.width, self.height))
        )
        self.canvas.create_image(self.width / 2, self.height / 2, image=self.image)


class Exit(Tile):
    def add_image(self) -> None:
        self.image = ImageTk.PhotoImage(
            Image.open("data/icons/exit.png").resize((self.width, self.height))
        )
        self.canvas.create_image(self.width / 2, self.height / 2, image=self.image)


if __name__ == "__main__":
    im = Image.open("data/icons/rail_half_in.png")
    im2 = _recolor_image(im, "#000000", "#FF0000")
    im2.show()
