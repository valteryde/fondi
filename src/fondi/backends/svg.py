from __future__ import annotations

import base64
from pathlib import Path
from xml.etree.ElementTree import Element, SubElement, tostring

from ..fileloader import loadFile
from ..scene import (
    Ellipse,
    Line,
    Node,
    Polyline,
    RasterSymbol,
    Rect,
    Scene,
    TextRun,
)

FONT_FAMILY = "FondiNewCM"
FONT_REGULAR = "NewCM10-Regular.otf"
FONT_ITALIC = "NewCM10-Italic.otf"
FONT_FILES = (FONT_REGULAR, FONT_ITALIC)


def copy_font_files(target_dir: str | Path) -> list[Path]:
    """Copy bundled New CM OTF files into target_dir. Returns written paths."""
    target = Path(target_dir)
    target.mkdir(parents=True, exist_ok=True)
    written = []
    for name in FONT_FILES:
        dest = target / name
        dest.write_bytes(loadFile(name).read())
        written.append(dest)
    return written


def _font_face_css(*, embed_fonts: bool, font_url_prefix: str) -> str:
    if embed_fonts:
        regular = base64.b64encode(loadFile(FONT_REGULAR).read()).decode("ascii")
        italic = base64.b64encode(loadFile(FONT_ITALIC).read()).decode("ascii")
        return (
            f"@font-face {{ font-family: '{FONT_FAMILY}'; font-style: normal; "
            f"src: url(data:font/otf;base64,{regular}) format('opentype'); }}\n"
            f"@font-face {{ font-family: '{FONT_FAMILY}'; font-style: italic; "
            f"src: url(data:font/otf;base64,{italic}) format('opentype'); }}"
        )

    prefix = font_url_prefix.replace("\\", "/")
    if prefix and not prefix.endswith("/"):
        prefix += "/"
    regular_url = f"{prefix}{FONT_REGULAR}"
    italic_url = f"{prefix}{FONT_ITALIC}"
    return (
        f"@font-face {{ font-family: '{FONT_FAMILY}'; font-style: normal; "
        f"src: url('{regular_url}') format('opentype'); }}\n"
        f"@font-face {{ font-family: '{FONT_FAMILY}'; font-style: italic; "
        f"src: url('{italic_url}') format('opentype'); }}"
    )


def _stroke_attrs(stroke: tuple[int, int, int, int], width: float) -> dict[str, str]:
    r, g, b, a = stroke
    attrs = {
        "stroke": f"rgb({r},{g},{b})",
        "stroke-width": str(width),
        "fill": "none",
    }
    if a < 255:
        attrs["stroke-opacity"] = str(round(a / 255, 4))
    return attrs


def _fill_attrs(fill: tuple[int, int, int, int]) -> dict[str, str]:
    r, g, b, a = fill
    attrs = {"fill": f"rgb({r},{g},{b})"}
    if a < 255:
        attrs["fill-opacity"] = str(round(a / 255, 4))
    return attrs


def _y_up_bitmap_transform(
    x: float, y_top: float, width: float, *, flip_x: bool = False
) -> str:
    """Undo the root Y flip so bitmap-backed nodes match Pillow placement."""
    rx, ry = round(x, 3), round(y_top, 3)
    parts = [f"translate({rx},{ry}) scale(1,-1) translate({-rx},{-ry})"]
    if flip_x:
        cx = round(x + width / 2, 3)
        parts.append(f"translate({cx},0) scale(-1,1) translate({-cx},0)")
    return " ".join(parts)


