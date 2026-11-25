import copy
import json

import card_banner
from svgcheck import check
from theme import DARK, LIGHT

CFG = json.load(open("profile/config.json"))
ACT = {"repos": [{"name": "Witness", "language": "Python", "commits": 78}]}


def test_one_image_with_art():
    out = card_banner.render(CFG, LIGHT, ACT)
    assert check(out).get("viewBox") == "0 0 648 208"
    for t in ("KEVINYYIN", "Kevin Yin", "LinkedIn ↗"):
        assert f'data-t="{t}"' in out
    assert 'data-t="Building stuff. Cognitive science and"' in out and 'data-t="entrepreneurship at Penn."' in out
    assert out.count('class="fx') >= 3 and "offset-path" in out and "#3B4B9A" in out
    assert 'data-t="art by LennSan"' in out and "data:image/png;base64," in out and "pixelated" in out
    assert "steps(12" in out and "steps(10" in out  # 12x10 sprite sheet: columns inside rows
    assert len(out.encode()) <= 1_500_000


def test_dark():
    out = card_banner.render(CFG, DARK, ACT)
    assert "#111110" in out and "#8C98E8" in out


def test_art_off():
    c = copy.deepcopy(CFG)
    c["art"] = None
    banner = card_banner.render(c, LIGHT, ACT)
    assert check(banner).get("viewBox") == "0 0 648 208"
    assert 'data-t="NOW BUILDING"' in banner and 'data-t="Witness"' in banner and "base64" not in banner
    assert 'data-t="NOW BUILDING"' not in card_banner.render(c, LIGHT, None)
