
from .layout import *
from ..mathtext import MathText
from ..scene import Ellipse, Line, Polyline
import math

GAPPROCENT = 0.1


class TextDecorationLayout(Layout):

    def __init__(self, parent, content, decoration):
        super().__init__()

        self.fontSize = parent.fontSize
        self.color = parent.color
        self.content = MathText(content, self.fontSize, self.color)
        self.decoration = decoration
        self._deco_nodes: list = []
        self._deco_width = 0
        self._deco_height = 0

    def _finalize_layout(self):
        gap = int(self.fontSize * GAPPROCENT)
        self._gap = gap
        self.width = max(self.content.width, self._deco_width)
        self.height = self.content.height + self._deco_height + gap

    def collect_scene(self, offset: tuple[float, float]) -> list:
        ox, oy = offset
        nodes = []
        content_x = ox + (self.width - self.content.width) / 2
        nodes.extend(self.content.collect_scene((content_x, oy)))

        deco_left = ox + (self.width - self._deco_width) / 2
        deco_base = oy + self.content.height + self._gap
        for node in self._deco_nodes:
            if isinstance(node, Ellipse):
                nodes.append(
                    Ellipse(
                        deco_left + node.x,
                        deco_base + node.y,
                        node.width,
                        node.height,
                        node.fill,
                    )
                )
            elif isinstance(node, Line):
                nodes.append(
                    Line(
                        deco_left + node.x1,
                        deco_base + node.y1,
                        deco_left + node.x2,
                        deco_base + node.y2,
                        node.stroke,
                        node.stroke_width,
                    )
                )
            elif isinstance(node, Polyline):
                points = [
                    (deco_left + x, deco_base + y) for x, y in node.points
                ]
                nodes.append(Polyline(points, node.stroke, node.stroke_width))
        return nodes


class DotLayout(TextDecorationLayout):
    def __init__(self, parent, content):
        super().__init__(parent, content, "dot")
        dotsize = int(self.fontSize * 0.2)
        self._deco_width = dotsize
        self._deco_height = dotsize
        self._deco_nodes = [Ellipse(0, 0, dotsize, dotsize, self.color)]
        self._finalize_layout()


class DDotLayout(TextDecorationLayout):
    def __init__(self, parent, content):
        super().__init__(parent, content, "ddot")
        dotsize = int(self.fontSize * 0.2)
        gap = int(dotsize * 0.6)
        self._deco_width = dotsize * 2 + gap
        self._deco_height = dotsize
        self._deco_nodes = [
            Ellipse(0, 0, dotsize, dotsize, self.color),
            Ellipse(dotsize + gap, 0, dotsize, dotsize, self.color),
        ]
        self._finalize_layout()


class BarLayout(TextDecorationLayout):
    def __init__(self, parent, content):
        super().__init__(parent, content, "bar")
        linewidth = max(1, int(self.fontSize * 0.1))
        self._deco_width = self.content.width
        self._deco_height = linewidth
        self._deco_nodes = [
            Line(0, 0, self.content.width, 0, self.color, linewidth),
        ]
        self._finalize_layout()


class TildeLayout(TextDecorationLayout):
    def __init__(self, parent, content):
        super().__init__(parent, content, "tilde")
        linewidth = max(1, int(self.fontSize * 0.1))
        amplitude = int(self.fontSize * 0.1)
        wavelength = int(self.fontSize * 0.4)
        points = []
        for x in range(0, int(self.content.width)):
            y = amplitude + int(
                amplitude * 0.9 * -1 * math.sin(2 * math.pi * x / wavelength)
            )
            points.append((x, y))
        self._deco_width = self.content.width
        self._deco_height = amplitude * 2
        self._deco_nodes = [Polyline(points, self.color, linewidth)]
        self._finalize_layout()


MACROS["\\dot"] = DotLayout
MACROS["\\ddot"] = DDotLayout
MACROS["\\tilde"] = TildeLayout
MACROS["\\bar"] = BarLayout
