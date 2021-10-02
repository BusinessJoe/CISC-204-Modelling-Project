from nnf import Var

Coord = tuple[int, int]

def build_2d_proposition_dict(size: tuple[int, int], prefix: str) -> dict[Coord, Var]:
    props = dict()
    rows, cols = size
    for x in range(cols):
        for y in range(rows):
            suffix = f',({x},{y})'
            props[x, y] = (Var(prefix + suffix))
    return props
