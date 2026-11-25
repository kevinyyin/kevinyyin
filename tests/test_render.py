import json
import re
import shutil
from datetime import datetime, timezone

import render

NOW = datetime(2026, 11, 25, 3, tzinfo=timezone.utc)


def make_root(tmp_path, activity=True):
    for d in ("profile", "data"):
        (tmp_path / d).mkdir()
    shutil.copytree("profile/art", tmp_path / "profile/art")
    for f in ("config.json", "README.template.md"):
        shutil.copy(f"profile/{f}", tmp_path / "profile" / f)
    shutil.copy("tests/fixtures/contributions.json", tmp_path / "data/contributions.json")
    if activity:
        shutil.copy("tests/fixtures/activity.json", tmp_path / "data/activity.json")
    return tmp_path


def test_build(tmp_path):
    root = make_root(tmp_path)
    for stale in ("recent-1-light.svg", "banner-left-dark.svg"):  # files from the old sliced layout
        (root / "profile" / stale).write_text("<svg/>")
    render.build(str(root), NOW)
    names = {p.name for p in (root / "profile").glob("*.svg")}
    assert names == {f"{c}-{t}.svg" for c in ("banner", "streak", "contributions", "recent") for t in ("light", "dark")}
    md = (root / "README.md").read_text()
    assert "{{" not in md and md.count("<picture>") == 4
    assert 'href="https://www.linkedin.com/in/kevinyinkyy"' in md
    assert 'href="https://github.com/kevinyyin?tab=repositories"' in md
    assert "LennSan</a>" not in md  # no artist link until config has the post URL
    for src in re.findall(r'(?:src|srcset)="\./([^"]+)"', md):
        assert (root / src).exists(), src


def test_artist_link_when_configured(tmp_path):
    root = make_root(tmp_path)
    cfg = json.loads((root / "profile/config.json").read_text())
    cfg["art"]["url"] = "https://example.com/post?a=1&b=2"
    (root / "profile/config.json").write_text(json.dumps(cfg))
    render.build(str(root), NOW)
    assert '<a href="https://example.com/post?a=1&amp;b=2">Banner art by LennSan</a>' in (root / "README.md").read_text()


def test_no_activity(tmp_path):
    root = make_root(tmp_path, activity=False)
    render.build(str(root), NOW)
    assert "profile/recent" not in (root / "README.md").read_text()


def test_bad_activity_removes_recent_card(tmp_path):
    root = make_root(tmp_path)
    render.build(str(root), NOW)
    (root / "data/activity.json").write_text("{not json")
    render.build(str(root), NOW)
    assert not list((root / "profile").glob("recent*.svg")) and "profile/recent" not in (root / "README.md").read_text()


def test_unsupported_text_in_activity_does_not_stop_the_build(tmp_path):
    root = make_root(tmp_path)
    act = json.loads((root / "data/activity.json").read_text())
    act["repos"][0]["description"] = "🚀✨"
    act["repos"][0]["language"] = "中文"
    act["repos"][0]["highlights"] = [{"kind": "commit", "title": "🎉", "date": "2026-11-21"}]
    (root / "data/activity.json").write_text(json.dumps(act))
    render.build(str(root), NOW)
    assert "profile/recent" in (root / "README.md").read_text()
