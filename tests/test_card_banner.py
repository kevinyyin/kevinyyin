import copy
import json

import card_banner
from svgcheck import check
from theme import DARK, LIGHT

CFG = json.load(open("profile/config.json"))
ACT = {"repos": [{"name": "Witness", "language": "Python", "commits": 78}]}


def test_two_slices():
    out = card_banner.render(CFG, LIGHT, ACT)
    assert [(s, w) for s, _, w, _ in out] == [("banner-left", 318), ("banner-art", 330)]
    assert out[0][3] == "https://www.linkedin.com/in/kevinyinkyy" and out[1][3] is None
    left, art = out[0][1], out[1][1]
    assert check(left).get("viewBox") == "0 0 318 208" and check(art).get("viewBox") == "0 0 330 208"
    for t in ("KEVINYYIN", "Kevin Yin", "LinkedIn ↗"):
        assert f'data-t="{t}"' in left
    assert 'data-t="Building stuff. Cognitive science and"' in left and 'data-t="entrepreneurship at Penn."' in left
    assert left.count('class="fx') >= 3 and "offset-path" in left and "#3B4B9A" in left
    assert 'data-t="art by LennSan"' in art and "data:image/png;base64," in art and "pixelated" in art
    assert "steps(12" in art and "steps(10" in art  # 12x10 sprite sheet: columns inside rows
    assert len(art.encode()) <= 1_500_000


def test_dark():
    left = card_banner.render(CFG, DARK, ACT)[0][1]
    assert "#111110" in left and "#8C98E8" in left


def test_art_link():
    c = copy.deepcopy(CFG)
    c["art"]["url"] = "https://example.com/post"
    assert card_banner.render(c, LIGHT, ACT)[1][3] == "https://example.com/post"


def test_art_off():
    c = copy.deepcopy(CFG)
    c["art"] = None
    out = card_banner.render(c, LIGHT, ACT)
    assert len(out) == 1 and out[0][0] == "banner" and out[0][2] == 648
    banner = out[0][1]
    check(banner)
    assert 'data-t="NOW BUILDING"' in banner and 'data-t="Witness"' in banner and "base64" not in banner
    assert 'data-t="NOW BUILDING"' not in card_banner.render(c, LIGHT, None)[0][1]
