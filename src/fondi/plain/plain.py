
from ..layout import Layout
from ..metrics import font_style_for, measure_text
from ..scene import TextRun


class PlainText(Layout):

    def __init__(self, text, fontSize, color, center=False, italic=True):
        super().__init__()

        self.text = text
        self.fontSize = fontSize
        self.color = color
        self.style = font_style_for(text, italic)

        if len(text) == 0:
            self.width = 0
            self.height = 0
            return

        metrics = measure_text(text, fontSize, self.style)
        self.width = metrics.width
        self.height = metrics.height
        self.setBottomLineDiffrence(metrics.bottom_line_delta)

    def collect_scene(self, offset: tuple[float, float]) -> list:
        if len(self.text) == 0:
            return []
        ox, oy = offset
        return [
            TextRun(
                self.text,
                self.getLeft() - ox + self.width / 2,
                self.getBottom() - oy + self.height / 2,
                self.fontSize,
                self.style,
                self.color,
            )
        ]

    def __repr__(self):
        return self.text
