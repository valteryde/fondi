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
