
from .layout import *
from ..mathtext import MathText
from .helper import boundingBox, unwrap_macro_arg
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

        self.top = MathText(unwrap_macro_arg(top), int(self.fontSize * FRACSHRINKCOEFF), self.color)
        self.bottom = MathText(unwrap_macro_arg(bottom), int(self.fontSize * FRACSHRINKCOEFF), self.color)

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

    def collect_scene(
        self,
        corner: tuple[float, float] | tuple[float, float, float],
        root: tuple[float, float] | None = None,
        **kwargs,
    ) -> list:
        bx, by = self._bbox_offset
        paste = (bx, by)
        nodes = collect_children(
            self, paste, self.top, self.bottom, root=root, scene_corner=corner
        )
        origin_x = corner[0]
        origin_y = corner[1]
        line_y = origin_y + self._frac_line_y
        nodes.append(
            Line(
                origin_x,
                line_y,
                origin_x + self.width,
                line_y,
                self.color,
                self._frac_line_width,
            )
        )
        return nodes

    def __repr__(self):
        return "({})/({})".format(self.top, self.bottom)


MACROS["\\frac"] = FracLayout
