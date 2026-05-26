
from .parser.tokens import *
from .layout.helper import boundingBox
from .layout import Layout
from .plain import PlainText
from .parser import *
from .layout import *
from .scene import Scene, translate_node
from pathlib import Path

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
        self.__build_scene__()

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

    def __build_scene__(self):
        if len(self.text) == 0:
            self.width = 0
            self.height = 0
            self._scene = Scene(0, 0, [])
            return

        maxCenterLine = 0
        for i, obj in enumerate(self.line):
            obj.prepPasteLeft(self.line[i - 1])
            maxCenterLine = min(maxCenterLine, obj.bottomLineDiffrence)

        self.setBottomLineDiffrence(maxCenterLine)

        x, y, x1, y1 = boundingBox(*self.line)
        self.width = x1 - x
        self.height = y1 - y

        children = []
        for obj in self.line:
            children.extend(obj.collect_scene((x, y)))

        self._scene = Scene(self.width, self.height, children)

    def collect_scene(self, offset: tuple[float, float]) -> list:
        if self._scene is None:
            self.__build_scene__()
        ox, oy = offset
        dx = self.getLeft() - ox
        dy = self.getBottom() - oy
        return [translate_node(n, dx, dy) for n in self._scene.children]

    def scene(self) -> Scene:
        if self._scene is None:
            self.__build_scene__()
        return self._scene

    def to_pil(self):
        from PIL import Image

        if self.width == 0 and self.height == 0:
            return Image.new("RGBA", (0, 0))
        return render_pillow(self.scene())

    def to_svg(self, *, embed_fonts: bool = True, font_url_prefix: str = "") -> str:
        """
        Return SVG as a string.

        embed_fonts: embed OTF data in the file (default), or reference external files.
        font_url_prefix: when embed_fonts is False, path prefix to the OTF files
            relative to the SVG, e.g. "fonts/" or "" if they sit beside the SVG.
        """
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
        """
        Write SVG to path.

        embed_fonts: True for one self-contained file; False for external @font-face URLs.
        font_subdir: folder prefix for external fonts (e.g. "fonts/").
        copy_fonts: when embed_fonts is False, copy OTF files into font_subdir.
            Set False to only write the SVG (fonts must already be at that path).
        """
        return save_svg_bundle(
            self.scene(),
            path,
            embed_fonts=embed_fonts,
            font_subdir=font_subdir,
            copy_fonts=copy_fonts,
        )

    @property
    def image(self):
        return self.to_pil()
