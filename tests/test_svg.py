import sys
import pathlib
import xml.etree.ElementTree as ET

BASEDIR = pathlib.Path(__file__).parent.resolve()
SVG_DIR = BASEDIR / "images" / "svg"
sys.path.insert(0, str(BASEDIR / ".." / "src"))

import fondi

COLOR = (255, 0, 0, 255)

def _write_svg(
    mathtext,
    filename,
    fontsize=50,
    color=COLOR,
    *,
    embed_fonts=True,
    font_subdir="fonts",
    copy_fonts=True,
):
    SVG_DIR.mkdir(parents=True, exist_ok=True)
    mt = fondi.MathText(mathtext, fontsize, color)
    path = SVG_DIR / filename
    if embed_fonts:
        path.write_text(mt.to_svg(embed_fonts=True), encoding="utf-8")
    else:
        mt.save_svg(
            path,
            embed_fonts=False,
            font_subdir=font_subdir,
            copy_fonts=copy_fonts,
        )
    return mt, path


def test_svg_valid_and_has_fonts():
    mt, path = _write_svg(r"\frac{1}{2}", "frac_half.svg")
    svg = path.read_text(encoding="utf-8")
    assert "@font-face" in svg
    assert "FondiNewCM" in svg
    assert "<text" in svg
    root = ET.fromstring(svg)
    assert root.tag.endswith("svg")


def test_svg_contains_formula_text():
    mt, path = _write_svg("x^{2}", "x_squared.svg")
    svg = path.read_text(encoding="utf-8")
    assert "x" in svg
    assert "2" in svg


def test_scene_api():
    mt = fondi.MathText("a+b", 50, COLOR)
    scene = mt.scene()
    assert scene.width > 0
    assert len(scene.children) >= 1
    _, path = _write_svg("a+b", "a_plus_b.svg")
    assert path.exists()


def test_external_fonts_small_svg():
    mt, path = _write_svg(
        "x",
        "external_x.svg",
        fontsize=12,
        embed_fonts=False,
        font_subdir="fonts",
    )
    embedded = mt.to_svg(embed_fonts=True)
    external = path.read_text(encoding="utf-8")
    assert len(external) < len(embedded) // 10
    assert "data:font/otf;base64" not in external
    assert "fonts/NewCM10-Regular.otf" in external


def test_save_svg_bundle_writes_fonts():
    mt, out = _write_svg(
        "x",
        "save_bundle.svg",
        fontsize=12,
        embed_fonts=False,
        font_subdir="fonts",
    )
    assert out.exists()
    assert (out.parent / "fonts" / "NewCM10-Regular.otf").exists()
    assert (out.parent / "fonts" / "NewCM10-Italic.otf").exists()
    text = out.read_text(encoding="utf-8")
    assert "fonts/NewCM10-Regular.otf" in text
    assert "data:font/otf;base64" not in text


def test_svg_raster_symbols_are_tinted():
    from fondi.raster_symbols import load_symbol_image

    image = load_symbol_image("integral.png", 50, 200, COLOR)
    bbox = image.getbbox()
    assert bbox is not None
    pixel = None
    for y in range(bbox[1], bbox[3]):
        for x in range(bbox[0], bbox[2]):
            p = image.getpixel((x, y))
            if p[3] > 200 and p[:3] == COLOR[:3]:
                pixel = p
                break
        if pixel is not None:
            break
    assert pixel is not None


def test_nested_mathtext_argument_after_text_is_visible():
    from fondi.scene import TextRun

    mt = fondi.MathText(
        r"\text{ [s] }{ v_q=12.5 }",
        50,
        COLOR,
    )
    scene = mt.scene()
    runs = [n for n in scene.children if isinstance(n, TextRun)]
    assert {n.text for n in runs} == {" [s] ", "v", "q", "=", "12.5"}
    assert all(n.x >= 0 for n in runs)
    xs = sorted(n.x for n in runs)
    assert xs == sorted(xs), "text runs should appear left-to-right"


def test_cases_scene_fits_rightmost_text():
    from fondi.metrics import measure_text
    from fondi.scene import TextRun

    mt = fondi.MathText(
        r"f(x^2)=\cases{2*x}{10>x}{[2^{x}]}{10<x}{\frac{1}{2}}{\text{else}}",
        50,
        COLOR,
    )
    scene = mt.scene()
    rightmost = max(
        n.x + measure_text(n.text, int(n.font_size), n.style).width / 2
        for n in scene.children
        if isinstance(n, TextRun)
    )
    assert scene.width > rightmost


def test_svg_raster_symbols_use_y_up_placement():
    mt = fondi.MathText(
        r"\int{\frac{1}{2}}{dx}",
        20,
        COLOR,
    )
    scene = mt.scene()
    symbols = [n for n in scene.children if hasattr(n, "asset_id")]
    assert symbols
    svg = mt.to_svg(embed_fonts=False)
    root = ET.fromstring(svg)
    images = [el for el in root.iter() if el.tag.endswith("image")]
    assert len(images) == len(symbols)


