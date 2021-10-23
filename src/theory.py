from nnf import Var
from .lib204 import Encoding

from . import helpers
from . import logic


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
            - SR:       the tile is an entrance
            - ER:       the tile is an exit
            - V:        the rail is visited during the train's route
            - SA:       the alien is satisfied (picked up) during the train's route
            - SH:       the house is satisfied (an alien is dropped off) during the train's route
            - TA_[c]    honestly no clue

        The value of each key is a dictionary mapping from grid coordinates (x, y) to a propositional variable.

        To get the variable representing an obstacle at position (2, 3) you would use self.props["O"][2, 3].
        """
        self.props = dict()

        grid_prop_prefixes = [
            "A",
            *[f"A_{c}" for c in range(self.num_colors)],
            "H",
            *[f"H_{c}" for c in range(self.num_colors)],
            "O",
            "R",
            *[f"RI{d}" for d in "NESW"],
            *[f"RO{d}" for d in "NESW"],
            "SR",
            "ER",
            "V",
            "SA",
            "SH",
            *[f"TA_{c}" for c in range(self.num_colors)],
        ]

        for prefix in grid_prop_prefixes:
            self.props[prefix] = helpers.build_2d_proposition_dict(self.size, prefix)

    def add_constraints(self) -> None:
        """Adds all of the required contraints to the theory"""
        self.add_alien_constraints()
        self.add_house_constraints()
        self.add_rail_connection_constraints()

        for x, y in helpers.all_coords(self.size):

            # Each tile can only be an alien, house, obstacle, regular rail, special rail, or nothing.
            self.theory.add_constraint(
                logic.one_of_or_none(
                    self.props["A"][x, y],
                    self.props["H"][x, y],
                    self.props["O"][x, y],
                    self.props["R"][x, y],
                    self.props["SR"][x, y],
                    self.props["ER"][x, y],
                )
            )

    def add_alien_constraints(self) -> None:
        for x, y in helpers.all_coords(self.size):
            # If an alien of any color is present, then an alien is present
            self.theory.add_constraint(
                logic.implication(
                    logic.multi_or(
                        *(self.props[f"A_{c}"][x, y] for c in range(self.num_colors))
                    ),
                    self.props["A"][x, y],
                )
            )

            # Each alien must only have one color
            self.theory.add_constraint(
                logic.one_of_or_none(
                    *(self.props[f"A_{c}"][x, y] for c in range(self.num_colors))
                )
            )

    def add_house_constraints(self) -> None:
        for x, y in helpers.all_coords(self.size):
            # If a house of any color is present, then a house is present
            self.theory.add_constraint(
                logic.implication(
                    logic.multi_or(
                        *(self.props[f"H_{c}"][x, y] for c in range(self.num_colors))
                    ),
                    self.props["H"][x, y],
                )
            )

            # Each house must only have one color
            self.theory.add_constraint(
                logic.one_of_or_none(
                    *(self.props[f"H_{c}"][x, y] for c in range(self.num_colors))
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

            # Only one of the input directions can be true. The same holds for output directions
            for io in "IO":
                self.theory.add_constraint(
                    logic.one_of_or_none(
                        *(self.props[f"R{io}{d}"][x, y] for d in "NESW")
                    )
                )

            for direction, opposite, offset in zip(
                "NESW", "SWNE", ((0, 1), (1, 0), (0, -1), (-1, 0))
            ):
                offset_coords = (x + offset[0], y + offset[1])
                if offset_coords in self.props[f"RI{opposite}"]:
                    self.theory.add_constraint(
                        logic.implication(
                            self.props[f"RO{direction}"][x, y],
                            logic.one_of(
                                self.props[f"RI{opposite}"][offset_coords],
                                self.props["SR"][offset_coords],
                                self.props["ER"][offset_coords],
                            ),
                        )
                    )

            # Entrances and exits need a rail beside them
            parts = []
            for opposite, offset in zip("SWNE", ((0, 1), (1, 0), (0, -1), (-1, 0))):
                offset_coords = (x + offset[0], y + offset[1])
                if offset_coords in self.props[f"RI{opposite}"]:
                    parts.append(self.props[f"RI{opposite}"][offset_coords])

            self.theory.add_constraint(
                logic.implication(
                    self.props[f"SR"][x, y],
                    logic.multi_or(*parts),
                )
            )

            parts = []
            for opposite, offset in zip("SWNE", ((0, 1), (1, 0), (0, -1), (-1, 0))):
                offset_coords = (x + offset[0], y + offset[1])
                if offset_coords in self.props[f"RO{opposite}"]:
                    parts.append(self.props[f"RO{opposite}"][offset_coords])

            self.theory.add_constraint(
                logic.implication(
                    self.props[f"ER"][x, y],
                    logic.multi_or(*parts),
                )
            )
