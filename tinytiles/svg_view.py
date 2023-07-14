import drawsvg as draw
from tinytiles.tiling import Tiling, SquareGlues
from tinytiles.utils_2D import TilePosition

TILE_SIZE = 32
null_glue_color = "#CACACA"
color_wheel = ["#E6C58F", "#0AC52E", "#E37998", "#3FB3F3"]


def random_color() -> str:
    import random

    random_number = random.randint(0, 16777215)
    hex_number = str(hex(random_number))
    hex_number = "#" + hex_number[2:]
    return hex_number


class SvgPosition(TilePosition):
    pass


def tile_pos_to_svg_pos(
    position: TilePosition,
    bounding_box: tuple[int, int, int, int],
) -> SvgPosition:
    min_x, min_y, w, h = bounding_box
    max_y = min_y + h
    return SvgPosition(
        (position.x - min_x) * TILE_SIZE,
        (-1 * position.y + max_y - 1) * TILE_SIZE,
    )


def tile_to_svg(
    tiling: Tiling,
    position: TilePosition,
    tile: SquareGlues,
    bounding_box: tuple[int, int, int, int],
):
    svg_position = tile_pos_to_svg_pos(position, bounding_box)
    svg_tile = draw.Group()
    svg_tile.append(
        draw.Rectangle(
            svg_position.x, svg_position.y, TILE_SIZE, TILE_SIZE, fill=random_color()
        )
    )
    svg_tile.append(
        draw.Text(
            str(tiling.tileset.index(tile)),
            20,
            svg_position.x,
            svg_position.y + 20,
            color="#000000",
        )
    )
    return svg_tile


def tiling_to_svg(tiling: Tiling) -> draw.Drawing:
    min_x, min_y, w, h = tiling.bounding_box()
    svg = draw.Drawing(TILE_SIZE * w, TILE_SIZE * h)
    for position in tiling:
        svg.append(
            tile_to_svg(tiling, position, tiling[position], (min_x, min_y, w, h))
        )
    return svg