def test_square_brackets_wrap_content():
    mt = fondi.MathText(r"[2^{x}]", 50, COLOR)
    scene = mt.scene()
    from fondi.scene import Rect, TextRun

    rects = [n for n in scene.children if isinstance(n, Rect)]
    texts = [n for n in scene.children if isinstance(n, TextRun)]
    min_tx = min(t.x for t in texts)
    max_tx = max(t.x for t in texts)
    assert min(r.x for r in rects) < min_tx
    assert max(r.x + r.width for r in rects) > max_tx


def test_round_parens_use_vector_delimiters():
    from fondi.scene import Polyline

    mt = fondi.MathText(
        r"\sin(\frac{x^2 + (10+2)_{hej}}{\frac{2}{x}_{i,j}})",
        50,
        COLOR,
    )
    scene = mt.scene()
    delimiters = [n for n in scene.children if isinstance(n, Polyline)]
    assert len(delimiters) >= 2
    assert not any(
        getattr(n, "asset_id", "").startswith("normpara")
        for n in scene.children
        if hasattr(n, "asset_id")
    )
    _, path = _write_svg(
        r"\sin(\frac{1}{2})",
        "paren_vector.svg",
        fontsize=50,
    )
    svg = path.read_text(encoding="utf-8")
    assert "<polyline" in svg
    assert "normpara_left" not in svg


def test_square_brackets_in_cases_do_not_overlap_brace():
    from fondi.scene import Polyline, Rect

    mt = fondi.MathText(
        r"f(x^2)=\cases{2*x}{10>x}{[2^{x}]}{10<x}{\frac{1}{2}}{\text{else}}",
        50,
        COLOR,
    )
    scene = mt.scene()
    brace_polylines = [n for n in scene.children if isinstance(n, Polyline)]
    assert brace_polylines
    brace_right = max(max(x for x, _ in p.points) for p in brace_polylines)
    bracket_rects = [n for n in scene.children if isinstance(n, Rect)]
    assert bracket_rects
    bracket_left = min(r.x for r in bracket_rects)
    assert bracket_left > brace_right


def test_save_svg_skip_copy_fonts():
    import tempfile

    tmp = pathlib.Path(tempfile.mkdtemp())
    font_dir = tmp / "fonts"
    font_dir.mkdir()
    (font_dir / "NewCM10-Regular.otf").write_bytes(b"fake")
    (font_dir / "NewCM10-Italic.otf").write_bytes(b"fake")

    out = tmp / "formula.svg"
    mt = fondi.MathText("x", 12, COLOR)
    mt.save_svg(out, embed_fonts=False, font_subdir="fonts", copy_fonts=False)
    assert out.exists()
    assert (font_dir / "NewCM10-Regular.otf").read_bytes() == b"fake"
    assert "fonts/NewCM10-Regular.otf" in out.read_text(encoding="utf-8")


def write_gallery():
    examples = [
        (r"2*x_{5}^{2}+7^{2}_{1}", "polynomen.svg"),
        (
            r"f(x^2)=\cases{2*x}{10>x}{[2^{x}]}{10<x}{\frac{1}{2}}{\text{else}}",
            "cases.svg",
        ),
        (r"10+\frac{\frac{1}{2}}{x}", "nested_fraction.svg"),
        (
            r"0,4x^{3}+2*x^{2}+5*x_{n-1}+b_{a}+c_{0}+5^{2}_{x}",
            "supersub.svg",
        ),
        (r"R^2=0,9281", "rsquared.svg"),
        (r"\sqrt{10^{2+1}}", "sqrt.svg"),
        (
            r"\sin(\frac{x^2 + (10+2)_{hej}}{\frac{2}{x}_{i,j}})",
            "para.svg",
        ),
        (
            r"5x+\int{2x}{dx} + 7x \int{x^2}{dx}_{-2}^{2}",
            "integral.svg",
        ),
        (
            r"\dot{x} + \ddot{y} + \tilde{z} + \bar{a}",
            "dot_tilde_bar.svg",
        ),
        (
            r"a_{ijk} + b^{xyz} + c_{a+b}^{m+n} + a_{bc_{ak}}",
            "subscript_multiple_characters.svg",
        ),
    ]
    for mathtext, filename in examples:
        _write_svg(mathtext, filename)


if __name__ == "__main__":
    test_svg_valid_and_has_fonts()
    test_svg_contains_formula_text()
    test_scene_api()
    test_external_fonts_small_svg()
    test_save_svg_bundle_writes_fonts()
    test_svg_raster_symbols_are_tinted()
    test_cases_scene_fits_rightmost_text()
    test_nested_mathtext_argument_after_text_is_visible()
    test_svg_raster_symbols_use_y_up_placement()
    test_square_brackets_wrap_content()
    test_round_parens_use_vector_delimiters()
    test_square_brackets_in_cases_do_not_overlap_brace()
    test_save_svg_skip_copy_fonts()
    write_gallery()
    print(f"test_svg: ok — SVG files written to {SVG_DIR}")
