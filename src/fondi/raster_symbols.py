from __future__ import annotations

from io import BytesIO

import numpy as np
from PIL import Image

from .fileloader import loadFile
from .scene import Color


def load_symbol_image(
    asset_id: str, width: int, height: int, fill: Color
) -> Image.Image:
    image = Image.open(loadFile(asset_id)).convert("RGBA")
    data = np.array(image)
    data[(data == (0, 0, 0, 255)).all(axis=-1)] = fill
    return Image.fromarray(data).resize((int(width), int(height)))


def symbol_image_png_bytes(
    asset_id: str, width: int, height: int, fill: Color
) -> bytes:
    buffer = BytesIO()
    load_symbol_image(asset_id, width, height, fill).save(buffer, format="PNG")
    return buffer.getvalue()
