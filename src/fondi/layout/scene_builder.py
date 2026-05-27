from __future__ import annotations

from ..mathtext import MathText
from ..plain import PlainText
from ..plain.symbol import Symbol
from ..scene import Node, RasterSymbol, TextRun
from .layout import Layout


def composite_origin(
    parent: Layout, ox: float, oy: float, bx: float, by: float
) -> tuple[float, float]:
    """Bottom-left of parent composite in scene coords (matches v0.1.6 paste offset)."""
    return parent.getLeft() - bx - ox, parent.getBottom() - oy - by


def collect_children(
    parent: Layout,
    paste: tuple[float, float] | tuple[float, float, float],
    *layouts: Layout,
    root: tuple[float, float] | None = None,
    scene_corner: tuple[float, float] | None = None,
) -> list[Node]:
    """
    paste: v0.1.6 paste offset (bbox min) for siblings composited under parent.
    root: root MathText line-bbox paste offset (scene origin).
    scene_corner: bottom-left of parent composite in scene coords (if already known).
    """
    px, py = paste[0], paste[1]
    rox, roy = (root[0], root[1]) if root is not None else (px, py)
    bx, by = getattr(parent, "_bbox_offset", (0.0, 0.0))
    if scene_corner is not None:
        corner_x, corner_y = scene_corner[0], scene_corner[1]
    else:
        corner_x = parent.getLeft() - rox
        corner_y = parent.getBottom() - roy
    nodes: list[Node] = []

    for layout in layouts:
        if isinstance(parent, MathText):
            lx, ly = parent._line_bbox_offset()
            if isinstance(layout, PlainText):
                if scene_corner is not None:
                    world_x = corner_x + layout.getLeft() - lx + layout.width / 2
                    baseline_y = (
                        corner_y
                        + layout.getBottom()
                        - ly
                        - layout.bottomLineDiffrence
                    )
                else:
                    world_x = parent.getLeft() + layout.getLeft() - rox + layout.width / 2
                    baseline_y = (
                        parent.getBottom()
                        + layout.getBottom()
                        - roy
                        - layout.bottomLineDiffrence
                    )
                nodes.append(
                    TextRun(
                        layout.text,
                        world_x,
                        baseline_y,
                        layout.fontSize,
                        layout.style,
                        layout.color,
                    )
                )
            elif isinstance(layout, Symbol):
                if scene_corner is not None:
                    sx = corner_x + layout.getLeft() - lx
                    sy = corner_y + layout.getBottom() - ly
                else:
                    sx = parent.getLeft() + layout.getLeft() - rox
                    sy = parent.getBottom() + layout.getBottom() - roy
                nodes.append(
                    RasterSymbol(
                        layout.fname,
                        sx,
                        sy,
                        layout.width,
                        layout.height,
                        layout.color,
                    )
                )
            elif isinstance(layout, MathText):
                nodes.extend(
                    layout.collect_scene(relayout=False, root=(rox, roy))
                )
            else:
                if scene_corner is not None:
                    child_corner = (
                        corner_x + layout.getLeft() - lx,
                        corner_y + layout.getBottom() - ly,
                    )
                else:
                    child_corner = (
                        layout.getLeft() - rox,
                        layout.getBottom() - roy,
                    )
                nodes.extend(
                    layout.collect_scene(child_corner, root=(rox, roy))
                )
        else:
            child_corner = (
                corner_x + layout.getLeft() - bx,
                corner_y + layout.getBottom() - by,
            )
            if isinstance(layout, PlainText):
                nodes.append(
                    TextRun(
                        layout.text,
                        child_corner[0] + layout.width / 2,
                        child_corner[1]
                        - layout.bottomLineDiffrence,
                        layout.fontSize,
                        layout.style,
                        layout.color,
                    )
                )
            elif isinstance(layout, Symbol):
                nodes.append(
                    RasterSymbol(
                        layout.fname,
                        child_corner[0],
                        child_corner[1],
                        layout.width,
                        layout.height,
                        layout.color,
                    )
                )
            elif isinstance(layout, MathText):
                nodes.extend(layout.collect_scene(child_corner, root=(rox, roy)))
            else:
                nodes.extend(layout.collect_scene(child_corner, root=(rox, roy)))
    return nodes
