
MACROS = {}
WHITESPACESIZE = 0.15


class Layout:
    """
    positioner er venstre nederst. Som et normal koordinatsystem
    """

    def __init__(self):
        self.x = 0
        self.y = 0
        self.bottomLineDiffrence = 0
        self.hasBottomLineDiffrence = False
        self._extra_nodes: list = []

    def getBottom(self):
        return self.y

    def getTop(self):
        return self.y + self.height

    def getLeft(self):
        return self.x

    def getRight(self):
        return self.x + self.width

    def getBoundingBox(self):
        return self.getLeft(), self.getBottom(), self.getRight(), self.getTop()

    def setRight(self, x):
        self.x = x - self.width

    def setLeft(self, x):
        self.x = x

    def setTop(self, y):
        self.y = y - self.height

    def setBottom(self, y):
        self.y = y

    def setBottomLineDiffrence(self, dy):
        self.hasBottomLineDiffrence = True
        self.bottomLineDiffrence = dy

    def setCenter(self, x=None, y=None):
        if x is not None:
            self.x = x - self.width / 2
        if y is not None:
            self.y = y - self.height / 2

    def collect_scene(self, offset: tuple[float, float]) -> list:
        return list(self._extra_nodes)

    def prepPasteLeft(self, lastobj=0):
        self.x = lastobj.getRight() + WHITESPACESIZE * self.fontSize
        if self.hasBottomLineDiffrence:
            self.y = self.bottomLineDiffrence

    def handleSuperSub(self, parent, body, lower="", upper=""):
        return False

    def copy(self, target):
        state = dict(target.__dict__)
        state["_extra_nodes"] = list(getattr(target, "_extra_nodes", []))
        self.__dict__.update(state)
