
from .layout import *
from ..mathtext import MathText
from ..plain import Symbol
from .parenthesis import PARATUBORWIDTHCOEFF
from .helper import boundingBox, unwrap_macro_arg
from .scene_builder import collect_children
import math

DISTSPACE = 0.75
PARAPADDING = 0.25
DISTLINES = 2


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
        self.para = Symbol(
            "tuborpara_left.png",
            PARATUBORWIDTHCOEFF * self.fontSize,
            int(sumHeight),
            self.color,
        )
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
        parts = [self.para] + [c for case in self.cases for c in case[:2]]
        return collect_children(
            self, (bx, by), *parts, root=root, scene_corner=corner
        )

    def __repr__(self):
        return "\\cases{...}"


MACROS["\\cases"] = Cases
