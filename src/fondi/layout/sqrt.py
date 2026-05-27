
from .helper import boundingBox, unwrap_macro_arg
from .layout import Layout, MACROS
from ..mathtext import MathText
from .scene_builder import collect_children, composite_origin
from ..scene import Polyline
import math


class SqrtLayout(Layout):
    def __init__(self, parent, *args):
        super().__init__()

        self.inner = MathText(unwrap_macro_arg(args[0]), parent.fontSize, color=parent.color)

        self.linewidth = 3
        self.fontSize = parent.fontSize
        self.color = parent.color
        self.padding = self.fontSize // 5
        self.height = int(self.inner.height + self.padding)

        self.angle = math.radians(60)

        c = self.inner.height / math.sin(self.angle)
        line1 = (0, self.height / 2), (math.cos(self.angle) * c / 2, self.height)
        line2 = line1[1], (math.cos(self.angle) * c + line1[0][0], 0)

        self.width = int(self.inner.width + self.linewidth * 2 + line2[1][0] + self.padding)

        line3 = line2[1], (self.width, line2[1][1])
        self._sqrt_points = [*line1, *line2, *line3]

        self.inner.setBottom(0)
        self.inner.setLeft(line3[0][0] + self.padding / 2)

        x, y, _, _ = boundingBox(self.inner)
        self._bbox_offset = (x, y)

    def collect_scene(
        self,
        corner: tuple[float, float] | tuple[float, float, float],
        root: tuple[float, float] | None = None,
        **kwargs,
    ) -> list:
        bx, by = self._bbox_offset
        origin_x, origin_y = corner[0], corner[1]
        nodes = collect_children(
            self, (bx, by), self.inner, root=root, scene_corner=corner
        )
        points = [
            (origin_x + px, origin_y + py) for px, py in self._sqrt_points
        ]
        nodes.append(
            Polyline(points, self.color, self.linewidth)
        )
        return nodes

    def __repr__(self):
        return "\\sqrt{{{}}}".format(self.inner)


MACROS["\\sqrt"] = SqrtLayout
