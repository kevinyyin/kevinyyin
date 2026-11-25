from datetime import date

import card_contributions as cc
from svgcheck import check
from theme import LIGHT

T = date(2026, 11, 24)


def test_grid(contrib):
    out = cc.render(contrib, LIGHT, T)
    root = check(out)
    assert root.get("viewBox") == "0 0 648 262"
    cells = [e for e in root.iter() if e.get("class") == "d"]
    assert len(cells) == 25 * 7 + 3
    assert sum(1 for e in cells if e.get("fill") == "#3B4B9A") == 2  # Nov 13 (115) and Nov 14 (188)
    assert sum(1 for e in cells if e.get("fill-opacity") == "0.07") >= 70  # the empty weeks before Aug 9
    assert 'data-t="1,595 in the last six months"' in out
    for m in ("Jun", "Jul", "Aug", "Sep", "Oct", "Nov"):
        assert f'data-t="{m}"' in out


def test_empty(contrib):
    days = [{"date": "2026-11-24", "count": 0, "level": 0}]
    out = cc.render({**contrib, "days": days}, LIGHT, T)
    check(out)
    assert 'data-t="0 in the last six months"' in out
