
from PIL import ImageDraw, Image, ImageFont
from ..layout import Layout
from .helper import replaceColorRandom, BASEPATH
import os
import numpy as np

class Symbol(Layout):

    def __init__(self, fname:str, width:int=50, height:int=50, color:int=(0,0,0,255)):
        super().__init__()

        self.fname = fname
        self.path = os.path.join(BASEPATH, fname)
        self.image = Image.open(self.path)

        self.color = color
        data = np.array(self.image)
        data[(data == (0,0,0,255)).all(axis = -1)] = self.color
        self.image = Image.fromarray(data)

        #self.image.thumbnail((width, height))
        self.image = self.image.resize((int(width), int(height)))
        self.width = width
        self.height = height
        #self.image.save(os.path.join('debug','symbol.png'))
