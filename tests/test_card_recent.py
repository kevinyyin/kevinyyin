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


def test_one_card_with_every_repo():
    out = card_recent.render(BASE, LIGHT)
    check(out)
    assert out.count('data-t="RECENTLY"') == 1 and 'data-t="last 30 days · 251 commits · 5 repos"' in out
    assert 'data-t="78 commits · active Nov 21"' in out
    assert 'data-t="57 commits · 1 merged · active Nov 21"' in out and 'data-t="Music player"' in out
    assert out.index('data-t="Witness"') < out.index('data-t="struum"')


def test_max_three():
    a = copy.deepcopy(BASE)
    a["repos"] = [dict(a["repos"][0], name=f"repo{i}") for i in range(6)]
    out = card_recent.render(a, LIGHT)
    assert 'data-t="repo2"' in out and 'data-t="repo3"' not in out


def test_taller_with_more_repos():
    one = dict(BASE, repos=BASE["repos"][:1])
    h = lambda s: float(check(s).get("viewBox").split()[3])
    assert h(card_recent.render(BASE, LIGHT)) > h(card_recent.render(one, LIGHT))


def test_none():
    assert card_recent.render({"totals": {"repos": 0, "commits": 0}, "repos": []}, LIGHT) is None


def test_hostile_text():
    a = copy.deepcopy(BASE)
    a["repos"][0]["name"] = "a-very-long-repository-name-" * 6
    a["repos"][0]["description"] = 'Tom & Jerry <b>"quoted"</b> 🚀 数据 ' * 20
    a["repos"][0]["highlights"][0]["title"] = "x" * 500
    root = check(card_recent.render(a, LIGHT))
    for el in root.iter():
        t = el.get("data-t")
        if t:
            assert "🚀" not in t and "数" not in t and len(t) < 200


def test_singular():
    a = copy.deepcopy(BASE)
    a["repos"][0]["commits"] = 1
    assert 'data-t="1 commit · active Nov 21"' in card_recent.render(a, LIGHT)


def test_emoji_only_description_and_title_are_skipped():
    a = copy.deepcopy(BASE)
    a["repos"][0]["description"] = "音乐播放器"
    a["repos"][0]["highlights"] = [{"kind": "commit", "title": "🎉", "date": "2026-11-21"},
                                   {"kind": "commit", "title": "real work", "date": "2026-11-20"}]
    a["repos"][1]["highlights"] = []
    out = card_recent.render(a, LIGHT)
    check(out)
    assert 'data-t=""' not in out and out.count('data-t="commit"') == 1 and 'data-t="real work"' in out
