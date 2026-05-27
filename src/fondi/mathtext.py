
from .parser.tokens import *
from .layout.helper import boundingBox
from .layout import Layout, IMGMODE
from .plain import PlainText
from .parser import *
from .layout import *
from .scene import Scene
from pathlib import Path

from PIL import Image

from .backends import render_pillow, render_svg, save_svg_bundle


class MathText(Layout):

    def __init__(self, text, fontSize, color):
        super().__init__()

        self.text = text
        self.fontSize = fontSize
        self.color = color
        self.line: list = []
        self._scene: Scene | None = None

        self.__parse__(text)
        self._update_dimensions()

    def _update_dimensions(self) -> None:
        if not self.line:
            self.width = 0
            self.height = 0
            return
        self._position_line()
        x, y, x1, y1 = boundingBox(*self.line)
        self.width = x1 - x
        self.height = y1 - y

    def __parse__(self, text):
        text = text.replace("*", "·")
        tokens = parse(text)

        self.line = []
        for clss, tok in tokens:
            if tok == " " or tok == "":
                continue

            if clss == PLAINTEXT:
                self.line.append(
                    PlainText(
                        tok.replace("{", "").replace("}", ""),
                        self.fontSize,
                        self.color,
                    )
                )
            elif clss == ARGUMENT:
                self.line.append(MathText(tok, self.fontSize, self.color))
            elif clss == FULLCOMMAND:
                self.line.append(MACROS[tok["name"]](self, *tok["args"]))
            elif clss == OPERATION:
                self.line.append(
                    PlainText(
                        tok.replace("{", "").replace("}", ""),
                        self.fontSize,
                        self.color,
                        center=True,
                    )
                )

    def __repr__(self):
        return "".join(repr(i) for i in self.line)

    def _position_line(self):
        maxCenterLine = 0
        for i, obj in enumerate(self.line):
            obj.prepPasteLeft(self.line[i - 1])
            maxCenterLine = min(maxCenterLine, obj.bottomLineDiffrence)
        self.setBottomLineDiffrence(maxCenterLine)

    def _line_bbox_offset(self) -> tuple[float, float]:
        if not self.line:
            return 0.0, 0.0
        lx, ly, _, _ = boundingBox(*self.line)
        return lx, ly

    def collect_scene(
        self,
        corner: tuple[float, float] | tuple[float, float, float] | None = None,
        *,
        relayout: bool = True,
        root: tuple[float, float] | None = None,
    ) -> list:
        from .layout.scene_builder import collect_children

        if relayout:
            self._position_line()
        lx, ly = self._line_bbox_offset()
        return collect_children(
            self,
            (lx, ly),
            *self.line,
            root=root,
            scene_corner=corner,
        )

    def __build_scene__(self) -> Scene:
        if len(self.text) == 0:
            self.width = 0
            self.height = 0
            return Scene(0, 0, [])

        self._position_line()
        x, y, x1, y1 = boundingBox(*self.line)
        self.width = x1 - x
        self.height = y1 - y
        from .layout.scene_builder import collect_children

        children = collect_children(self, (x, y), *self.line, root=(x, y))
        return Scene(self.width, self.height, children)

    def scene(self) -> Scene:
        if self._scene is None:
            self._scene = self.__build_scene__()
        return self._scene

    def to_pil(self):
        scene = self.scene()
        if scene.width == 0 and scene.height == 0:
            return Image.new(IMGMODE, (0, 0))
        return render_pillow(scene)

    @property
    def image(self):
        return self.to_pil()

    def to_svg(self, *, embed_fonts: bool = True, font_url_prefix: str = "") -> str:
        return render_svg(
            self.scene(),
            embed_fonts=embed_fonts,
            font_url_prefix=font_url_prefix,
        )

    def save_svg(
        self,
        path: str | Path,
        *,
        embed_fonts: bool = False,
        font_subdir: str | None = "fonts",
        copy_fonts: bool = True,
    ) -> Path:
        return save_svg_bundle(
            self.scene(),
            path,
            embed_fonts=embed_fonts,
            font_subdir=font_subdir,
            copy_fonts=copy_fonts,
        )
