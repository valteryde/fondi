
from .layout import *
from ..mathtext import MathText
from ..plain.plain import PlainText


class StandardText(PlainText):

    def __init__(self, parent, text):
        super().__init__(text, parent.fontSize, parent.color, False, italic=False)


class Ln(MathText):
    def __init__(self, parent, inner=""):
        super().__init__("\\text{ln}" + inner, parent.fontSize, color=parent.color)


class Log(MathText):
    def __init__(self, parent, inner=""):
        super().__init__("\\text{log}" + inner, parent.fontSize, color=parent.color)


class Sin(MathText):
    def __init__(self, parent, inner=""):
        super().__init__("\\text{sin}" + inner, parent.fontSize, color=parent.color)


class Cos(MathText):
    def __init__(self, parent, inner=""):
        super().__init__("\\text{cos}" + inner, parent.fontSize, color=parent.color)


class Tan(MathText):
    def __init__(self, parent, inner=""):
        super().__init__("\\text{tan}" + inner, parent.fontSize, color=parent.color)


class Cdot(MathText):
    def __init__(self, parent):
        super().__init__("*", parent.fontSize, color=parent.color)
        self.setBottomLineDiffrence(parent.fontSize / 4)


MACROS["\\text"] = StandardText
MACROS["\\ln"] = Ln
MACROS["\\log"] = Log
MACROS["\\sin"] = Sin
MACROS["\\cos"] = Cos
MACROS["\\tan"] = Tan
MACROS["\\cdot"] = Cdot
