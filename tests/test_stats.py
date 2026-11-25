import copy
from datetime import date, datetime, timezone

import pytest

import stats

T = date(2026, 11, 24)


def test_weekly_streak(contrib):
    assert stats.weekly_streak(contrib["days"], T) == 16


def test_grid_shape(contrib):
    g = stats.grid(contrib["days"], T)
    assert len(g) == 26 and all(len(c) == 7 for c in g)
    assert g[0][0]["date"] == "2026-05-31"
    assert [c and c["date"] for c in g[-1]] == ["2026-11-22", "2026-11-23", "2026-11-24", None, None, None, None]


def test_window_total(contrib):
    assert stats.window_total(stats.grid(contrib["days"], T)) == 1595


def test_month_labels(contrib):
    assert stats.month_labels(stats.grid(contrib["days"], T)) == [
        (0, "Jun"), (4, "Jul"), (8, "Aug"), (13, "Sep"), (17, "Oct"), (22, "Nov")]


def test_shade():
    assert stats.shade(0) == ("ink", 0.07)
    assert stats.shade(188) == ("accent", 1.0) and stats.shade(100) == ("accent", 1.0)
    assert stats.shade(75) == ("ink", 1.0)
    assert stats.shade(20)[1] == pytest.approx(0.6228, abs=1e-3)


def test_caption(contrib):
    assert stats.streak_caption(contrib) == "since Oct 15 · your longest yet"
    d = copy.deepcopy(contrib)
    d["current_streak"] = {"length": 3, "start": "2026-11-21", "end": "2026-11-23"}
    assert stats.streak_caption(d) == "since Nov 21 · longest: 40 days"


def test_zero_streak(contrib):
    d = copy.deepcopy(contrib)
    d["current_streak"] = {"length": 0, "start": None, "end": None}
    assert stats.streak_caption(d) == "last active Nov 23"


def test_empty_window():
    days = [{"date": "2026-11-24", "count": 0, "level": 0}]
    g = stats.grid(days, T)
    assert len(g) == 26 and stats.window_total(g) == 0 and stats.weekly_streak(days, T) == 0
    assert stats.last_active(days) is None


def test_as_of():
    now = datetime(2026, 11, 25, 12, tzinfo=timezone.utc)
    assert stats.as_of("2026-11-24T17:38:12Z", now) is None
    assert stats.as_of("2026-11-20T06:17:00Z", now) == "as of Nov 20"


def test_fmt_date():
    assert stats.fmt_date("2026-11-14", year=True) == "Nov 14, 2026"
