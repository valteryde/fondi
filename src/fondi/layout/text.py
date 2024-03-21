
from .layout import *
from ..mathtext import MathText
from ..plain.helper import replaceColorRandom
from ..plain.plain import PlainText
from .helper import boundingBox
from PIL import Image, ImageDraw

class StandardText(PlainText):

    def __init__(self, parent, text):
        super().__init__(text, parent.fontSize, parent.color, False, italic=False)


MACROS["\\text"] = StandardText


#     "\\frac": FracLayout,
#     "\\super": SuperLayout,
#     "\\sub": SubLayout,
#     "\\supersub": SuperSubLayout,
#     "\\subsuper": SubSuperLayout,
#     "\\para": ParenthesisLayout


