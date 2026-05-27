from __future__ import annotations

from PIL import Image, ImageDraw

from ..metrics import load_font
from ..raster_symbols import load_symbol_image
from ..scene import (
    Color,
    Ellipse,
    Line,
    Node,
    Polyline,
    RasterSymbol,
    Rect,
    Scene,
    TextRun,
)

IMGMODE = "RGBA"


def _fondi_y_to_pil(y: float, scene_height: float) -> float:
    return scene_height - y


def _load_symbol_image(asset_id: str, width: int, height: int, fill: Color) -> Image.Image:
    return load_symbol_image(asset_id, width, height, fill)


def _render_node(
    draw: ImageDraw.ImageDraw,
    surface: Image.Image,
    node: Node,
    scene_height: float,
) -> None:
    if isinstance(node, TextRun):
        font = load_font(int(node.font_size), node.style)
        pil_x = node.x
        pil_y = _fondi_y_to_pil(node.y, scene_height)
        draw.text((pil_x, pil_y), node.text, node.fill, font=font, anchor="ms")
    elif isinstance(node, Line):
        draw.line(
            (
                node.x1,
                _fondi_y_to_pil(node.y1, scene_height),
                node.x2,
                _fondi_y_to_pil(node.y2, scene_height),
            ),
            fill=node.stroke,
            width=int(node.stroke_width),
        )
    elif isinstance(node, Polyline):
        pil_points = [
            (x, _fondi_y_to_pil(y, scene_height)) for x, y in node.points
        ]
        draw.line(pil_points, fill=node.stroke, width=int(node.stroke_width))
    elif isinstance(node, Ellipse):
        x0 = node.x
        y1 = _fondi_y_to_pil(node.y + node.height, scene_height)
        x1 = node.x + node.width
        y0 = _fondi_y_to_pil(node.y, scene_height)
        draw.ellipse((x0, y1, x1, y0), fill=node.fill)
    elif isinstance(node, Rect):
        x0 = node.x
        y1 = _fondi_y_to_pil(node.y + node.height, scene_height)
        x1 = node.x + node.width
        y0 = _fondi_y_to_pil(node.y, scene_height)
        draw.rectangle((x0, y1, x1, y0), fill=node.fill)
    elif isinstance(node, RasterSymbol):
        symbol = _load_symbol_image(
            node.asset_id,
            int(node.width),
            int(node.height),
            node.fill,
        )
        if node.flip_x:
            symbol = symbol.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        pil_x = int(node.x)
        pil_y = int(_fondi_y_to_pil(node.y + node.height, scene_height))
        surface.paste(symbol, (pil_x, pil_y), symbol)


def render_pillow(scene: Scene) -> Image.Image:
    width = max(int(scene.width), 0)
    height = max(int(scene.height), 0)
    if width == 0 or height == 0:
        return Image.new(IMGMODE, (0, 0))
    surface = Image.new(IMGMODE, (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(surface)
    for node in scene.children:
        _render_node(draw, surface, node, height)
    return surface
