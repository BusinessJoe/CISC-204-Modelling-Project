import functools
from nnf import Var, false
from .lib204 import Encoding

from . import helpers
from . import logic

ARGS = []


class CosmicExpressTheory:
    props: dict[str, dict[tuple[int, int], Var]]

    def __init__(self, size: tuple[int, int] = (5, 5), num_colors: int = 2) -> None:
        self.num_rows, self.num_cols = size

        self.num_colors = num_colors

        self.theory = Encoding()
        self.build_propositions()
        self.add_constraints()

    @property
    def size(self) -> tuple[int, int]:
        return self.num_rows, self.num_cols

    def grid_contains(self, coord) -> bool:
        # coord is an (x, y) tuple, so coord[0] corrisponds to columns and coord[1] to rows.
        return 0 <= coord[0] < self.num_cols and 0 <= coord[1] < self.num_rows

    def build_propositions(self) -> None:
        """Builds the propositions required by the theory

        Each tile on the grid has many propositions that apply to it:
            - whether the tile is an alien
            - whether the tile is a rail
            - whether the tile's rail outputs to the North
        and so on. These propositions are created and stored in the self.props dictionary.

        The key of self.props represents the type of proposition:
            - A:        the tile is an alien
            - A_[c]:    the alien is of color [c]
            - H:        the tile is a house
            - H_[c]:    the house is of color [c]
            - O:        the tile is an obstacle
            - R:        the tile is a rail
            - RI[d]:    the rail has input from direction [d]
            - RO[d]:    the rail has input from direction [d]
            - EN:       the tile is an entrance
            - EX:       the tile is an exit
            - V:        the rail is visited during the train's route
            - SA:       the alien is satisfied (picked up) during the train's route
            - SH:       the house is satisfied (an alien is dropped off) during the train's route
            - TA_[c]    train alien color

        The value of each key is a dictionary mapping from grid coordinates (x, y) to a propositional variable.

        To get the variable representing an obstacle at position (2, 3) you would use self.props["O"][2, 3].
        """
        self.props = dict()

        grid_prop_prefixes = [
            "A",
            "H",
            "O",
            "R",
            "EN",
            "EX",
            "V",
            "SA",
            "SH",
            *(f"A_{c}" for c in range(self.num_colors)),
            *(f"H_{c}" for c in range(self.num_colors)),
            *(f"TA_{c}" for c in range(self.num_colors)),
            *(f"RI{d}" for d in "NESW"),
            *(f"RO{d}" for d in "NESW"),
        ]

        for prefix in grid_prop_prefixes:
            self.props[prefix] = helpers.build_2d_proposition_dict(self.size, prefix)

    def add_constraints(self) -> None:
        """Adds all of the required contraints to the theory"""
        self.add_alien_constraints()
        self.add_house_constraints()
        self.add_rail_connection_constraints()
        self.add_rail_state_constraints()

        for x, y in helpers.all_coords(self.size):

            # Each tile can only be an alien, house, obstacle, regular rail, special rail, or nothing.
            self.theory.add_constraint(
                logic.one_of_or_none(
                    self.props["A"][x, y],
                    self.props["H"][x, y],
                    self.props["O"][x, y],
                    self.props["R"][x, y],
                    self.props["EN"][x, y],
                    self.props["EX"][x, y],
                )
            )

    def add_alien_constraints(self) -> None:
        for x, y in helpers.all_coords(self.size):
            # If an alien of any color is present, then an alien is present
            self.theory.add_constraint(
                logic.implication(
                    logic.multi_or(
                        self.props[f"A_{c}"][x, y] for c in range(self.num_colors)
                    ),
                    self.props["A"][x, y],
                )
            )

            # Each alien must only have one color
            self.theory.add_constraint(
                logic.one_of_or_none(
                    self.props[f"A_{c}"][x, y] for c in range(self.num_colors)
                )
            )

    def add_house_constraints(self) -> None:
        for x, y in helpers.all_coords(self.size):
            # If a house of any color is present, then a house is present
            self.theory.add_constraint(
                logic.implication(
                    logic.multi_or(
                        self.props[f"H_{c}"][x, y] for c in range(self.num_colors)
                    ),
                    self.props["H"][x, y],
                )
            )

            # Each house must only have one color
            self.theory.add_constraint(
                logic.one_of_or_none(
                    self.props[f"H_{c}"][x, y] for c in range(self.num_colors)
                )
            )

    def add_rail_connection_constraints(self) -> None:
        """Ensures that the rails form a single, connected path from the entrance to exit"""
        for x, y in helpers.all_coords(self.size):
            # If an input or output rail direction is present then a rail is present
            self.theory.add_constraint(
                logic.implication(
                    logic.multi_or(
                        *(self.props[f"RI{d}"][x, y] for d in "NESW"),
                        *(self.props[f"RO{d}"][x, y] for d in "NESW"),
                    ),
                    self.props["R"][x, y],
                )
            )

            # Input direction cannot be the same as the output direction
            for d in "NESW":
                self.theory.add_constraint(
                    logic.implication(
                        self.props[f"RI{d}"][x, y], self.props[f"RO{d}"][x, y].negate()
                    )
                )
                self.theory.add_constraint(
                    logic.implication(
                        self.props[f"RO{d}"][x, y], self.props[f"RI{d}"][x, y].negate()
                    )
                )

            # Only one of the input directions can be true. The same holds for output directions
            for io in "IO":
                self.theory.add_constraint(
                    logic.one_of_or_none(self.props[f"R{io}{d}"][x, y] for d in "NESW")
                )

            # Each rail connects to two of: another rail, entrance, or exit
            for direction, opposite_direction, offset_coord in helpers.get_directions(
                (x, y)
            ):
                if self.grid_contains(offset_coord):
                    self.theory.add_constraint(
                        logic.implication(
                            self.props[f"RO{direction}"][x, y],
                            logic.one_of(
                                self.props[f"RI{opposite_direction}"][offset_coord],
                                self.props["EX"][offset_coord],
                            ),
                        )
                    )

                    self.theory.add_constraint(
                        logic.implication(
                            self.props[f"RI{direction}"][x, y],
                            logic.one_of(
                                self.props[f"RO{opposite_direction}"][offset_coord],
                                self.props["EN"][offset_coord],
                            ),
                        )
                    )

            # Entrances need a single rail taking input from them
            parts = []
            for _, opposite_direction, offset_coord in helpers.get_directions((x, y)):
                if self.grid_contains(offset_coord):
                    parts.append(self.props[f"RI{opposite_direction}"][offset_coord])

            self.theory.add_constraint(
                logic.implication(
                    self.props[f"EN"][x, y],
                    logic.one_of(parts),
                )
            )

            # Exits need a single rail outputting to them
            parts = []
            for _, opposite_direction, offset_coord in helpers.get_directions((x, y)):
                if self.grid_contains(offset_coord):
                    parts.append(self.props[f"RO{opposite_direction}"][offset_coord])

            self.theory.add_constraint(
                logic.implication(
                    self.props["EX"][x, y],
                    logic.one_of(parts),
                )
            )

    def add_rail_state_constraints(self):
        for x, y in helpers.all_coords(self.size):
            for _, opposite_direction, offset_coord in helpers.get_directions((x, y)):
                if self.grid_contains(offset_coord):
                    self.theory.add_constraint(
                        logic.implication(
                            self.props["EN"][offset_coord],
                            self.props["BTA"]
                        )
                    )

    @helpers.simple_cache
    def rail_comes_before(self, p1, p2):
        if p1 == p2:
            return false
        if not (self.grid_contains(p1) and self.grid_contains(p2)):
            return false

        # adjacency check using taxicab distance
        if abs(p1[0] - p2[0]) + abs(p1[1] - p2[1]) == 1:
            parts = []
            for direction, opposite_direction in zip("NESW", "SWNE"):
                parts.append(
                    self.props[f"RI{direction}"][p2]
                    & self.props[f"RO{opposite_direction}"][p1]
                )
            return logic.multi_or(parts)

        parts = []
        for _, _, p3 in helpers.get_directions(p2):
            if self.grid_contains(p3):
                parts.append(
                    self.rail_comes_before(p1, p3) & self.rail_comes_before(p3, p2)
                )

        return logic.multi_or(parts)
