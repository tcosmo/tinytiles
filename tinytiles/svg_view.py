import drawsvg as draw
from tinytiles.tiling import (
    Tiling,
    SquareGlues,
    NoTileCanFit,
    ManyTilesCanFit,
)
from tinytiles.utils_2D import TilePosition

TILE_SIZE = 32
null_glue_color = "#CACACA"
color_wheel = ["#E6C58F", "#0AC52E", "#E37998", "#3FB3F3"]
color_no_tile_can_fit = "#ff0000"
color_many_tiles_can_fit = "#00af00"
special_tiles_opacity = 0.3


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


def tile_edges_to_svg(tile, tile_center_x, tile_center_y):
    edges_group = draw.Group()
    # The following was found by trial and error
    a = [-1, 1, 1, -1]
    b = [-1, -1, 1, 1]
    c = [1, 0, -1, 0]
    e = [0, 1, 0, -1]

    def edge_name_to_svg(side, glue):
        tweak_x = [0, -4, 0, 3.5]
        tweak_y = [8.5, 2, -2, 2]

        if glue is None:
            return draw.NoElement()

        return draw.Text(
            str(glue),
            8,
            tile_center_x + (a[side] + c[side]) * (TILE_SIZE / 2) + tweak_x[side],
            tile_center_y + (b[side] + e[side]) * (TILE_SIZE) / 2 + tweak_y[side],
            fill="black",
            text_anchor="middle",
            valign="middle",
            font_family="Arimo",
        )

    for side in range(0, 4):
        glue = tile[side]
        color = "transparent"
        if glue is not None:
            color = color_wheel[glue]
        p = draw.Path(
            stroke="gray",
            stroke_width=0.5,
            fill=color,
            fill_opacity=1,
            marker_end=None,
        )
        p.M(tile_center_x, tile_center_y)
        p.l(a[side] * (TILE_SIZE / 2), b[side] * (TILE_SIZE / 2))
        p.l(c[side] * (TILE_SIZE), e[side] * (TILE_SIZE))
        p.Z()
        triangle_group = draw.Group([p])
        triangle_group.children.append(edge_name_to_svg(side, glue))
        edges_group.append(triangle_group)

    return edges_group


def tile_name_to_svg(tiling, tile, tile_center_x, tile_center_y):
    if tile in tiling.tileset:
        tweak_offset_x = -0.5
        tweak_offset_y = 4.2
        tile_name = str(tiling.tileset.index(tile))
        return draw.Text(
            str(tile_name),
            13,
            tile_center_x + tweak_offset_x,
            tile_center_y + tweak_offset_y,
            fill="black",
            text_anchor="middle",
            valign="middle",
            font_weight="bold",
            font_family="Arimo",
        )
    return draw.NoElement()


def tile_to_svg(
    tiling: Tiling,
    position: TilePosition,
    tile: SquareGlues | str,
    bounding_box: tuple[int, int, int, int],
):
    svg_position = tile_pos_to_svg_pos(position, bounding_box)
    svg_tile = draw.Group()

    fill_color = null_glue_color

    if type(tile) == str:
        if tile == NoTileCanFit:
            fill_color = color_no_tile_can_fit
        elif tile == ManyTilesCanFit:
            fill_color = color_many_tiles_can_fit

    # Tile square
    svg_tile.append(
        draw.Rectangle(
            svg_position.x,
            svg_position.y,
            TILE_SIZE,
            TILE_SIZE,
            stroke="gray",
            stroke_width=1,
            fill=fill_color,
            fill_opacity=1 if type(tile) != str else special_tiles_opacity,
        )
    )

    if type(tile) == str:
        return svg_tile

    tile_center_x = svg_position.x + TILE_SIZE / 2
    tile_center_y = svg_position.y + TILE_SIZE / 2

    svg_tile.append(tile_edges_to_svg(tile, tile_center_x, tile_center_y))

    svg_tile.append(tile_name_to_svg(tiling, tile, tile_center_x, tile_center_y))

    return svg_tile


def tiling_to_svg(
    tiling: Tiling,
    hihghlight_positions: list[TilePosition | tuple[TilePosition, str]] = [],
) -> draw.Drawing:
    min_x, min_y, w, h = tiling.bounding_box()
    svg = draw.Drawing(TILE_SIZE * w, TILE_SIZE * h)
    for position in tiling:
        svg.append(
            tile_to_svg(tiling, position, tiling[position], (min_x, min_y, w, h))
        )

    for elem in hihghlight_positions:
        try:
            pos, color = elem
            svg_pos = tile_pos_to_svg_pos(pos, (min_x, min_y, w, h))
            svg.append(
                draw.Rectangle(
                    svg_pos.x,
                    svg_pos.y,
                    TILE_SIZE,
                    TILE_SIZE,
                    stroke=color,
                    stroke_width=2,
                    fill=color,
                    fill_opacity=0.4,
                )
            )
        except Exception as _:
            pos = elem
            svg_pos = tile_pos_to_svg_pos(pos, (min_x, min_y, w, h))
            svg.append(
                draw.Rectangle(
                    svg_pos.x,
                    svg_pos.y,
                    TILE_SIZE,
                    TILE_SIZE,
                    stroke="blue",
                    stroke_width=2,
                    fill="transparent",
                )
            )
    return svg
