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

    theory_wrapper = CosmicExpressTheory((data["rows"], data["cols"]), data["colors"])
    theory = theory_wrapper.theory

    non_empty_coords = []

    for coord in data["entrances"]:
        theory.add_constraint(theory_wrapper.get_prop(name="entrance", coord=coord))
        non_empty_coords.append(coord)

    for coord in data["exits"]:
        theory.add_constraint(theory_wrapper.get_prop(name="exit", coord=coord))
        non_empty_coords.append(coord)

    for color, coord in data["aliens"]:
        theory.add_constraint(
            theory_wrapper.get_prop(name="alien_color", descriptor=color, coord=coord)
        )
        non_empty_coords.append(coord)

    for color, coord in data["houses"]:
        theory.add_constraint(
            theory_wrapper.get_prop(name="house_color", descriptor=color, coord=coord)
        )
        non_empty_coords.append(coord)

    for coord in data["obstacles"]:
        theory.add_constraint(theory_wrapper.get_prop(name="obstacle", coord=coord))
        non_empty_coords.append(coord)

    for directions, coord in data["rails"]:
        theory.add_constraint(
            theory_wrapper.get_prop(
                name="rail_input", descriptor=directions[0], coord=coord
            )
        )
        theory.add_constraint(
            theory_wrapper.get_prop(
                name="rail_output", descriptor=directions[1], coord=coord
            )
        )
        theory.add_constraint(theory_wrapper.get_prop(name="rail", coord=coord))
        non_empty_coords.append(coord)

    for c in range(data["cols"]):
        for r in range(data["rows"]):
            if (c, r) not in non_empty_coords:
                coord = (c, r)
                theory.add_constraint(
                    logic.none_of(
                        theory_wrapper.get_prop(name="alien", coord=coord),
                        theory_wrapper.get_prop(name="house", coord=coord),
                        theory_wrapper.get_prop(name="obstacle", coord=coord),
                        theory_wrapper.get_prop(name="rail", coord=coord),
                        theory_wrapper.get_prop(name="entrance", coord=coord),
                        theory_wrapper.get_prop(name="exit", coord=coord),
                    )
                )

    return theory


if __name__ == "__main__":
    with open("data/xml/test.xml") as f:
        T, _ = read_file(f)

    T.solve()
