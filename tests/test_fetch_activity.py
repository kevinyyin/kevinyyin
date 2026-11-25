import json
from datetime import datetime, timezone

import pytest

import fetch_activity as fa

NOW = datetime(2026, 11, 25, 3, tzinfo=timezone.utc)


def repo(name, **kw):
    return {"name": name, "html_url": f"https://github.com/kevinyyin/{name}", "private": False, "fork": False,
            "owner": {"login": "kevinyyin"}, "description": None, "language": "Python", **kw}


def commit(msg, day, login="kevinyyin"):
    return {"commit": {"message": msg, "author": {"date": f"{day}T12:00:00Z"}}, "author": {"login": login}}


def pull(title, merged, login="kevinyyin"):
    return {"title": title, "merged_at": merged and f"{merged}T12:00:00Z", "user": {"login": login}}


def test_selection_and_order():
    repos = [repo("old"), repo("Witness"), repo("struum"), repo("kevinyyin"), repo("secret", private=True),
             repo("forked", fork=True)]
    commits = {"old": [commit("x", "2026-09-01")], "Witness": [commit("a", "2026-11-21"), commit("b", "2026-11-20")],
               "struum": [commit("c", "2026-11-19")], "kevinyyin": [commit("chore", "2026-11-24")],
               "secret": [commit("s", "2026-11-22")], "forked": [commit("f", "2026-11-22")]}
    out = fa.build_activity("kevinyyin", repos, commits, {}, NOW)
    assert [r["name"] for r in out["repos"]] == ["Witness", "struum"]
    assert out["totals"] == {"repos": 2, "commits": 3}
    assert out["repos"][0]["commits"] == 2 and out["repos"][0]["last_active"] == "2026-11-21"


def test_highlights_prefer_merged():
    merged = [pull("Phone home screen", "2026-11-19"), pull("Too old", "2026-09-01"),
              pull("Not mine", "2026-11-20", "someone")]
    commits = {"struum": [commit("fix: one\n\nbody", "2026-11-21"), commit("Merge pull request #3", "2026-11-19"),
                          commit("bump", "2026-11-18", "dependabot[bot]"), commit("fix: two", "2026-11-17")]}
    r = fa.build_activity("kevinyyin", [repo("struum")], commits, {"struum": merged}, NOW)["repos"][0]
    assert r["merged"] == 1
    assert [(h["kind"], h["title"]) for h in r["highlights"]] == [("merged", "Phone home screen"), ("commit", "fix: one")]


def test_no_repos():
    assert fa.build_activity("kevinyyin", [], {}, {}, NOW)["repos"] == []


def test_failed_fetch_keeps_file(tmp_path, monkeypatch):
    out = tmp_path / "activity.json"
    out.write_text('{"keep": true}')
    monkeypatch.setattr(fa, "OUT_PATH", str(out))
    monkeypatch.setenv("GH_PROFILE_USER", "kevinyyin")

    def boom(*a, **k):
        raise fa.requests.ConnectionError("down")

    monkeypatch.setattr(fa.requests, "get", boom)
    with pytest.raises(SystemExit) as e:
        fa.main()
    assert e.value.code == 1 and json.loads(out.read_text()) == {"keep": True}


def test_squash_commit_does_not_repeat_its_pull_request():
    merged = [pull("Phone home screen", "2026-11-19")]
    commits = [commit("Phone home screen (#4)", "2026-11-19"), commit("fix: two", "2026-11-17")]
    got = fa.pick_highlights(merged, commits)
    assert [(h["kind"], h["title"]) for h in got] == [("merged", "Phone home screen"), ("commit", "fix: two")]
