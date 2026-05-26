
from .layout import Layout, MACROS


class Space(Layout):
    def __init__(self, parent, space):
        super().__init__()
        self.fontSize = parent.fontSize
        self.width = int(space)
        self.height = 1


class Quad(Space):
    def __init__(self, parent):
        super().__init__(parent, parent.fontSize)


class Quad3(Space):
    def __init__(self, parent):
        super().__init__(parent, 3 / 18 * parent.fontSize)


class Quad4(Space):
    def __init__(self, parent):
        super().__init__(parent, 4 / 18 * parent.fontSize)


class Quad5(Space):
    def __init__(self, parent):
        super().__init__(parent, 5 / 18 * parent.fontSize)


class QQuad(Space):
    def __init__(self, parent):
        super().__init__(parent, 2 * parent.fontSize)


class Quad0(Space):
    def __init__(self, parent):
        super().__init__(parent, 0)


MACROS["\\quad"] = Quad
MACROS["\\smallSpace"] = Quad0
MACROS["\\,"] = Quad3
MACROS["\\:"] = Quad4
MACROS["\\;"] = Quad5
MACROS["\\qquad"] = QQuad
