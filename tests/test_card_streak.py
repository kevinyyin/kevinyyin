import copy
from datetime import datetime, timezone

import card_streak
import svg
import textpath as tp
from svgcheck import check
from theme import DARK, LIGHT

NOW = datetime(2026, 11, 25, 3, tzinfo=timezone.utc)


def test_values(contrib):
    out = card_streak.render(contrib, LIGHT, NOW)
    root = check(out)
    assert root.get("viewBox") == "0 0 648 266"
    for t in ("40", "day streak", "since Oct 15 · your longest yet", "16", "79", "1,596", "188", "Nov 14, 2026", "STREAK"):
        assert f'data-t="{t}"' in out, t
    assert "as of" not in out and "#3B4B9A" in out and "#F3F1EB" in out


def test_dark(contrib):
    out = card_streak.render(contrib, DARK, NOW)
    assert "#111110" in out and "#8C98E8" in out and "#F3F1EB" not in out


def test_zero_streak(contrib):
    d = copy.deepcopy(contrib)
    d["current_streak"] = {"length": 0, "start": None, "end": None}
    out = card_streak.render(d, LIGHT, NOW)
    check(out)
    assert 'data-t="0"' in out and 'data-t="last active Nov 23"' in out


def test_stale(contrib):
    d = copy.deepcopy(contrib)
    d["generated_at"] = "2026-11-20T06:17:00Z"
    assert 'data-t="as of Nov 20"' in card_streak.render(d, LIGHT, NOW)


def test_big_numbers_fit(contrib):
    d = copy.deepcopy(contrib)
    d["current_streak"]["length"] = 1234
    d["total_contributions"] = 123456
    out = card_streak.render(d, LIGHT, NOW)
    check(out)
    assert 'data-t="1234"' in out and 'data-t="123,456"' in out
    assert svg.value_size("1234", "display-500", 64, 130) < 64
    assert tp.measure("1234", "display-500", svg.value_size("1234", "display-500", 64, 130)) <= 130 + 1e-6
    assert svg.value_size("40", "display-500", 64, 130) == 64
