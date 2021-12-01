from itertools import product
from typing import Generator
from nnf import Var, false

Coord = tuple[int, int]


def build_2d_proposition_dict(size: tuple[int, int], prefix: str) -> dict[Coord, Var]:
    props = dict()
    rows, cols = size
    for x in range(cols):
        for y in range(rows):
            suffix = f":({x},{y})"
            props[x, y] = Var(prefix + suffix)
    return props


def all_coords(size: tuple[int, int]):
    """Returns an iterator containing all coordinates in a grid of the given size"""
    return product(range(size[1]), range(size[0]))


def get_directions(coord: Coord):
    for direction, opposite_direction, offset in zip(
        "NESW", "SWNE", ((0, 1), (1, 0), (0, -1), (-1, 0))
    ):
        offset_coord = coord[0] + offset[0], coord[1] + offset[1]
        yield direction, opposite_direction, offset_coord


def get_adjacent(coord: Coord) -> Generator[Coord, None, None]:
    for offset in ((0, 1), (1, 0), (0, -1), (-1, 0)):
        offset_coord = coord[0] + offset[0], coord[1] + offset[1]
        yield offset_coord


def direction_between(p1: Coord, p2: Coord):
    """Returns a string representing the direction of a path from p1 to p2"""
    if p1 == p2:
        raise RuntimeError("coords are equal")
    if p1[0] != p2[0] and p1[1] != p2[1]:
        raise RuntimeError("coords are not aligned along an axis")

    if p1[0] < p2[0]:
        return "E"
    elif p1[0] > p2[0]:
        return "W"
    elif p1[1] < p2[1]:
        return "N"
    else:
        return "S"


def opposite_direction(direction):
    return {"N": "S", "E": "W", "S": "N", "W": "E"}[direction]


def simple_cache(f):
    cache = dict()

    def wrapper(self, *args):
        if args in cache:
            return cache[args]

        # print("new args:", args)
        # This needs to be false for some reason
        # Without it the function recurses infinitely
        # The problem is probably in the wrapped function
        cache[args] = false
        cache[args] = f(self, *args)
        return cache[args]

    return wrapper


if __name__ == "__main__":
    coords = all_coords((3, 5))
    print(type(coords))
    print(coords)
