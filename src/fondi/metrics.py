from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from PIL import Image, ImageDraw, ImageFont

from .fileloader import loadFile

REGULAR = set(["+", "-", ">", "<", "=", "·", "{", "}", "(", ")", "[", "]"])

FontStyle = Literal["regular", "italic"]

_FONT_FILES = {
    "regular": "NewCM10-Regular.otf",
    "italic": "NewCM10-Italic.otf",
}


def is_num(text: str) -> bool:
    try:
        float(text)
        return True
    except ValueError:
        return False


def font_style_for(text: str, italic: bool = True) -> FontStyle:
    if is_num(text) or text in REGULAR or not italic:
        return "regular"
    return "italic"


def load_font(font_size: int, style: FontStyle) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(loadFile(_FONT_FILES[style]), font_size)


@dataclass
class TextMetrics:
    width: float
    height: float
    bottom_line_delta: float


def measure_text(
    text: str,
    font_size: int,
    style: FontStyle,
    *,
    pad_spaces: bool = True,
) -> TextMetrics:
    if len(text) == 0:
        return TextMetrics(0, 0, 0)

    font = load_font(font_size, style)
    win_size = (font_size * 3 * len(text), font_size * 3 * len(text))
    image = Image.new("RGBA", win_size, color=(0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.text(
        (win_size[0] // 2, win_size[1] // 2),
        text,
        (255, 255, 255, 255),
        font=font,
        anchor="ms",
    )
    bbox = list(image.getbbox())
    lower_offset = bbox[3] - win_size[1] // 2

    if pad_spaces:
        if text[0] == " ":
            bbox[0] -= font_size * 0.25
        if text[-1] == " ":
            bbox[2] += font_size * 0.25

    return TextMetrics(
        width=bbox[2] - bbox[0],
        height=bbox[3] - bbox[1],
        bottom_line_delta=-lower_offset,
    )
