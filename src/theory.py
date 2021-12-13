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
        self.colors = range(num_colors)
        self.directions = list("NESW")

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
            ("alien_satisfied", None),
            ("house_satisfied", None),
            ("alien_color", "color"),
            ("house_color", "color"),
            ("rail_input", "direction"),
            ("rail_output", "direction"),
            ("train_alien_before_color", "color"),
            ("train_alien_after_color", "color"),
        ]

        for name, prop_type in grid_props:
            if prop_type is None:
                self._add_grid_prop_dict(name)
            elif prop_type == "color":
                for c in self.colors:
                    self._add_grid_prop_dict(name, c)
            elif prop_type == "direction":
                for d in self.directions:
                    self._add_grid_prop_dict(name, d)
            else:
                raise RuntimeError(f"unknown prop type '{prop_type}'")

    def add_constraints(self) -> None:
        """Adds all of the required contraints to the theory"""

        for coord in helpers.all_coords(self.size):
            self.add_alien_constraints(coord)
            self.add_house_constraints(coord)
            self.add_rail_connection_constraints(coord)
            self.add_rail_state_constraints(coord)
            self.add_satisfaction_constraints(coord)

            # Each tile can only be an alien, house, obstacle, regular rail, special rail, or nothing.
            self.theory.add_constraint(
                logic.one_of_or_none(
                    self.get_prop(name="alien", coord=coord),
                    self.get_prop(name="house", coord=coord),
                    self.get_prop(name="obstacle", coord=coord),
                    self.get_prop(name="rail", coord=coord),
                    self.get_prop(name="entrance", coord=coord),
                    self.get_prop(name="exit", coord=coord),
                )
            )

    def add_alien_constraints(self, coord) -> None:
        # If an alien of any color is present, then an alien is present
        self.theory.add_constraint(
            logic.equal(
                logic.one_of(self.get_props(name="alien_color", coord=coord)),
                self.get_prop(name="alien", coord=coord),
            )
        )

        # Each alien must only have one color
        self.theory.add_constraint(
            logic.one_of_or_none(self.get_props(name="alien_color", coord=coord))
        )

    def add_house_constraints(self, coord) -> None:
        # If a house of any color is present, then a house is present
        self.theory.add_constraint(
            logic.equal(
                logic.one_of(self.get_props(name="house_color", coord=coord)),
                self.get_prop(name="house", coord=coord),
            )
        )

        # Each house must only have one color
        self.theory.add_constraint(
            logic.one_of_or_none(self.get_props(name="house_color", coord=coord))
        )

    def add_rail_connection_constraints(self, coord) -> None:
        """Ensures that the rails form a single, connected path from the entrance to exit"""
        # If an input or output rail direction is present then a rail is present
        self.theory.add_constraint(
            logic.equal(
                logic.multi_or(self.get_props(name="rail_input", coord=coord)),
                self.get_prop(name="rail", coord=coord),
            )
        )
        self.theory.add_constraint(
            logic.equal(
                logic.multi_or(self.get_props(name="rail_output", coord=coord)),
                self.get_prop(name="rail", coord=coord),
            )
        )

        # Input direction cannot be the same as the output direction
        self.theory.add_constraint(
            logic.multi_and(
                logic.implication(
                    self.get_prop(name="rail_input", descriptor=d, coord=coord),
                    self.get_prop(
                        name="rail_output", descriptor=d, coord=coord
                    ).negate(),
                )
                for d in self.directions
            )
        )

        # Only one of the input directions can be true. The same holds for output directions
        self.theory.add_constraint(
            logic.one_of_or_none(self.get_props(name="rail_input", coord=coord))
        )
        self.theory.add_constraint(
            logic.one_of_or_none(self.get_props(name="rail_output", coord=coord))
        )

        # Each rail connects to two of: another rail, entrance, or exit
        for direction, opposite_direction, offset_coord in helpers.get_directions(
            coord
        ):
            if self.grid_contains(offset_coord):
                self.theory.add_constraint(
                    logic.implication(
                        self.get_prop(
                            name="rail_output", descriptor=direction, coord=coord
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
                            name="rail_input", descriptor=direction, coord=coord
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
        self.theory.add_constraint(
            logic.implication(
                self.get_prop(name="entrance", coord=coord),
                logic.one_of(
                    self.get_prop(
                        name="rail_input",
                        descriptor=helpers.direction_between(offset_coord, coord),
                        coord=offset_coord,
                    )
                    for offset_coord in helpers.get_adjacent(coord)
                    if self.grid_contains(offset_coord)
                ),
            )
        )

        # Exits need a single rail outputting to them
        self.theory.add_constraint(
            logic.implication(
                self.get_prop(name="exit", coord=coord),
                logic.one_of(
                    self.get_prop(
                        name="rail_output",
                        descriptor=helpers.direction_between(offset_coord, coord),
                        coord=offset_coord,
                    )
                    for offset_coord in helpers.get_adjacent(coord)
                    if self.grid_contains(offset_coord)
                ),
            )
        )

    def add_rail_state_constraints(self, coord):
        # No rail means no alien on train
        self.theory.add_constraint(
            logic.implication(
                self.get_prop(name="rail", coord=coord).negate(),
                logic.none_of(
                    *self.get_props(name="train_alien_before_color", coord=coord),
                    *self.get_props(name="train_alien_after_color", coord=coord),
                ),
            )
        )

        # Only one color can be true
        self.theory.add_constraint(
            logic.one_of_or_none(
                self.get_props(name="train_alien_before_color", coord=coord)
            )
        )
        self.theory.add_constraint(
            logic.one_of_or_none(
                self.get_props(name="train_alien_after_color", coord=coord)
            )
        )

        # After state of one rail becomes before state of the next
        for c in self.colors:
            for direction, _, offset_coord in helpers.get_directions(coord):
                if self.grid_contains(offset_coord):
                    self.theory.add_constraint(
                        logic.implication(
                            self.get_prop(
                                name="rail_output",
                                descriptor=direction,
                                coord=coord,
                            ),
                            logic.equal(
                                self.get_prop(
                                    name="train_alien_after_color",
                                    descriptor=c,
                                    coord=coord,
                                ),
                                self.get_prop(
                                    name="train_alien_before_color",
                                    descriptor=c,
                                    coord=offset_coord,
                                ),
                            ),
                        )
                    )

        for offset_coord in helpers.get_adjacent(coord):
            if self.grid_contains(offset_coord):
                self.theory.add_constraint(
                    logic.implication(
                        self.get_prop(name="entrance", coord=offset_coord),
                        logic.none_of(
                            self.get_props(
                                name="train_alien_before_color",
                                coord=coord,
                            )
                        ),
                    )
                )
                self.theory.add_constraint(
                    logic.implication(
                        self.get_prop(name="exit", coord=offset_coord),
                        logic.none_of(
                            self.get_props(
                                name="train_alien_after_color",
                                coord=coord,
                            )
                        ),
                    )
                )

        # Rail satisfies alien -> alien gets on train
        self.theory.add_constraint(
            logic.multi_and(
                logic.multi_and(
                    logic.implication(
                        self._rail_satisfies_alien_color(coord, adjacent1, c),
                        # then the alien gets on the train
                        self.get_prop(
                            name="train_alien_after_color",
                            descriptor=c,
                            coord=coord,
                        ),
                    )
                    for c in self.colors
                )
                for adjacent1 in helpers.get_adjacent(coord)
                if self.grid_contains(adjacent1)
            )
        )

        # No alien satisfies rail -> no alien gets on train
        self.theory.add_constraint(
            logic.implication(
                self.get_prop(name="rail", coord=coord)
                # If no aliens satisfy the rail
                & logic.none_of(
                    self._rail_satisfies_alien_color(coord, adjacent1, c)
                    for c in self.colors
                    for adjacent1 in helpers.get_adjacent(coord)
                    if self.grid_contains(adjacent1)
                ),
                # then no alien gets on the train
                logic.implication(
                    logic.none_of(
                        self.get_props(
                            name="train_alien_before_color",
                            coord=coord,
                        ),
                    ),
                    logic.none_of(
                        self.get_props(
                            name="train_alien_after_color",
                            coord=coord,
                        ),
                    ),
                ),
            )
        )

        # Rail satisfies house -> alien gets off train
        self.theory.add_constraint(
            logic.multi_and(
                logic.multi_and(
                    logic.implication(
                        self._rail_satisfies_house_color(coord, adjacent1, c),
                        # then the alien gets off the train
                        self.get_prop(
                            name="train_alien_after_color",
                            descriptor=c,
                            coord=coord,
                        ).negate(),
                    )
                    for c in self.colors
                )
                for adjacent1 in helpers.get_adjacent(coord)
                if self.grid_contains(adjacent1)
            )
        )

        # No house satisfies rail -> no alien gets off train
        self.theory.add_constraint(
            logic.implication(
                self.get_prop(name="rail", coord=coord)
                # If no houses satisfy the rail
                & logic.none_of(
                    self._rail_satisfies_house_color(coord, adjacent1, c)
                    for c in self.colors
                    for adjacent1 in helpers.get_adjacent(coord)
                    if self.grid_contains(adjacent1)
                ),
                # then no alien gets off the train
                logic.multi_and(
                    logic.implication(
                        self.get_prop(
                            name="train_alien_before_color",
                            descriptor=c,
                            coord=coord,
                        ),
                        self.get_prop(
                            name="train_alien_after_color",
                            descriptor=c,
                            coord=coord,
                        ),
                    )
                    for c in self.colors
                ),
            )
        )

        # No rail satisfies alien -> alien is not satisfied
        self.theory.add_constraint(
            logic.implication(
                self.get_prop(name="alien", coord=coord)
                # If no rails satisfy the alien
                & logic.none_of(
                    self._rail_satisfies_alien_color(adjacent1, coord, c)
                    for c in self.colors
                    for adjacent1 in helpers.get_adjacent(coord)
                    if self.grid_contains(adjacent1)
                ),
                # then alien is not satisfied
                self.get_prop(name="alien_satisfied", coord=coord).negate(),
            )
        )

        # No rail satisfies house -> house is not satisfied
        self.theory.add_constraint(
            logic.implication(
                self.get_prop(name="house", coord=coord)
                # If no rails satisfy the house
                & logic.none_of(
                    self._rail_satisfies_house_color(adjacent1, coord, c)
                    for c in self.colors
                    for adjacent1 in helpers.get_adjacent(coord)
                    if self.grid_contains(adjacent1)
                ),
                # then house is not satisfied
                self.get_prop(name="house_satisfied", coord=coord).negate(),
            )
        )

    def add_satisfaction_constraints(self, coord):
        # Every alien must be satisfied and
        # no alien means alien is not satisfied
        self.theory.add_constraint(
            logic.equal(
                self.get_prop(name="alien", coord=coord),
                self.get_prop(name="alien_satisfied", coord=coord),
            )
        )

        # Every house must be satisfied and
        # no house means house is not satisfied
        self.theory.add_constraint(
            logic.equal(
                self.get_prop(name="house", coord=coord),
                self.get_prop(name="house_satisfied", coord=coord),
            )
        )

        # No alien means alien is not satisfied

    def _rail_satisfies_alien_color(self, rail_coord, alien_coord, color) -> Var:
        return (
            # If coord is a rail,
            self.get_prop(name="rail", coord=rail_coord)
            # and the train is empty
            & logic.none_of(
                self.get_props(
                    name="train_alien_before_color",
                    coord=rail_coord,
                )
            )
            # and adjacent tile is an alien of given color
            & self.get_prop(name="alien_color", descriptor=color, coord=alien_coord)
            # and the rail comes before any other rails adjacent to alien
            # TODO: only check empty adjacent rails
            & logic.multi_and(
                logic.implication(
                    self.get_prop(name="rail", coord=other_rail)
                    & logic.none_of(
                        self.get_props(
                            name="train_alien_before_color", coord=other_rail
                        )
                    ),
                    self.rail_comes_before(rail_coord, other_rail),
                )
                for other_rail in helpers.get_adjacent(alien_coord)
                if rail_coord != other_rail and self.grid_contains(other_rail)
            )
        )

    def _rail_satisfies_house_color(self, rail_coord, house_coord, color) -> Var:
        return (
            # If coord is a rail,
            self.get_prop(name="rail", coord=rail_coord)
            # and the train has an alien of given color
            & self.get_prop(
                name="train_alien_before_color", descriptor=color, coord=rail_coord
            )
            # and adjacent tile is an house of given color
            & self.get_prop(name="house_color", descriptor=color, coord=house_coord)
            # and the rail comes before any other rails adjacent to house
            # TODO: only check adjacent rails with color
            & logic.multi_and(
                logic.implication(
                    self.get_prop(name="rail", coord=other_rail)
                    & self.get_prop(
                        name="train_alien_before_color",
                        descriptor=color,
                        coord=other_rail,
                    ),
                    self.rail_comes_before(rail_coord, other_rail),
                )
                for other_rail in helpers.get_adjacent(house_coord)
                if rail_coord != other_rail and self.grid_contains(other_rail)
            )
        )

    @helpers.simple_cache
    def rail_comes_before(self, p1, p2):
        # TODO: rewrite this with iteration instead of recursion
        if p1 == p2:
            return false
        if not (self.grid_contains(p1) and self.grid_contains(p2)):
            return false

        # adjacency check using taxicab distance
        if abs(p1[0] - p2[0]) + abs(p1[1] - p2[1]) == 1:
            direction = helpers.direction_between(p1, p2)

            return self.get_prop(name="rail_output", descriptor=direction, coord=p1)

        parts = []
        for p3 in helpers.get_adjacent(p2):
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
