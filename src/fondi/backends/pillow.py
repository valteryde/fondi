from __future__ import annotations

import math

from PIL import Image, ImageDraw

from ..metrics import load_font
from ..raster_symbols import load_symbol_image
from ..path_util import sample_path_subpaths
from ..scene import (
    Color,
    Ellipse,
    Line,
    Node,
    Path as ScenePath,
    Polyline,
    RasterSymbol,
    Rect,
    Scene,
    TextRun,
)

IMGMODE = "RGBA"
_POLYLINE_SUPERSAMPLE = 2
_POLYLINE_SUPERSAMPLE_MIN_POINTS = 40


def _fondi_y_to_pil(y: float, scene_height: float) -> float:
    return scene_height - y


def _draw_polyline(
    draw: ImageDraw.ImageDraw,
    surface: Image.Image,
    pil_points: list[tuple[float, float]],
    stroke: Color,
    width: float,
) -> None:
    if len(pil_points) < 2:
        return
    line_width = max(1, int(round(width)))
    if len(pil_points) < _POLYLINE_SUPERSAMPLE_MIN_POINTS:
        draw.line(
            pil_points,
            fill=stroke,
            width=line_width,
            joint="curve",
        )
        return

    scale = _POLYLINE_SUPERSAMPLE
    xs = [p[0] for p in pil_points]
    ys = [p[1] for p in pil_points]
    pad = line_width * scale + 2
    x0 = min(xs) - pad
    y0 = min(ys) - pad
    x1 = max(xs) + pad
    y1 = max(ys) + pad
    layer_w = max(1, int(math.ceil(x1 - x0)))
    layer_h = max(1, int(math.ceil(y1 - y0)))
    layer = Image.new(IMGMODE, (layer_w * scale, layer_h * scale), (0, 0, 0, 0))
    layer_draw = ImageDraw.Draw(layer)
    scaled = [
        ((x - x0) * scale, (y - y0) * scale) for x, y in pil_points
    ]
    layer_draw.line(
        scaled,
        fill=stroke,
        width=line_width * scale,
        joint="curve",
    )
    layer = layer.resize((layer_w, layer_h), Image.Resampling.LANCZOS)
    surface.paste(layer, (int(x0), int(y0)), layer)


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
        _draw_polyline(draw, surface, pil_points, node.stroke, node.stroke_width)
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
    elif isinstance(node, ScenePath):
        width = int(max(1, node.stroke_width))
        for subpath in sample_path_subpaths(node.d):
            pil_points = [
                (x, _fondi_y_to_pil(y, scene_height)) for x, y in subpath
            ]
            if pil_points:
                draw.line(
                    pil_points,
                    fill=node.stroke,
                    width=width,
                    joint="curve",
                )
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
