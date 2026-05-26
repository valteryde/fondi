
import sys
import pathlib
import xml.etree.ElementTree as ET

BASEDIR = pathlib.Path(__file__).parent.resolve()
sys.path.insert(0, str(BASEDIR / ".." / "src"))

import fondi


def test_svg_valid_and_has_fonts():
    mt = fondi.MathText(r"\frac{1}{2}", 50, (255, 255, 255, 255))
    svg = mt.to_svg()
    assert "@font-face" in svg
    assert "FondiNewCM" in svg
    assert "<text" in svg
    root = ET.fromstring(svg)
    assert root.tag.endswith("svg")


def test_svg_contains_formula_text():
    mt = fondi.MathText("x^{2}", 50, (255, 255, 255, 255))
    svg = mt.to_svg()
    assert "x" in svg
    assert "2" in svg


def test_scene_api():
    mt = fondi.MathText("a+b", 50, (255, 255, 255, 255))
    scene = mt.scene()
    assert scene.width > 0
    assert len(scene.children) >= 1


def test_external_fonts_small_svg():
    mt = fondi.MathText("x", 12, (0, 0, 0, 255))
    embedded = mt.to_svg(embed_fonts=True)
    external = mt.to_svg(embed_fonts=False, font_url_prefix="fonts/")
    assert len(external) < len(embedded) // 10
    assert "data:font/otf;base64" not in external
    assert "fonts/NewCM10-Regular.otf" in external


def test_save_svg_bundle_writes_fonts(tmp_path=None):
    import tempfile

    tmp = tempfile.mkdtemp() if tmp_path is None else tmp_path
    out = pathlib.Path(tmp) / "formula.svg"
    mt = fondi.MathText("x", 12, (0, 0, 0, 255))
    mt.save_svg(out, embed_fonts=False, font_subdir="fonts")
    assert out.exists()
    assert (out.parent / "fonts" / "NewCM10-Regular.otf").exists()
    assert (out.parent / "fonts" / "NewCM10-Italic.otf").exists()
    text = out.read_text()
    assert "fonts/NewCM10-Regular.otf" in text
    assert "data:font/otf;base64" not in text


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
    assert "fonts/NewCM10-Regular.otf" in out.read_text()


if __name__ == "__main__":
    test_svg_valid_and_has_fonts()
    test_svg_contains_formula_text()
    test_scene_api()
    test_external_fonts_small_svg()
    test_save_svg_bundle_writes_fonts()
    test_save_svg_skip_copy_fonts()
    print("test_svg: ok")
