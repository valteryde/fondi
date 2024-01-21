
from ..plain import Image as LayoutImage 
from .helper import boundingBox
from .layout import Layout, IMGMODE, MACROS, WHITESPACESIZE
from ..plain import Symbol
from ..mathtext import MathText
from PIL import Image, ImageDraw
import math

#         super().__init__()

#         self.fontSize = parent.fontSize
#         self.color = parent.color

#         self.top = MathText(top, int(self.fontSize*FRACSHRINKCOEFF), self.color)
#         self.bottom = MathText(bottom, int(self.fontSize*FRACSHRINKCOEFF), self.color)

#         linewidth = int(FRACFONTWIDTHCOEFF * self.fontSize)
#         self.padding = FRACPADDINGCOEFF * self.fontSize + linewidth/2
#         self.width = max(self.bottom.width, self.top.width)
#         self.height = self.bottom.height + self.top.height + self.padding * 2

#         # draw
#         self.image = Image.new(IMGMODE, (int(self.width), int(self.height)))

#         self.top.setBottom(self.padding)
#         self.top.setCenter(x=self.width/2)
        
#         self.bottom.setTop(-self.padding)
#         self.bottom.setCenter(x=self.width/2)

#         x, y, x1, y1 = boundingBox(self.bottom, self.top)
#         self.setCenterLine(y + self.fontSize/4)

#         # paste
#         self.top.paste(self.image, (x,y))
#         self.bottom.paste(self.image, (x,y))

#         # draw line
#         imd = ImageDraw.ImageDraw(self.image)
#         imd.line((0, self.height+y, self.width, self.height+y), self.color, width=linewidth)

#         self.image = replaceColorRandom(self.image)
#         #self.image.save('debug/test-frac.png')



class SqrtLayout(Layout):
    def __init__(self, parent, *args):
        super().__init__()

        if len(args) == 2:
            print(args)

        self.inner = MathText(args[0], parent.fontSize, color=parent.color)

        self.linewidth = 3
        self.fontSize = parent.fontSize
        self.padding = self.fontSize//5
        self.height = int(self.inner.height+self.padding)

        self.angle = math.radians(60)

        c = self.inner.height/math.sin(self.angle)
        line1 = (0,self.height/2), (math.cos(self.angle)*c/2, self.height)
        line2 = line1[1], (math.cos(self.angle)*c+line1[0][0], 0)

        self.width = int(self.inner.height + self.linewidth*2 + line2[1][0] + self.padding)

        line3 = line2[1], (self.width, line2[1][1])
        
        lines = *line1, *line2, *line3

        self.inner.setBottom(0)
        self.inner.setLeft(line3[0][0]+self.padding/2)

        print(line1)
        print(line2)


        self.image = Image.new('RGBA', (self.width, self.height))
        draw = ImageDraw.ImageDraw(self.image)

        self.inner.paste(self.image, (0,0))

        draw.line(lines, fill=(255,255,255,255), width=self.linewidth, joint="curve")


MACROS["\\sqrt"] = SqrtLayout
