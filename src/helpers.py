from itertools import product
from nnf import Var

Coord = tuple[int, int]


def build_2d_proposition_dict(size: tuple[int, int], prefix: str) -> dict[Coord, Var]:
    props = dict()
    rows, cols = size
    for x in range(cols):
        for y in range(rows):
            suffix = f",({x},{y})"
            props[x, y] = Var(prefix + suffix)
    return props


def all_coords(size: tuple[int, int]):
    """Returns an iterator containing all coordinates in a grid of the given size"""
    return product(range(size[1]), range(size[0]))


if __name__ == "__main__":
    coords = all_coords((3, 5))
    print(type(coords))
    print(coords)
