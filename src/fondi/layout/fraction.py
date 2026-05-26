
from .layout import *
from ..mathtext import MathText
from .helper import boundingBox
from .scene_builder import collect_children
from ..scene import Line

FRACFONTWIDTHCOEFF = 0.05
FRACPADDINGCOEFF = 0.1
FRACSHRINKCOEFF = 0.75


class FracLayout(Layout):

    def __init__(self, parent, top, bottom):
        super().__init__()

        self.fontSize = parent.fontSize
        self.color = parent.color

        self.top = MathText(top, int(self.fontSize * FRACSHRINKCOEFF), self.color)
        self.bottom = MathText(bottom, int(self.fontSize * FRACSHRINKCOEFF), self.color)

        linewidth = int(FRACFONTWIDTHCOEFF * self.fontSize)
        self.padding = FRACPADDINGCOEFF * self.fontSize + linewidth / 2
        self.width = max(self.bottom.width, self.top.width)
        self.height = self.bottom.height + self.top.height + self.padding * 2

        self.top.setBottom(self.padding)
        self.top.setCenter(x=self.width / 2)

        self.bottom.setTop(-self.padding)
        self.bottom.setCenter(x=self.width / 2)

        x, y, x1, y1 = boundingBox(self.bottom, self.top)
        self.setBottomLineDiffrence(y + self.fontSize / 4)

        self._bbox_offset = (x, y)
        self._frac_line_y = -y
        self._frac_line_width = linewidth

    def collect_scene(self, offset: tuple[float, float]) -> list:
        ox, oy = offset
        bx, by = self._bbox_offset
        nodes = collect_children((ox + bx, oy + by), self.top, self.bottom)
        line_y = oy + self._frac_line_y
        nodes.append(
            Line(
                ox + bx,
                line_y,
                ox + bx + self.width,
                line_y,
                self.color,
                self._frac_line_width,
            )
        )
        return nodes

    def __repr__(self):
        return "({})/({})".format(self.top, self.bottom)


MACROS["\\frac"] = FracLayout
