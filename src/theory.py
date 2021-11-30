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
            - BTA_[c]   train alien color before a timestep (think about it like the input state)
            - ATA_[c]   train alien color after a timestep (think about it like the output state)

        The value of each key is a dictionary mapping from grid coordinates (x, y) to a propositional variable.

        To get the variable representing an obstacle at position (2, 3) you would use self.props["O"][2, 3].
        """
        self._named_props = dict()

        # Props are represented by a tuple (prefix, name, prop_type)
        # - prefix is the shorthand symbol used as a key for the prop in the props dict
        # - name is the full name of the prop (currently unused)
        # - prop_type is one of (None, "color", "direction") and determines if the prop
        #   gets an extra descriptor
        grid_props = [
            ("alien", None),
            ("house", None),
            ("obstacle", None),
            ("rail", None),
            ("entrance", None),
            ("exit", None),
            ("visited", None),
            ("alien_satisfied", None),
            ("house_satisfied", None),
            ("alien_color", "color"),
            ("house_color", "color"),
            ("rail_input", "direction"),
            ("rail_output", "direction"),
            ("train_alien", None),
            ("train_alien_before", "color"),
            ("train_alien_after", "color"),
        ]

        for name, prop_type in grid_props:
            if prop_type is None:
                self._add_grid_prop_dict(name)
            elif prop_type == "color":
                for c in range(self.num_colors):
                    self._add_grid_prop_dict(name, c)
            elif prop_type == "direction":
                for d in "NESW":
                    self._add_grid_prop_dict(name, d)
            else:
                raise RuntimeError(f"unknown prop type '{prop_type}'")

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
                    self.get_prop(name="alien", coord=(x, y)),
                    self.get_prop(name="house", coord=(x, y)),
                    self.get_prop(name="obstacle", coord=(x, y)),
                    self.get_prop(name="rail", coord=(x, y)),
                    self.get_prop(name="entrance", coord=(x, y)),
                    self.get_prop(name="exit", coord=(x, y)),
                )
            )

    def add_alien_constraints(self) -> None:
        for x, y in helpers.all_coords(self.size):
            # If an alien of any color is present, then an alien is present
            self.theory.add_constraint(
                logic.implication(
                    logic.multi_or(self.get_props(name="alien_color", coord=(x, y))),
                    self.get_prop(name="alien", coord=(x, y)),
                )
            )

            # Each alien must only have one color
            self.theory.add_constraint(
                logic.one_of_or_none(self.get_props(name="alien_color", coord=(x, y)))
            )

    def add_house_constraints(self) -> None:
        for x, y in helpers.all_coords(self.size):
            # If a house of any color is present, then a house is present
            self.theory.add_constraint(
                logic.implication(
                    logic.multi_or(self.get_props(name="house_color", coord=(x, y))),
                    self.get_prop(name="house", coord=(x, y)),
                )
            )

            # Each house must only have one color
            self.theory.add_constraint(
                logic.one_of_or_none(self.get_props(name="house_color", coord=(x, y)))
            )

    def add_rail_connection_constraints(self) -> None:
        """Ensures that the rails form a single, connected path from the entrance to exit"""
        for x, y in helpers.all_coords(self.size):
            # If an input or output rail direction is present then a rail is present
            self.theory.add_constraint(
                logic.implication(
                    logic.multi_or(
                        *self.get_props(name="rail_input", coord=(x, y)),
                        *self.get_props(name="rail_output", coord=(x, y)),
                    ),
                    self.get_prop(name="rail", coord=(x, y)),
                )
            )

            # Input direction cannot be the same as the output direction
            for d in "NESW":
                self.theory.add_constraint(
                    logic.implication(
                        self.get_prop(name="rail_input", descriptor=d, coord=(x, y)),
                        self.get_prop(
                            name="rail_output", descriptor=d, coord=(x, y)
                        ).negate(),
                    )
                )
                self.theory.add_constraint(
                    logic.implication(
                        self.get_prop(name="rail_output", descriptor=d, coord=(x, y)),
                        self.get_prop(
                            name="rail_input", descriptor=d, coord=(x, y)
                        ).negate(),
                    )
                )

            # Only one of the input directions can be true. The same holds for output directions
            for io in ("rail_input", "rail_output"):
                self.theory.add_constraint(
                    logic.one_of_or_none(self.get_props(name=io, coord=(x, y)))
                )

            # Each rail connects to two of: another rail, entrance, or exit
            for direction, opposite_direction, offset_coord in helpers.get_directions(
                (x, y)
            ):
                if self.grid_contains(offset_coord):
                    self.theory.add_constraint(
                        logic.implication(
                            self.get_prop(
                                name="rail_output", descriptor=direction, coord=(x, y)
                            ),
                            logic.one_of(
                                self.get_prop(
                                    name="rail_input",
                                    descriptor=opposite_direction,
                                    coord=offset_coord,
                                ),
                                self.get_prop(name="exit", coord=offset_coord),
                            ),
                        )
                    )

                    self.theory.add_constraint(
                        logic.implication(
                            self.get_prop(
                                name="rail_input", descriptor=direction, coord=(x, y)
                            ),
                            logic.one_of(
                                self.get_prop(
                                    name="rail_output",
                                    descriptor=opposite_direction,
                                    coord=offset_coord,
                                ),
                                self.get_prop(name="entrance", coord=offset_coord),
                            ),
                        )
                    )

            # Entrances need a single rail taking input from them
            parts = []
            for _, opposite_direction, offset_coord in helpers.get_directions((x, y)):
                if self.grid_contains(offset_coord):
                    parts.append(
                        self.get_prop(
                            name="rail_input",
                            descriptor=opposite_direction,
                            coord=offset_coord,
                        )
                    )

            self.theory.add_constraint(
                logic.implication(
                    self.get_prop(name="entrance", coord=(x, y)),
                    logic.one_of(parts),
                )
            )

            # Exits need a single rail outputting to them
            parts = []
            for _, opposite_direction, offset_coord in helpers.get_directions((x, y)):
                if self.grid_contains(offset_coord):
                    parts.append(
                        self.get_prop(
                            name="rail_output",
                            descriptor=opposite_direction,
                            coord=offset_coord,
                        )
                    )

            self.theory.add_constraint(
                logic.implication(
                    self.get_prop(name="exit", coord=(x, y)),
                    logic.one_of(parts),
                )
            )

    def add_rail_state_constraints(self):
        return
        for x, y in helpers.all_coords(self.size):
            for _, opposite_direction, offset_coord in helpers.get_directions((x, y)):
                if self.grid_contains(offset_coord):
                    self.theory.add_constraint(
                        logic.implication(
                            self.props["EN"][offset_coord], self.props["BTA"]
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
                    self.get_prop(name="rail_input", descriptor=direction, coord=p2)
                    & self.get_prop(
                        name="rail_output", descriptor=opposite_direction, coord=p1
                    )
                )
            return logic.multi_or(parts)

        parts = []
        for _, _, p3 in helpers.get_directions(p2):
            if self.grid_contains(p3):
                parts.append(
                    self.rail_comes_before(p1, p3) & self.rail_comes_before(p3, p2)
                )
        a = logic.multi_or(parts)
        b = a.simplify()
        return b

    def _add_grid_prop_dict(self, name, descriptor=None):
        key = name
        if descriptor is not None:
            key = f"{key}_{descriptor}"

        prop_dict = helpers.build_2d_proposition_dict(self.size, key)

        if name in self._named_props:
            self._named_props[name][descriptor] = prop_dict
        else:
            self._named_props[name] = {descriptor: prop_dict}

    def get_prop(self, *, coord, name, descriptor=None):
        return self._named_props[name][descriptor][coord]

    def get_props(self, *, coord, name):
        if name:
            descriptor_dicts = [
                v for k, v in self._named_props[name].items() if k is not None
            ]
            if not descriptor_dicts:
                raise RuntimeError("no props found")
            return [d[coord] for d in descriptor_dicts]
