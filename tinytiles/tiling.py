from typing import Dict
from tinytiles.utils_2D import *


class SquareGlues(object):
    """Represents the four squares of a Wang tile. Edge colors are given by int and can be None."""

    def __init__(
        self,
        north: int | None = None,
        east: int | None = None,
        south: int | None = None,
        west: int | None = None,
    ):
        self.north: int | None = north
        self.east: int | None = east
        self.south: int | None = south
        self.west: int | None = west

    def __getitem__(self, i: int) -> int | None:
        return [self.north, self.east, self.south, self.west][i]

    def __setitem__(self, key, value):
        if key == 0:
            self.north = value
        if key == 1:
            self.east = value
        if key == 2:
            self.south = value
        if key == 3:
            self.west = value

    def __eq__(self, other: "SquareGlues") -> bool:
        return (
            self.north == other.north
            and self.east == other.east
            and self.south == other.south
            and self.west == other.west
        )

    def __str__(self):
        return f"({self.north},{self.east},{self.south},{self.west})"

    def __repr__(self):
        return str(self)


SpecialTiles = str
NoTileCanFit = "NoTileCanFit"
ManyTilesCanFit = "ManyTilesCanFit"


class Tiling(object):
    def __init__(
        self,
        tileset: list[SquareGlues] | list[tuple[int, int, int, int]] = [],
        tiling: Dict[TilePosition, SquareGlues | SpecialTiles] = {},
        _cursor_position=TilePosition(0, 0),
        copy_tiling=True,
    ):
        self.tileset: list[SquareGlues] = []
        if len(tileset) > 1 and type(tileset[0]) == tuple:
            for tiletype in tileset:
                self.tileset.append(SquareGlues(*tiletype))
        else:
            self.tileset: list[SquareGlues] = tileset

        if copy_tiling:
            self.tiling: Dict[TilePosition, SquareGlues | SpecialTiles] = tiling.copy()
        else:
            self.tiling: Dict[TilePosition, SquareGlues | SpecialTiles] = tiling

        self._cursor_position = _cursor_position  # position updated by factories
        self._growth_frontier = None

    def get_tile_from_id(
        self, tile: SquareGlues | list[tuple[int, int, int, int]] | int | SpecialTiles
    ) -> SquareGlues:
        if isinstance(tile, str) or isinstance(tile, SquareGlues):
            return tile

        if type(tile) == int:
            return self.tileset[tile]

        return SquareGlues(*tile)

    def move(self, step_2D: TilePosition):
        return Tiling(self.tileset, self.tiling, self._cursor_position + step_2D)

    def reset_pos(self):
        return Tiling(self.tileset, self.tiling)

    def put_tiles(
        self,
        tiles: list[SquareGlues | list[tuple[int, int, int, int]] | int],
        step_2D: TilePosition,
    ):
        new_tiling = self.tiling.copy()
        new_cursor_position = self._cursor_position
        for i, tile in enumerate(tiles):
            tile = self.get_tile_from_id(tile)
            new_tiling[new_cursor_position] = tile
            if i != len(tiles) - 1:
                new_cursor_position += step_2D

        return Tiling(self.tileset, new_tiling, new_cursor_position, copy_tiling=False)

    def bounding_box(self) -> tuple[int, int, int, int]:
        min_x, max_x = 0, 0
        min_y, max_y = 0, 0
        for position in self.tiling:
            min_x = min(min_x, position.x)
            max_x = max(max_x, position.x)
            min_y = min(min_y, position.y)
            max_y = max(max_y, position.y)
        return min_x, min_y, max_x - min_x + 1, max_y - min_y + 1

    def svg(
        self,
        hihghlight_positions: list[TilePosition | tuple[TilePosition, str]] = [],
        show_growth_frontier=False,
    ):
        from tinytiles.svg_view import tiling_to_svg

        highlight_frontier = []
        if show_growth_frontier:
            if self._growth_frontier is None:
                self._compute_growth_frontier()
            for pos in self._growth_frontier:
                highlight_frontier.append((pos, "orange"))

        return tiling_to_svg(self, hihghlight_positions + highlight_frontier)

    def __getitem__(self, position: TilePosition) -> SquareGlues | SpecialTiles:
        return self.tiling[position]

    def __iter__(self):
        for position in self.tiling:
            yield position

    def neighbouring_tiles(self, pos: TilePosition) -> list[SquareGlues]:
        to_return = []
        for _dir in DIRS:
            neigh = pos + _dir
            if neigh in self.tiling and not self.pos_is_special_tile(neigh):
                to_return.append(self.tiling[neigh])
        return to_return

    def _update_growth_frontier_at_pos(self, pos: TilePosition):
        for _dir in DIRS:
            neigh = pos + _dir
            if (
                neigh not in self._growth_frontier
                and (
                    neigh not in self.tiling
                    or (
                        neigh in self.tiling
                        and self.pos_is_special_tile(neigh)
                        and self.tiling[neigh] == ManyTilesCanFit
                    )
                )
                and len(self.neighbouring_tiles(neigh)) >= 2
            ):
                self._growth_frontier.add(neigh)

    def _compute_growth_frontier(self):
        """The growth frontier is defined as any empty position that is adjacent to more than one tile."""
        self._growth_frontier = set({})
        for pos in self.tiling:
            self._update_growth_frontier_at_pos(pos)

    def pos_is_special_tile(self, pos):
        return pos in self.tiling and isinstance(self.tiling[pos], str)

    def get_possible_tiles_given_constraints(
        self, constraints: SquareGlues
    ) -> list[SquareGlues]:
        tiles = []
        for tile in self.tileset:
            fit = True
            for i in range(4):
                if tile[i] != constraints[i] and constraints[i] is not None:
                    fit = False
                    break
            if fit:
                tiles.append(tile)
        return tiles

    def get_constraints_at_pos(self, pos: TilePosition) -> SquareGlues:
        if pos in self.tiling and not self.pos_is_special_tile(pos):
            return self.tiling[pos]

        constraints = SquareGlues()

        for i, _dir in enumerate(DIRS):
            neigh = pos + _dir
            if neigh in self.tiling and not self.pos_is_special_tile(neigh):
                constraints[i] = self.tiling[neigh][(i + 2) % 4]
        return constraints

    def get_possible_tiles_at_pos(self, pos: TilePosition) -> list[SquareGlues]:
        constraints = self.get_constraints_at_pos(pos)
        return self.get_possible_tiles_given_constraints(constraints)

    def step(self, synchronous=False) -> int:
        if self._growth_frontier is None:
            self._compute_growth_frontier()

        events = []

        for pos in self._growth_frontier:
            tiles = self.get_possible_tiles_at_pos(pos)
            if len(tiles) == 0:
                events.append((pos, NoTileCanFit))
            elif len(tiles) > 1:
                events.append((pos, ManyTilesCanFit))
            else:
                events.append((pos, tiles[0]))
            if not synchronous and pos not in self.tiling:
                break

        for pos, tile in events:
            self.tiling[pos] = tile

            if self.pos_is_special_tile(pos):
                self._growth_frontier.remove(pos)
                continue
            self._growth_frontier.remove(pos)
            self._update_growth_frontier_at_pos(pos)

        return len(events)

    def all_steps(self):
        while self.step(True) != 0:
            continue
