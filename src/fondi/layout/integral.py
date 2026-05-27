
from .helper import boundingBox, unwrap_macro_arg
from .layout import Layout, MACROS, WHITESPACESIZE
from ..plain import Symbol
from .supersub import SUBSUPSIZE
from ..mathtext import MathText
from .scene_builder import collect_children

INTEGRALSYMBOLSIZEFACTOR = 2
INTEGRALSYMBOLASPECTRATIO = 0.4
INTEGRALLOWEROFFSET = 0.45


class IntegralLayout(Layout):
    def __init__(
        self,
        parent,
        inner="",
        dx="",
        lower="",
        upper="",
        symbolFileName: str = "integral.png",
    ):
        super().__init__()

        self.inner = MathText(unwrap_macro_arg(inner), parent.fontSize, color=parent.color)
        self.inner_dx = MathText(unwrap_macro_arg(dx), parent.fontSize, color=parent.color)

        self.lower = MathText(unwrap_macro_arg(lower), int(parent.fontSize * SUBSUPSIZE), color=parent.color)
        self.upper = MathText(unwrap_macro_arg(upper), int(parent.fontSize * SUBSUPSIZE), color=parent.color)

        self.fontSize = parent.fontSize
        self.color = parent.color

        self.inner.setBottom(0)

        self.symbol = Symbol(
            symbolFileName,
            INTEGRALSYMBOLASPECTRATIO * INTEGRALSYMBOLSIZEFACTOR * self.fontSize,
            INTEGRALSYMBOLSIZEFACTOR * self.fontSize,
            self.color,
        )
        self.symbol.setLeft(0)
        self.symbol.setCenter(y=0)

        self.upper.setLeft(self.symbol.getRight() + WHITESPACESIZE * self.fontSize)
        self.upper.setCenter(y=self.symbol.getTop())

        self.lower.setLeft(
            self.symbol.getRight()
            - self.symbol.width * INTEGRALLOWEROFFSET
            + WHITESPACESIZE * self.fontSize
        )
        self.lower.setCenter(y=self.symbol.getBottom())

        leftInnerPosition = self.symbol.width + max(self.lower.width, self.upper.width)

        self.inner.setLeft(leftInnerPosition)
        self.inner.setCenter(y=0)

        self.inner_dx.setLeft(
            leftInnerPosition + self.inner.width + self.fontSize * 0.3
        )
        self.inner_dx.setCenter(y=0)

        bbox = boundingBox(
            self.inner, self.symbol, self.inner_dx, self.lower, self.upper
        )

        self._bbox_offset = (bbox[0], bbox[1])
        self.width = int(bbox[2] - bbox[0])
        self.height = int(bbox[3] - bbox[1])
        self._children = (
            self.symbol,
            self.lower,
            self.upper,
            self.inner,
            self.inner_dx,
        )

        diff = self.lower.getBottom() - self.inner.getBottom()
        self.setBottomLineDiffrence(diff + self.inner.bottomLineDiffrence)

    def collect_scene(
        self,
        corner: tuple[float, float] | tuple[float, float, float],
        root: tuple[float, float] | None = None,
        **kwargs,
    ) -> list:
        bx, by = self._bbox_offset
        return collect_children(
            self, (bx, by), *self._children, root=root, scene_corner=corner
        )

    def handleSuperSub(parent, body, lower, upper):
        return IntegralLayout(parent, *body, lower=lower, upper=upper)

    def __repr__(self):
        return "\\int({})".format(self.inner)


class ContourIntegralLayout(IntegralLayout):
    def __init__(self, parent, inner="", dx="", lower="", upper=""):
        super().__init__(
            parent, inner, dx, lower, upper, symbolFileName="contour-integral.png"
        )

    def handleSuperSub(parent, body, lower, upper):
        return IntegralLayout(
            parent,
            *body,
            lower=lower,
            upper=upper,
            symbolFileName="contour-integral.png",
        )


MACROS["\\int"] = IntegralLayout
MACROS["\\oint"] = ContourIntegralLayout
