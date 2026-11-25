import xml.etree.ElementTree as ET

import pytest

import textpath as tp

NAME = ("Kevin Yin", "display-600", 128, -5 / 128)


def test_measure_scales():
    assert tp.measure("40", "display-500", 64) == pytest.approx(2 * tp.measure("40", "display-500", 32))


def test_name_width():
    assert 480 < tp.measure(*NAME) < 560  # mockup: about 520 at 128 units


def test_fit():
    long = "fix: a failed read can't wipe playlists, and other sites can't use the local server " * 3
    out = tp.fit(long, "text-400", 13, 400)
    assert out.endswith("…") and tp.measure(out, "text-400", 13) <= 400
    assert tp.fit("short", "text-400", 13, 400) == "short"


def test_clean_drops_unsupported():
    assert tp.clean("ship 🚀 it  数据 now", "text-400") == "ship it now"


def test_text_is_valid_xml_with_specials():
    el = ET.fromstring(tp.text(0, 20, 'A & B <c> "d"', "text-400", 13, "#141311"))
    assert el.tag == "path" and el.get("data-t") == 'A & B <c> "d"' and el.get("d")


def test_anchor_end():
    w = tp.measure("78 commits", "text-400", 12)
    d_end = tp.text(600, 20, "78 commits", "text-400", 12, "#000", anchor="end")
    d_start = tp.text(600 - w, 20, "78 commits", "text-400", 12, "#000")
    assert ET.fromstring(d_end).get("d") == ET.fromstring(d_start).get("d")


def test_wrap():
    lines = tp.wrap("Building stuff. Cognitive science and entrepreneurship at Penn.", "text-400", 14, 270)
    assert len(lines) == 2 and all(tp.measure(l, "text-400", 14) <= 270 for l in lines)


def test_i_dots():
    dots = tp.i_dots(*NAME)
    assert len(dots) == 2 and dots[0][0] < dots[1][0]
    for cx, cy, r in dots:
        assert -90 < cy < -70 and 8.5 < r < 12  # mockup: cy about -81, r about 10
    assert abs(dots[0][1] - dots[1][1]) < 0.01


def test_dotless_differs():
    assert tp.text(0, 0, "Yin", "display-600", 128, "#000", dotless=True) != tp.text(0, 0, "Yin", "display-600", 128, "#000")
