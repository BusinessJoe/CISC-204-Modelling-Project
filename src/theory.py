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
        """Builds the propositions required by the theory"""
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
        self.add_alien_constraints()
        self.add_house_constraints()
        self.add_rail_constraints()

        for x, y in helpers.all_coords(self.size):

            # Each tile can only be an alien, house, obstacle, rail, or nothing.
            self.theory.add_constraint(
                logic.one_of_or_none(
                    self.props["A"][x, y],
                    self.props["H"][x, y],
                    self.props["O"][x, y],
                    self.props["R"][x, y],
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

    def add_rail_constraints(self) -> None:
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
