
from .helper import boundingBox
from .layout import Layout, MACROS
from ..mathtext import MathText
from .scene_builder import collect_children
from ..parser.parser import parse
from ..parser.tokens import ARGUMENT, FULLCOMMAND

SUBSUPSIZE = 0.75
SUBSUPPOS = 0.25


def determineSuberSubHandledInteranally(parent, tokens, lower="", upper=""):
    if len(tokens) == 0:
        return

    tokens = parse(tokens)

    if len(tokens) > 1:
        return

    tokens = tokens[0]

    if tokens[0] == ARGUMENT:
        tokens = parse(tokens[1])

        if len(tokens) != 1:
            return

        tokens = tokens[0]

    if tokens[0] == FULLCOMMAND:
        return MACROS[tokens[1]["name"]].handleSuperSub(
            parent, tokens[1]["args"], lower, upper
        )


class SuperLayout(Layout):

    def __init__(self, parent, base, upper):
        super().__init__()

        r = determineSuberSubHandledInteranally(parent, base, "", upper)
        if r:
            return self.copy(r)

        self.fontSize = parent.fontSize
        self.color = parent.color

        self.base = MathText(base, self.fontSize, self.color)
        self.base.setCenter(0, 0)
        self.upper = MathText(upper, int(self.fontSize * SUBSUPSIZE), self.color)

        self.upper.setBottom(int(self.base.height * SUBSUPPOS))
        self.upper.setLeft(self.base.getRight())
        x, y, x1, y1 = boundingBox(self.base, self.upper)

        self._bbox_offset = (x, y)
        self.width = x1 - x
        self.height = y1 - y
        self._children = (self.base, self.upper)

    def collect_scene(self, offset: tuple[float, float]) -> list:
        ox, oy = offset
        bx, by = self._bbox_offset
        return collect_children((ox + bx, oy + by), *self._children)

    def __repr__(self):
        return "({})^{}({})".format(self.base, self.upper)


class SubLayout(Layout):

    def __init__(self, parent, base, lower):
        super().__init__()

        r = determineSuberSubHandledInteranally(parent, base, lower, "")
        if r:
            return self.copy(r)

        self.fontSize = parent.fontSize
        self.color = parent.color

        self.base = MathText(base, self.fontSize, self.color)
        self.lower = MathText(lower, int(self.fontSize * SUBSUPSIZE), self.color)
        self.base.setCenter(0, 0)

        self.lower.setTop(-int(self.base.height * SUBSUPPOS))
        self.lower.setLeft(self.base.getRight())
        x, y, x1, y1 = boundingBox(self.base, self.lower)

        self._bbox_offset = (x, y)
        self.width = x1 - x
        self.height = y1 - y
        self._children = (self.base, self.lower)
        self.setBottomLineDiffrence(self.lower.getBottom() - self.base.getBottom())

    def collect_scene(self, offset: tuple[float, float]) -> list:
        ox, oy = offset
        bx, by = self._bbox_offset
        return collect_children((ox + bx, oy + by), *self._children)

    def __repr__(self):
        return "({})_({})".format(self.base, self.lower)


class SubSuperLayout(Layout):

    def __init__(self, parent, base, lower, upper):
        super().__init__()

        r = determineSuberSubHandledInteranally(parent, base, lower, upper)
        if r:
            return self.copy(r)

        self.fontSize = parent.fontSize
        self.color = parent.color

        self.base = MathText(base, self.fontSize, self.color)
        self.upper = MathText(upper, int(self.fontSize * SUBSUPSIZE), self.color)
        self.lower = MathText(lower, int(self.fontSize * SUBSUPSIZE), self.color)
        self.base.setCenter(0, 0)

        self.upper.setBottom(int(self.base.height * SUBSUPPOS))
        self.upper.setLeft(self.base.getRight())
        self.lower.setTop(-int(self.base.height * SUBSUPPOS))
        self.lower.setLeft(self.base.getRight())
        x, y, x1, y1 = boundingBox(self.base, self.upper, self.lower)

        self._bbox_offset = (x, y)
        self.width = x1 - x
        self.height = y1 - y
        self._children = (self.base, self.upper, self.lower)
        self.setBottomLineDiffrence(self.lower.getBottom() - self.base.getBottom())

    def collect_scene(self, offset: tuple[float, float]) -> list:
        ox, oy = offset
        bx, by = self._bbox_offset
        return collect_children((ox + bx, oy + by), *self._children)

    def __repr__(self):
        return "{}^{}_{}".format(self.base, self.upper, self.lower)


class SuperSubLayout(SubSuperLayout):
    def __init__(self, parent, base, upper, lower):
        super().__init__(parent, base, lower, upper)


MACROS["\\sub"] = SubLayout
MACROS["\\super"] = SuperLayout
MACROS["\\subsuper"] = SubSuperLayout
MACROS["\\supersub"] = SuperSubLayout
