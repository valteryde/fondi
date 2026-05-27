
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

    def collect_scene(
        self,
        corner: tuple[float, float] | tuple[float, float, float] | None = None,
        root: tuple[float, float] | None = None,
        **kwargs,
    ) -> list:
        if len(self.text) == 0:
            return []
        ox, oy = offset[0], offset[1]
        if len(offset) >= 3:
            baseline_y = offset[2]
        else:
            baseline_y = self.getBottom() - oy - self.bottomLineDiffrence
        return [
            TextRun(
                self.text,
                self.getLeft() - ox + self.width / 2,
                baseline_y,
                self.fontSize,
                self.style,
                self.color,
            )
        ]

    def __repr__(self):
        return self.text
