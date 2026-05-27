from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Union

Color = tuple[int, int, int, int]
FontStyle = Literal["regular", "italic"]


@dataclass
class TextRun:
    text: str
    x: float
    y: float
    font_size: float
    style: FontStyle
    fill: Color


@dataclass
class Line:
    x1: float
    y1: float
    x2: float
    y2: float
    stroke: Color
    stroke_width: float


@dataclass
class Polyline:
    points: list[tuple[float, float]]
    stroke: Color
    stroke_width: float


@dataclass
class Ellipse:
    x: float
    y: float
    width: float
    height: float
    fill: Color


@dataclass
class Rect:
    x: float
    y: float
    width: float
    height: float
    fill: Color


@dataclass
class RasterSymbol:
    asset_id: str
    x: float
    y: float
    width: float
    height: float
    fill: Color
    flip_x: bool = False


Node = Union[TextRun, Line, Polyline, Ellipse, Rect, RasterSymbol]


@dataclass
class Scene:
    width: float
    height: float
    children: list[Node]


def _node_bounds(node: Node) -> tuple[float, float, float, float]:
    """Return (left, bottom, right, top) in fondi y-up coordinates."""
    if isinstance(node, TextRun):
        from .metrics import measure_text

        metrics = measure_text(node.text, int(node.font_size), node.style)
        half = metrics.width / 2
        pad = max(1.0, node.font_size * 0.06)
        left = node.x - half
        right = node.x + half + pad
        bottom = node.y - metrics.bottom_line_delta
        top = node.y + (metrics.height - metrics.bottom_line_delta)
        return left, bottom, right, top
    if isinstance(node, Line):
        stroke_pad = node.stroke_width / 2
        left = min(node.x1, node.x2) - stroke_pad
        right = max(node.x1, node.x2) + stroke_pad
        bottom = min(node.y1, node.y2) - stroke_pad
        top = max(node.y1, node.y2) + stroke_pad
        return left, bottom, right, top
    if isinstance(node, Polyline):
        xs = [x for x, _ in node.points]
        ys = [y for _, y in node.points]
        stroke_pad = node.stroke_width / 2
        return (
            min(xs) - stroke_pad,
            min(ys) - stroke_pad,
            max(xs) + stroke_pad,
            max(ys) + stroke_pad,
        )
    if isinstance(node, (Ellipse, Rect, RasterSymbol)):
        return node.x, node.y, node.x + node.width, node.y + node.height
    raise TypeError(type(node))


def scene_size(children: list[Node]) -> tuple[float, float]:
    if not children:
        return 0.0, 0.0
    right = top = 0.0
    for node in children:
        _, _, node_right, node_top = _node_bounds(node)
        right = max(right, node_right)
        top = max(top, node_top)
    return right, top


def translate_node(node: Node, dx: float, dy: float) -> Node:
    if isinstance(node, TextRun):
        return TextRun(
            node.text, node.x + dx, node.y + dy, node.font_size, node.style, node.fill
        )
    if isinstance(node, Line):
        return Line(
            node.x1 + dx,
            node.y1 + dy,
            node.x2 + dx,
            node.y2 + dy,
            node.stroke,
            node.stroke_width,
        )
    if isinstance(node, Polyline):
        return Polyline(
            [(x + dx, y + dy) for x, y in node.points],
            node.stroke,
            node.stroke_width,
        )
    if isinstance(node, Ellipse):
        return Ellipse(
            node.x + dx, node.y + dy, node.width, node.height, node.fill
        )
    if isinstance(node, Rect):
        return Rect(node.x + dx, node.y + dy, node.width, node.height, node.fill)
    if isinstance(node, RasterSymbol):
        return RasterSymbol(
            node.asset_id,
            node.x + dx,
            node.y + dy,
            node.width,
            node.height,
            node.fill,
            node.flip_x,
        )
    raise TypeError(type(node))
