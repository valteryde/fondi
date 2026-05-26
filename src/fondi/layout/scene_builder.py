from __future__ import annotations

from ..scene import Node


def collect_children(offset: tuple[float, float], *layouts) -> list[Node]:
    nodes: list[Node] = []
    for layout in layouts:
        nodes.extend(layout.collect_scene(offset))
    return nodes
