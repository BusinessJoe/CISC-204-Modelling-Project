import xml.etree.ElementTree as ET

Coord = tuple[int, int]
Color = int
Directions = tuple[str, str]


def export_xml(
    rows: int,
    cols: int,
    colors: int,
    entrances: list[Coord],
    exits: list[Coord],
    aliens: list[tuple[Color, Coord]],
    houses: list[tuple[Color, Coord]],
    obstacles: list[Coord],
    rails: list[tuple[Directions, Coord]],
) -> str:
    """Returns an xml representation of the grid"""

    if len(entrances) != 1:
        raise ValueError("there must be exactly one entrance")
    if len(exits) != 1:
        raise ValueError("there must be exactly one exit")

    board = ET.Element(
        "board",
        {"rows": str(rows), "cols": str(cols), "colors": str(colors)},
    )
    ET.SubElement(board, "entrance", _tuple_to_coord(entrances[0]))
    ET.SubElement(board, "exit", _tuple_to_coord(exits[0]))
    e = ET.SubElement(board, "aliens")
    for color, coord in aliens:
        ET.SubElement(e, "alien", {**_tuple_to_coord(coord), "color": str(color)})
    e = ET.SubElement(board, "houses")
    for color, coord in houses:
        ET.SubElement(e, "house", {**_tuple_to_coord(coord), "color": str(color)})
    e = ET.SubElement(board, "obstacles")
    for coord in obstacles:
        ET.SubElement(e, "obstacle", _tuple_to_coord(coord))
    e = ET.SubElement(board, "rails")
    for directions, coord in rails:
        ET.SubElement(
            e,
            "rail",
            {
                **_tuple_to_coord(coord),
                "in_direction": directions[0],
                "out_direction": directions[1],
            },
        )

    return ET.tostring(board, encoding="unicode")


def import_xml(xml: str):
    board = ET.fromstring(xml)
    rows = board.get("rows")
    cols = board.get("cols")
    colors = board.get("colors")

    entrance = board.find("entrance")
    exit_ = board.find("exit")
    aliens = board.find("aliens").findall("alien")
    houses = board.find("houses").findall("house")
    obstacles = board.find("obstacles").findall("obstacle")
    rails = board.find("rails").findall("rail")

    return {
        "rows": int(rows),
        "cols": int(cols),
        "colors": int(colors),
        "entrances": [_coord_to_tuple(entrance.attrib)],
        "exits": [_coord_to_tuple(exit_.attrib)],
        "aliens": [(int(e.get("color")), _coord_to_tuple(e.attrib)) for e in aliens],
        "houses": [(int(e.get("color")), _coord_to_tuple(e.attrib)) for e in houses],
        "obstacles": [_coord_to_tuple(e.attrib) for e in obstacles],
        "rails": [
            ((e.get("in_direction"), e.get("out_direction")), _coord_to_tuple(e.attrib))
            for e in rails
        ],
    }


def _tuple_to_coord(tup: tuple[int, int]) -> dict[str, str]:
    return {"x": str(tup[0]), "y": str(tup[1])}


def _coord_to_tuple(coord: dict[str, str]) -> tuple[int, int]:
    return int(coord["x"]), int(coord["y"])


if __name__ == "__main__":
    with open("data/xml/test.xml") as f:
        import_xml(f.read())
