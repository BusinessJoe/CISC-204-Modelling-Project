from typing import Any, TextIO

from src.xml_parser import import_xml
from .lib204 import Encoding
from .theory import CosmicExpressTheory
from . import logic


def read_file(file: TextIO) -> tuple[Encoding, Any]:
    # Reverse the order of rows since row 0 refers to the bottom row
    xml = file.read()

    data = import_xml(xml)

    if len(data["entrances"]) != 1:
        raise ValueError("there must be exactly one entrance")
    if len(data["exits"]) != 1:
        raise ValueError("there must be exactly one exit")

    # TODO: replace the number of colors with value calculated from the file
    theory_wrapper = CosmicExpressTheory((data["rows"], data["cols"]), 3)
    theory = theory_wrapper.theory
    props = theory_wrapper.props

    non_empty_coords = []

    for coord in data["entrances"]:
        theory.add_constraint(props["EN"][coord])
        non_empty_coords.append(coord)
    for coord in data["exits"]:
        theory.add_constraint(props["EX"][coord])
        non_empty_coords.append(coord)
    for color, coord in data["aliens"]:
        theory.add_constraint(props[f"A_{color}"][coord])
        non_empty_coords.append(coord)
    for color, coord in data["houses"]:
        theory.add_constraint(props[f"H_{color}"][coord])
        non_empty_coords.append(coord)
    for coord in data["obstacles"]:
        theory.add_constraint(props["O"][coord])
        non_empty_coords.append(coord)
    for directions, coord in data["rails"]:
        theory.add_constraint(props[f"RI{directions[0]}"][coord])
        theory.add_constraint(props[f"RO{directions[1]}"][coord])
        non_empty_coords.append(coord)

    for x in range(data["cols"]):
        for y in range(data["rows"]):
            if (x, y) not in non_empty_coords:
                theory.add_constraint(
                    logic.none_of(
                        props["A"][x, y],
                        props["H"][x, y],
                        props["O"][x, y],
                        props["R"][x, y],
                        props["EN"][x, y],
                        props["EX"][x, y],
                    )
                )

    return theory, props


if __name__ == "__main__":
    with open("data/xml/test.xml") as f:
        T, _ = read_file(f)

    T.solve()
