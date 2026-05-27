from __future__ import annotations

from ..scene import Color, Node, Polyline
from .delimiter_data import BRACE_CENTERLINE, PAREN_CENTERLINE

_PAREN_HOOK_FRAC = 0.22
_BRACE_EAR_FRAC = 0.16
# Linear chords between traced knots look jagged in PNG; interpolate densely.
_STEPS_PER_SEGMENT = 16


def _map_extent_y(fy: float, height: float, hook_frac: float) -> float:
    """Map normalized y (0=glyph bottom, 1=glyph top) to fondi y with fixed hooks."""
    hook_h = min(height / 2, height * hook_frac)
    if height <= 2 * hook_h:
        return fy * height
    if fy <= hook_frac:
        t = fy / hook_frac
        return t * hook_h
    if fy >= 1.0 - hook_frac:
        t = (fy - (1.0 - hook_frac)) / hook_frac
        return height - hook_h + t * hook_h
    t = (fy - hook_frac) / (1.0 - 2 * hook_frac)
    return hook_h + t * (height - 2 * hook_h)


def _densify(waypoints: list[tuple[float, float]]) -> list[tuple[float, float]]:
    if len(waypoints) < 2:
        return waypoints
    dense: list[tuple[float, float]] = []
    for i in range(len(waypoints) - 1):
        x0, y0 = waypoints[i]
        x1, y1 = waypoints[i + 1]
        for step in range(_STEPS_PER_SEGMENT + (0 if i else 1)):
            t = step / _STEPS_PER_SEGMENT
            dense.append((x0 + (x1 - x0) * t, y0 + (y1 - y0) * t))
    return dense


def _centerline_polyline(
    knots: list[tuple[float, float]],
    side_x: float,
    bottom: float,
    width: float,
    height: float,
    hook_frac: float,
) -> list[tuple[float, float]]:
    waypoints = [
        (side_x + fx * width, bottom + _map_extent_y(fy, height, hook_frac))
        for fx, fy in knots
    ]
    return _densify(waypoints)


def _mirror_points(
    points: list[tuple[float, float]], x_min: float, x_max: float
) -> list[tuple[float, float]]:
    cx = (x_min + x_max) / 2
    return [(2 * cx - x, y) for x, y in points]


def round_paren_nodes(
    side_x: float,
    bottom: float,
    width: float,
    height: float,
    stroke_width: float,
    color: Color,
    *,
    right: bool = False,
) -> list[Node]:
    points = _centerline_polyline(
        PAREN_CENTERLINE, side_x, bottom, width, height, _PAREN_HOOK_FRAC
    )
    if right:
        points = _mirror_points(points, side_x, side_x + width)
    return [Polyline(points, color, stroke_width)]


def cases_brace_nodes(
    side_x: float,
    bottom: float,
    width: float,
    height: float,
    stroke_width: float,
    color: Color,
) -> list[Node]:
    points = _centerline_polyline(
        BRACE_CENTERLINE, side_x, bottom, width, height, _BRACE_EAR_FRAC
    )
    return [Polyline(points, color, stroke_width)]
