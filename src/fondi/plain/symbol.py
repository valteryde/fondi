
from ..layout import Layout
from ..scene import RasterSymbol


class Symbol(Layout):

    def __init__(
        self,
        fname: str,
        width: int = 50,
        height: int = 50,
        color: tuple[int, int, int, int] = (0, 0, 0, 255),
    ):
        super().__init__()
        self.fname = fname
        self.width = width
        self.height = height
        self.color = color

    def collect_scene(self, offset: tuple[float, float]) -> list:
        ox, oy = offset
        return [
            RasterSymbol(
                self.fname,
                self.getLeft() - ox,
                self.getBottom() - oy,
                self.width,
                self.height,
                self.color,
            )
        ]
