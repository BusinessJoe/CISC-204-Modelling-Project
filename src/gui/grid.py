import tkinter as tk
from typing import Any

from src.xml_parser import Color, Coord, Directions, export_xml

from .tiles import Alien, Empty, Entrance, Exit, House, Obstacle, Rail, Tile


class GridDisplay(tk.Frame):
    grid_items: dict[tuple[int, int], Tile]

    def __init__(
        self, parent, create_tile, size: tuple[int, int] = (5, 5), *args, **kwargs
    ):
        super().__init__(parent, *args, **kwargs)
        self.create_tile = create_tile
        self.grid_items = dict()

        self.set_grid_size(size)

    def clear_grid(self):
        for tile in self.grid_items.values():
            tile.destroy()
        self.grid_items.clear()

    def set_grid_size(self, size):
        self.clear_grid()
        # Expand grid
        for x in range(size[1]):
            for y in range(size[0]):
                if (x, y) not in self.grid_items:
                    self.grid_items[x, y] = Empty(self)

        self.size = size
        self.create_layout()

    def create_layout(self):
        for coord, item in self.grid_items.items():
            self.add_grid_item(item, coord)

    def add_grid_item(self, item, coord):
        item.grid(
            # Transform row so that the positive direction is up
            row=self.size[0] - coord[1] - 1,
            column=coord[0],
            ipadx=0,
            sticky=tk.NS,
        )
        item.bind("<Button-1>", self.create_handle_click(coord))

    def create_handle_click(self, coord):
        def f(e):
            tile_type = self.create_tile(parent=self)
            old_widget = self.grid_items[coord]
            self.grid_items[coord] = tile_type
            self.add_grid_item(tile_type, coord)
            old_widget.destroy()

        return f

    def import_(
        self,
        rows: int,
        cols: int,
        colors: int,
        entrances: list[Coord],
        exits: list[Coord],
        aliens: list[tuple[Color, Coord]],
        houses: list[tuple[Color, Coord]],
        obstacles: list[Coord],
        rails: list[tuple[Directions, Coord]],
    ) -> None:
        """Imports the grid from a data dictionary"""
        self.clear_grid()
        self.set_grid_size((rows, cols))

        # TODO: handle color params
        for coord in entrances:
            self.grid_items[coord] = Entrance(self)
        for coord in exits:
            self.grid_items[coord] = Exit(self)
        for color, coord in aliens:
            if color not in range(colors):
                raise RuntimeError("color out of range")
            self.grid_items[coord] = Alien(self, color)
        for color, coord in houses:
            if color not in range(colors):
                raise RuntimeError("color out of range")
            self.grid_items[coord] = House(self, color)
        for coord in obstacles:
            self.grid_items[coord] = Obstacle(self)
        for directions, coord in rails:
            self.grid_items[coord] = Rail(self, directions[0], directions[1])
        for x in range(cols):
            for y in range(rows):
                if (x, y) not in self.grid_items:
                    self.grid_items[x, y] = Empty(self)

        self.create_layout()

    def export(self) -> str:
        """Exports the grid to a string"""
        entrances = [
            coord
            for coord, tile in self.grid_items.items()
            if isinstance(tile, Entrance)
        ]
        exits = [
            coord for coord, tile in self.grid_items.items() if isinstance(tile, Exit)
        ]
        aliens = [
            (tile.color, coord)
            for coord, tile in self.grid_items.items()
            if isinstance(tile, Alien)
        ]
        houses = [
            (tile.color, coord)
            for coord, tile in self.grid_items.items()
            if isinstance(tile, House)
        ]
        obstacles = [
            coord
            for coord, tile in self.grid_items.items()
            if isinstance(tile, Obstacle)
        ]
        rails = [
            ((tile.in_direction, tile.out_direction), coord)
            for coord, tile in self.grid_items.items()
            if isinstance(tile, Rail)
        ]
        colors = (
            max(
                max((a[0] for a in aliens), default=0),
                max((h[0] for h in houses), default=0),
            )
            + 1
        )

        return export_xml(
            rows=self.size[0],
            cols=self.size[1],
            colors=colors,
            entrances=entrances,
            exits=exits,
            aliens=aliens,
            houses=houses,
            obstacles=obstacles,
            rails=rails,
        )
