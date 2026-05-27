
from .helper import boundingBox, unwrap_macro_arg
from .layout import Layout, MACROS, WHITESPACESIZE
from ..plain import Symbol
from ..mathtext import MathText
from .scene_builder import collect_children, composite_origin
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

        self.inner = MathText(unwrap_macro_arg(inner), self.fontSize, self.color)
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

    def collect_scene(
        self,
        corner: tuple[float, float] | tuple[float, float, float],
        root: tuple[float, float] | None = None,
        **kwargs,
    ) -> list:
        bx, by = self._bbox_offset
        return collect_children(
            self,
            (bx, by),
            *self._children,
            root=root,
            scene_corner=corner,
        )

    def __repr__(self):
        return "\\left({}\\right)".format(self.inner)


class SquareParenthesisLayout(Layout):
    def __init__(self, parent, inner):
        super().__init__()

        self.fontSize = parent.fontSize
        self.color = parent.color

        self.inner = MathText(unwrap_macro_arg(inner), self.fontSize, self.color)
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

    def _bracket_rects(
        self, side_x: float, bottom: float, *, right: bool = False
    ) -> list:
        t = self._thickness
        w = self._bracket_width
        h = self._bracket_height
        color = self.color
        if right:
            return [
                Rect(side_x + w - t, bottom, t, h, color),
                Rect(side_x, bottom + h - t, w, t, color),
                Rect(side_x, bottom, w, t, color),
            ]
        return [
            Rect(side_x, bottom, t, h, color),
            Rect(side_x, bottom + h - t, w, t, color),
            Rect(side_x, bottom, w, t, color),
        ]

    def collect_scene(
        self,
        corner: tuple[float, float] | tuple[float, float, float],
        root: tuple[float, float] | None = None,
        **kwargs,
    ) -> list:
        bx, by = self._bbox_offset
        origin_x, origin_y = corner[0], corner[1]
        nodes = collect_children(
            self,
            (bx, by),
            self.left,
            self.inner,
            self.right,
            root=root,
            scene_corner=corner,
        )
        nodes.extend(
            self._bracket_rects(
                origin_x + self.left.getLeft() - bx,
                origin_y + self.left.getBottom() - by,
            )
        )
        nodes.extend(
            self._bracket_rects(
                origin_x + self.right.getLeft() - bx,
                origin_y + self.right.getBottom() - by,
                right=True,
            )
        )
        return nodes

    def __repr__(self):
        return "\\squarepara({})".format(self.inner)


MACROS["\\para"] = ParenthesisLayout
MACROS["\\squarepara"] = SquareParenthesisLayout
