
import math


def unwrap_macro_arg(text: str) -> str:
    text = text.strip()
    if len(text) >= 2 and text[0] == "{" and text[-1] == "}":
        return text[1:-1]
    return text


def boundingBox(*objs):

    bounding = [math.inf, math.inf, -math.inf, -math.inf]
    for obj in objs:
        x, y, x1, y1 = obj.getBoundingBox()
        bounding[0] = min(bounding[0], x)
        bounding[1] = min(bounding[1], y)
        bounding[2] = max(bounding[2], x1)
        bounding[3] = max(bounding[3], y1)

    return bounding
