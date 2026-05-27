
from .layout import *
from ..mathtext import MathText
from .parenthesis import DELIMITER_STROKE_WIDTH, PARATUBORWIDTHCOEFF
from .helper import boundingBox, unwrap_macro_arg
from .scene_builder import collect_children
from .delimiter_geom import cases_brace_nodes
import math

DISTSPACE = 0.75
PARAPADDING = 0.25
DISTLINES = 2


class _BraceSide(Layout):
    def __init__(self, width, height):
        super().__init__()
        self.width = width
        self.height = height


class Cases(Layout):

    def __init__(self, parent, *args):
        super().__init__()

        if len(args) % 2 == 0:
            cases = [(args[i * 2], args[i * 2 + 1]) for i in range(len(args) // 2)]
        else:
            cases = [
                (args[i * 2], args[i * 2 + 1])
                for i in range(len(args) // 2 - 1)
            ] + [(args[-1], "else")]

        self.fontSize = parent.fontSize
        self.color = parent.color

        self.cases = []
        for case, para in cases:
            left = MathText(unwrap_macro_arg(case), self.fontSize, self.color)
            left.setLeft(0)
            right = MathText(unwrap_macro_arg(para), self.fontSize, self.color)
            self.cases.append((left, right, max(left.height, right.height)))

        maxWidth = math.ceil(max(i[0].width for i in self.cases))

        GAPSIZE = WHITESPACESIZE * self.fontSize * DISTLINES
        sumHeight = parent.fontSize * PARAPADDING
        for left, right, height in self.cases:
            sumHeight += height
            right.setLeft(maxWidth + DISTSPACE * self.fontSize)
            right.setBottom(-sumHeight)
            left.setBottom(-sumHeight)
            sumHeight += GAPSIZE

        sumHeight += parent.fontSize * PARAPADDING - GAPSIZE
        brace_width = PARATUBORWIDTHCOEFF * self.fontSize
        self._stroke_width = self.fontSize * DELIMITER_STROKE_WIDTH
        self._brace_width = brace_width
        self._brace_height = int(sumHeight)

        self.para = _BraceSide(brace_width, int(sumHeight))
        self.para.setRight(self.cases[0][0].getLeft() - WHITESPACESIZE * self.fontSize)
        self.para.setTop(0)

        self.height = sumHeight

        parts = [self.para] + [c for case in self.cases for c in case[:2]]
        x, y, x1, y1 = boundingBox(*parts)

        self._bbox_offset = (x, y)
        self.width = x1 - x
        self.height = y1 - y
        self.setBottomLineDiffrence(-self.height / 2 + self.fontSize / 4)

    def collect_scene(
        self,
        corner: tuple[float, float] | tuple[float, float, float],
        root: tuple[float, float] | None = None,
        **kwargs,
    ) -> list:
        bx, by = self._bbox_offset
        origin_x, origin_y = corner[0], corner[1]
        parts = [c for case in self.cases for c in case[:2]]
        nodes = collect_children(
            self, (bx, by), *parts, root=root, scene_corner=corner
        )
        nodes.extend(
            cases_brace_nodes(
                origin_x + self.para.getLeft() - bx,
                origin_y + self.para.getBottom() - by,
                self._brace_width,
                self._brace_height,
                self._stroke_width,
                self.color,
            )
        )
        return nodes

    def __repr__(self):
        return "\\cases{...}"


MACROS["\\cases"] = Cases
