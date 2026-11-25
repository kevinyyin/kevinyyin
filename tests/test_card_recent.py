import copy

import card_recent
from svgcheck import check
from theme import LIGHT

BASE = {"totals": {"repos": 5, "commits": 251}, "repos": [
    {"name": "Witness", "url": "u", "description": None, "language": "Python", "commits": 78, "merged": 0,
     "last_active": "2026-11-21",
     "highlights": [{"kind": "commit", "title": "Break-it map is fixed in place", "date": "2026-11-21"}]},
    {"name": "struum", "url": "u", "description": "Music player", "language": "JavaScript", "commits": 57, "merged": 1,
     "last_active": "2026-11-21",
     "highlights": [{"kind": "merged", "title": "Phone home screen", "date": "2026-11-19"}]}]}


def test_slices():
    out = card_recent.render(BASE, LIGHT)
    assert len(out) == 2
    for s in out:
        check(s)
    assert 'data-t="RECENTLY"' in out[0] and 'data-t="last 30 days · 251 commits · 5 repos"' in out[0]
    assert 'data-t="78 commits · active Nov 21"' in out[0]
    assert 'data-t="57 commits · 1 merged · active Nov 21"' in out[1] and 'data-t="Music player"' in out[1]
    assert 'data-t="RECENTLY"' not in out[1]


def test_max_three():
    a = copy.deepcopy(BASE)
    a["repos"] = a["repos"] * 3
    assert len(card_recent.render(a, LIGHT)) == 3


def test_none():
    assert card_recent.render({"totals": {"repos": 0, "commits": 0}, "repos": []}, LIGHT) == []


def test_hostile_text():
    a = copy.deepcopy(BASE)
    a["repos"][0]["name"] = "a-very-long-repository-name-" * 6
    a["repos"][0]["description"] = 'Tom & Jerry <b>"quoted"</b> 🚀 数据 ' * 20
    a["repos"][0]["highlights"][0]["title"] = "x" * 500
    for s in card_recent.render(a, LIGHT):
        root = check(s)
        for el in root.iter():
            t = el.get("data-t")
            if t:
                assert "🚀" not in t and "数" not in t and len(t) < 200


def test_singular():
    a = copy.deepcopy(BASE)
    a["repos"][0]["commits"] = 1
    assert 'data-t="1 commit · active Nov 21"' in card_recent.render(a, LIGHT)[0]
