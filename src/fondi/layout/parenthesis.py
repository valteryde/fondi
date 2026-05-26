
from .helper import boundingBox
from .layout import Layout, MACROS, WHITESPACESIZE
from ..plain import Symbol
from ..mathtext import MathText
from .scene_builder import collect_children
from ..scene import Rect

FONTSIZELINEWIDTH = 0.05
PARANORMALWIDTHCOEFF = 0.2
PARATUBORWIDTHCOEFF = 0.4


class _BracketSide(Layout):
    def __init__(self, width, height):
        super().__init__()
        self.width = width
        self.height = height


class ParenthesisLayout(Layout):
    def __init__(
        self,
        parent,
        inner,
        openFname="normpara_left.png",
        closeFname="normpara_right.png",
    ):
        super().__init__()

        self.fontSize = parent.fontSize
        self.color = parent.color

        self.inner = MathText(inner, self.fontSize, self.color)
        self.inner.setCenter(0, self.inner.bottomLineDiffrence * 0.25)

        paraheight = max(self.inner.height, int(self.fontSize * 0.5))

        self.left = Symbol(
            openFname, PARANORMALWIDTHCOEFF * self.fontSize, paraheight, self.color
        )
        self.left.setCenter(y=0)
        self.left.setRight(self.inner.getLeft() - WHITESPACESIZE * self.fontSize)

        self.right = Symbol(
            closeFname, PARANORMALWIDTHCOEFF * self.fontSize, paraheight, self.color
        )
        self.right.setCenter(y=0)
        self.right.setLeft(self.inner.getRight() + WHITESPACESIZE * self.fontSize)

        x, y, x1, y1 = boundingBox(self.inner, self.left, self.right)

        self._bbox_offset = (x, y)
        self.width = x1 - x
        self.height = y1 - y
        self._children = (self.left, self.inner, self.right)
        self.setBottomLineDiffrence(self.inner.bottomLineDiffrence)

    def collect_scene(self, offset: tuple[float, float]) -> list:
        ox, oy = offset
        bx, by = self._bbox_offset
        return collect_children((ox + bx, oy + by), *self._children)

    def __repr__(self):
        return "\\left({}\\right)".format(self.inner)


class SquareParenthesisLayout(Layout):
    def __init__(self, parent, inner):
        super().__init__()

        self.fontSize = parent.fontSize
        self.color = parent.color

        self.inner = MathText(inner, self.fontSize, self.color)
        self.inner.setCenter(0, 0)

        bracket_width = int(PARANORMALWIDTHCOEFF * self.fontSize)
        bracket_height = int(self.inner.height) + 8
        self._thickness = int(self.fontSize * FONTSIZELINEWIDTH)
        self._bracket_width = bracket_width
        self._bracket_height = bracket_height

        self.left = _BracketSide(bracket_width, bracket_height)
        self.left.setCenter(y=0)
        self.left.setRight(self.inner.getLeft() - WHITESPACESIZE * self.fontSize)

        self.right = _BracketSide(bracket_width, bracket_height)
        self.right.setCenter(y=0)
        self.right.setLeft(self.inner.getRight() + WHITESPACESIZE * self.fontSize)

        x, y, x1, y1 = boundingBox(self.inner, self.left, self.right)

        self._bbox_offset = (x, y)
        self.width = x1 - x
        self.height = y1 - y
        self.setBottomLineDiffrence(self.inner.bottomLineDiffrence)

    def _bracket_rects(self, left_x: float, bottom: float) -> list:
        t = self._thickness
        w = self._bracket_width
        h = self._bracket_height
        color = self.color
        return [
            Rect(left_x, bottom, t, h, color),
            Rect(left_x, bottom + h - t, w, t, color),
            Rect(left_x, bottom, w, t, color),
        ]

    def collect_scene(self, offset: tuple[float, float]) -> list:
        ox, oy = offset
        bx, by = self._bbox_offset
        scene_offset = (ox + bx, oy + by)
        nodes = self.inner.collect_scene(scene_offset)
        nodes.extend(
            self._bracket_rects(
                ox + bx + self.left.getLeft(),
                oy + by + self.left.getBottom(),
            )
        )
        nodes.extend(
            self._bracket_rects(
                ox + bx + self.right.getLeft(),
                oy + by + self.right.getBottom(),
            )
        )
        return nodes

    def __repr__(self):
        return "\\squarepara({})".format(self.inner)


MACROS["\\para"] = ParenthesisLayout
MACROS["\\squarepara"] = SquareParenthesisLayout
