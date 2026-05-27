import sys
import pathlib
import xml.etree.ElementTree as ET

BASEDIR = pathlib.Path(__file__).parent.resolve()
SVG_DIR = BASEDIR / "images" / "svg"
sys.path.insert(0, str(BASEDIR / ".." / "src"))

import fondi


def _write_svg(
    mathtext,
    filename,
    fontsize=50,
    color=(0, 0, 0, 255),
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
    mt = fondi.MathText("a+b", 50, (0, 0, 0, 255))
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


def test_svg_raster_symbols_use_y_up_placement():
    mt = fondi.MathText(
        r"\sin(\frac{1}{2})",
        20,
        (0, 0, 0, 255),
    )
    scene = mt.scene()
    symbols = [n for n in scene.children if hasattr(n, "asset_id")]
    assert symbols
    svg = mt.to_svg(embed_fonts=False)
    root = ET.fromstring(svg)
    images = [el for el in root.iter() if el.tag.endswith("image")]
    assert len(images) == len(symbols)
    for symbol, image in zip(symbols, images):
        assert float(image.get("y")) == round(symbol.y + symbol.height, 3)
        assert "scale(1,-1)" in image.get("transform", "")


def test_save_svg_skip_copy_fonts():
    import tempfile

    tmp = pathlib.Path(tempfile.mkdtemp())
    font_dir = tmp / "fonts"
    font_dir.mkdir()
    (font_dir / "NewCM10-Regular.otf").write_bytes(b"fake")
    (font_dir / "NewCM10-Italic.otf").write_bytes(b"fake")

    out = tmp / "formula.svg"
    mt = fondi.MathText("x", 12, (0, 0, 0, 255))
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
    test_svg_raster_symbols_use_y_up_placement()
    test_save_svg_skip_copy_fonts()
    write_gallery()
    print(f"test_svg: ok — SVG files written to {SVG_DIR}")
