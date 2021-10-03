from typing import TextIO
import itertools
from .theory import CosmicExpressTheory


def read_file(file: TextIO) -> tuple[Encoding, Any]:
    # Reverse the order of rows since row 0 refers to the bottom row
    rows = list(reversed([line.rstrip("\n") for line in file]))

    num_rows = len(rows)
    num_cols = len(rows[0])

    print(f"{num_cols=}")
    # Sanity check that every row is the same length
    for row in rows:
        print(f"{row=}")
        if len(row) != num_cols:
            raise RuntimeError("The provided board is not rectangular")

    obstacles = []
    starting_rail = None
    ending_rail = None
    rails = []
    for y, row in enumerate(rows):
        for x, char in enumerate(row):
            if char == "#":
                obstacles.append((x, y))

            if char == "I":
                if not starting_rail:
                    starting_rail = (x, y)
                else:
                    raise RuntimeError("Found more than one starting rail")

            if char == "O":
                if not ending_rail:
                    ending_rail = (x, y)
                else:
                    raise RuntimeError("Found more than one ending rail")

            rail = parse_rail(char)
            if rail:
                rails.append((rail, (x, y)))
    # Check that starting rail and ending rail were defined
    if not starting_rail:
        raise RuntimeError("No starting rail found")
    if not ending_rail:
        raise RuntimeError("No ending rail found")

    # TODO: replace the number of colors with value calculated from the file
    theory_wrapper = CosmicExpressTheory((num_rows, num_cols), 2)
    theory = theory_wrapper.theory
    props = theory_wrapper.props

    for obs in obstacles:
        theory.add_constraint(props["O"][obs])
    theory.add_constraint(props["SR"][starting_rail])
    theory.add_constraint(props["ER"][ending_rail])
    for rail in rails:
        i, o = rail[0]
        x, y = rail[1]
        theory.add_constraint(props[f"RI{i}"][x, y])
        theory.add_constraint(props[f"RO{o}"][x, y])

    return theory


def parse_rail(char):
    rail_mapping = {
        "⭠": ("E", "W"),
        "⭢": ("W", "E"),
        "⭡": ("S", "N"),
        "⭣": ("N", "S"),
        "⮠": ("N", "W"),
        "⮡": ("N", "E"),
        "⮢": ("S", "W"),
        "⮣": ("S", "E"),
        "⮤": ("E", "N"),
        "⮥": ("W", "N"),
        "⮦": ("E", "S"),
        "⮧": ("W", "S"),
    }
    return rail_mapping.get(char)


def get_special_rail(rail_type, x, y, num_rows, num_cols):
    if (x, y) in (
        (0, 0),
        (0, num_rows - 1),
        (num_cols - 1, 0),
        (num_cols - 1, num_rows - 1),
    ):
        raise RuntimeError("Special rail cannot be in a corner")

    if x == 0:
        directions = "EW"
    elif x == num_cols - 1:
        directions = "WE"
    elif y == 0:
        directions = "NS"
    elif y == num_rows - 1:
        directions = "SN"
    else:
        raise RuntimeError("Special rail must be on an edge")

    direction = directions[0] if rail_type == "I" else directions[1]

    return direction, (x, y)


if __name__ == "__main__":
    with open("data/test1.ce") as f:
        read_file(f)