def _append_node(group: Element, node: Node) -> None:
    if isinstance(node, TextRun):
        el = SubElement(group, "text")
        el.set("x", str(round(node.x, 3)))
        el.set("y", str(round(node.y, 3)))
        el.set("font-family", FONT_FAMILY)
        el.set("font-size", str(node.font_size))
        el.set("font-style", "italic" if node.style == "italic" else "normal")
        el.set("text-anchor", "middle")
        el.set("dominant-baseline", "alphabetic")
        for key, value in _fill_attrs(node.fill).items():
            el.set(key, value)
        el.text = node.text
    elif isinstance(node, Line):
        el = SubElement(group, "line")
        el.set("x1", str(round(node.x1, 3)))
        el.set("y1", str(round(node.y1, 3)))
        el.set("x2", str(round(node.x2, 3)))
        el.set("y2", str(round(node.y2, 3)))
        for key, value in _stroke_attrs(node.stroke, node.stroke_width).items():
            el.set(key, value)
    elif isinstance(node, Polyline):
        points = " ".join(
            f"{round(x, 3)},{round(y, 3)}" for x, y in node.points
        )
        el = SubElement(group, "polyline")
        el.set("points", points)
        for key, value in _stroke_attrs(node.stroke, node.stroke_width).items():
            el.set(key, value)
    elif isinstance(node, Ellipse):
        el = SubElement(group, "ellipse")
        el.set("cx", str(round(node.x + node.width / 2, 3)))
        el.set("cy", str(round(node.y + node.height / 2, 3)))
        el.set("rx", str(round(node.width / 2, 3)))
        el.set("ry", str(round(node.height / 2, 3)))
        for key, value in _fill_attrs(node.fill).items():
            el.set(key, value)
    elif isinstance(node, Rect):
        x = node.x
        y_top = node.y + node.height
        el = SubElement(group, "rect")
        el.set("x", str(round(x, 3)))
        el.set("y", str(round(y_top, 3)))
        el.set("width", str(round(node.width, 3)))
        el.set("height", str(round(node.height, 3)))
        el.set("transform", _y_up_bitmap_transform(x, y_top, node.width))
        for key, value in _fill_attrs(node.fill).items():
            el.set(key, value)
    elif isinstance(node, RasterSymbol):
        href = (
            "data:image/png;base64,"
            + base64.b64encode(loadFile(node.asset_id).read()).decode("ascii")
        )
        x = node.x
        y_top = node.y + node.height
        el = SubElement(group, "image")
        el.set("x", str(round(x, 3)))
        el.set("y", str(round(y_top, 3)))
        el.set("width", str(round(node.width, 3)))
        el.set("height", str(round(node.height, 3)))
        el.set("href", href)
        el.set(
            "transform",
            _y_up_bitmap_transform(x, y_top, node.width, flip_x=node.flip_x),
        )


def render_svg(
    scene: Scene,
    *,
    embed_fonts: bool = True,
    font_url_prefix: str = "",
) -> str:
    """
    Render scene to an SVG document string.

    embed_fonts: If True (default), embed both OTF files as base64 in the SVG.
        If False, reference external files via @font-face URLs. Use
        font_url_prefix for the directory relative to the SVG file, e.g. "fonts/"
        or "" when the OTF files sit beside the SVG. Call copy_font_files() or
        save_svg() to write the font files.
    """
    width = max(scene.width, 0)
    height = max(scene.height, 0)
    root = Element(
        "svg",
        xmlns="http://www.w3.org/2000/svg",
        width=str(round(width, 3)),
        height=str(round(height, 3)),
        viewBox=f"0 0 {round(width, 3)} {round(height, 3)}",
    )
    defs = SubElement(root, "defs")
    style = SubElement(defs, "style")
    style.text = _font_face_css(embed_fonts=embed_fonts, font_url_prefix=font_url_prefix)
    group = SubElement(
        root,
        "g",
        transform=f"translate(0,{round(height, 3)}) scale(1,-1)",
    )
    for node in scene.children:
        _append_node(group, node)
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + tostring(root, encoding="unicode")


def save_svg_bundle(
    scene: Scene,
    svg_path: str | Path,
    *,
    embed_fonts: bool = False,
    font_subdir: str | None = "fonts",
    copy_fonts: bool = True,
) -> Path:
    """
    Write SVG to svg_path.

    embed_fonts: embed OTF data in the SVG (self-contained).
    font_subdir: when using external fonts, URL prefix (e.g. "fonts/") or None
        for OTF files expected beside the SVG.
    copy_fonts: when embed_fonts is False, copy bundled OTF files into place.
        Set False if fonts already exist at the referenced path.
    """
    svg_path = Path(svg_path)
    if embed_fonts:
        font_url_prefix = ""
        font_dir = None
    elif font_subdir:
        font_dir = svg_path.parent / font_subdir
        font_url_prefix = f"{font_subdir}/"
    else:
        font_dir = svg_path.parent
        font_url_prefix = ""

    if font_dir is not None and copy_fonts:
        copy_font_files(font_dir)

    svg_path.write_text(
        render_svg(
            scene,
            embed_fonts=embed_fonts,
            font_url_prefix=font_url_prefix,
        ),
        encoding="utf-8",
    )
    return svg_path
