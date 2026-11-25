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
    render.build(str(root), NOW)
    names = {p.name for p in (root / "profile").glob("*.svg")}
    assert {"banner-left-light.svg", "banner-art-dark.svg", "streak-light.svg", "contributions-dark.svg",
            "recent-1-light.svg"} <= names
    md = (root / "README.md").read_text()
    assert "{{" not in md and md.count("<picture>") >= 5
    assert 'href="https://www.linkedin.com/in/kevinyinkyy"' in md and "49.074%" in md and "50.926%" in md
    assert re.search(r"</a><a [^>]*kevinyyin/", md)  # recent slices touch, no whitespace
    for src in re.findall(r'(?:src|srcset)="\./([^"]+)"', md):
        assert (root / src).exists(), src


def test_no_activity(tmp_path):
    root = make_root(tmp_path, activity=False)
    render.build(str(root), NOW)
    assert "recent-1" not in (root / "README.md").read_text()


def test_bad_activity_and_stale_slices(tmp_path):
    root = make_root(tmp_path)
    render.build(str(root), NOW)
    (root / "data/activity.json").write_text("{not json")
    render.build(str(root), NOW)
    assert not list((root / "profile").glob("recent-*.svg")) and "recent-1" not in (root / "README.md").read_text()
