from typing import Dict
from tinytiles.utils_2D import *


class SquareGlues(object):
    """Represents the four squares of a Wang tile. Edge colors are given by int and can be None."""

    def __init__(
        self, north: int | None, east: int | None, south: int | None, west: int | None
    ):
        self.north: int | None = north
        self.east: int | None = east
        self.south: int | None = south
        self.west: int | None = west

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


class NoTileCanFit(object):
    """Represents the situation where no tile can fit at a position."""

    def __init__(self):
        pass


class ManyTilesCanFit(object):
    """Represents the situation where more than one tile can fit at a position."""

    def __init__(self):
        pass


class Tiling(object):
    def __init__(
        self,
        tileset: list[SquareGlues] | list[tuple[int, int, int, int]] = [],
        tiling={},
        _position=TilePosition(0, 0),
        copy_tiling=True,
    ):
        self.tileset: list[SquareGlues] = []
        if len(tileset) > 1 and type(tileset[0]) == tuple:
            for tiletype in tileset:
                self.tileset.append(SquareGlues(*tiletype))
        else:
            self.tileset: list[SquareGlues] = tileset

        if copy_tiling:
            self.tiling: Dict[
                TilePosition, SquareGlues | NoTileCanFit | ManyTilesCanFit
            ] = tiling.copy()
        else:
            self.tiling: Dict[
                TilePosition, SquareGlues | NoTileCanFit | ManyTilesCanFit
            ] = tiling

        self._position = _position  # position updated by factories

    def get_tile_from_id(self, tile: SquareGlues | int) -> SquareGlues:
        if type(tile) == int:
            return self.tileset[tile]
        return tile

    def put_tiles(self, tiles: list[SquareGlues | int], step_2D: TilePosition):
        new_tiling = self.tiling.copy()
        new_position = self._position
        for tile in tiles:
            tile = self.get_tile_from_id(tile)
            new_tiling[new_position] = tile
            new_position += step_2D

        return Tiling(self.tileset, new_tiling, new_position, copy_tiling=False)

    def bounding_box(self) -> tuple[int, int, int, int]:
        min_x, max_x = 0, 0
        min_y, max_y = 0, 0
        for position in self.tiling:
            min_x = min(min_x, position.x)
            max_x = max(max_x, position.x)
            min_y = min(min_y, position.y)
            max_y = max(max_y, position.y)
        return min_x, min_y, max_x - min_x + 1, max_y - min_y + 1

    def svg(self):
        from tinytiles.svg_view import tiling_to_svg

        return tiling_to_svg(self)

    def __getitem__(
        self, position: TilePosition
    ) -> SquareGlues | NoTileCanFit | ManyTilesCanFit:
        return self.tiling[position]

    def __iter__(self):
        for position in self.tiling:
            yield position
