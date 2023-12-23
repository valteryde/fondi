
from PIL import Image

MACROS = {}
IMGMODE = "RGBA"
WHITESPACESIZE = 0.15

class Layout:
    """
    
    positioner er venstre nederst. Som et normal koordinatsystem

    """

    def __init__(self):
        self.x = 0
        self.y = 0
        self.centerline = 0
        self.hasCenterLine = False

    # get
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

    # def getCenter(self):
    #     return self.x, self.y

    # set (Used by special layout)
    def setRight(self, x):
        self.x = x - self.width

    def setLeft(self, x):
        self.x = x
    
    def setTop(self, y):
        self.y = y - self.height

    def setBottom(self, y):
        self.y = y

    def setCenterLine(self, dy):
        self.hasCenterLine = True
        self.centerline = dy

    def setCenter(self, x=None, y=None):
        if x is not None: self.x = x - self.width/2
        if y is not None: self.y = y - self.height/2

    def paste(self, surface:Image.Image, offset:tuple=(0,0)):
        return surface.paste(self.image, (int(self.getLeft()-offset[0]), surface.height - int(self.getTop()-offset[1])))

    def prepPasteLeft(self, lastobj=0): # used be MathText
        self.x = lastobj.getRight() + WHITESPACESIZE * self.fontSize
        
        if self.hasCenterLine:
            self.y = self.centerline