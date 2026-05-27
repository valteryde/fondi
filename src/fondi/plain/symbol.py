
from ..fileloader import loadFile
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

    def collect_scene(
        self,
        corner: tuple[float, float] | tuple[float, float, float] | None = None,
        root: tuple[float, float] | None = None,
        **kwargs,
    ) -> list:
        ox, oy = offset[0], offset[1]
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
