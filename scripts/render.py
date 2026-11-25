#!/usr/bin/env python3
"""
Build the profile: read data/*.json and profile/config.json, write every card
to profile/ in light and dark, and fill README.md from the template.
"""
import glob
import json
import os
import sys
from datetime import date, datetime, timezone
from html import escape

import card_banner
import card_contributions
import card_recent
import card_streak
import stats
from theme import THEMES

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")


def picture(stem: str, alt: str, href: str | None = None) -> str:
    """One card as theme-aware README markup: GitHub serves the dark file to dark-mode visitors."""
    out = (f'<picture><source media="(prefers-color-scheme: dark)" srcset="./{stem}-dark.svg">'
           f'<img src="./{stem}-light.svg" width="100%" alt="{escape(alt, quote=True)}"></picture>')
    return f'<a href="{escape(href, quote=True)}">{out}</a>' if href else out


def _load(path: str):
    try:
        with open(path) as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def build(root: str, now: datetime) -> None:
    profile = os.path.join(root, "profile")
    with open(os.path.join(root, "data", "contributions.json")) as f:
        contrib = json.load(f)
    with open(os.path.join(profile, "config.json")) as f:
        config = json.load(f)
    activity = _load(os.path.join(root, "data", "activity.json"))
    if not isinstance(activity, dict) or not activity.get("repos"):
        activity = None  # no Recently card; the banner's fallback panel is skipped too
    card_banner.ROOT = root
    last_day = date.fromisoformat(contrib["days"][-1]["date"])  # saved data is shown as saved, never re-dated

    written = set()

    def write(slug: str, theme, svg: str) -> None:
        path = os.path.join(profile, f"{slug}-{theme.name}.svg")
        with open(path, "w") as f:
            f.write(svg)
        written.add(path)

    for theme in THEMES:
        write("banner", theme, card_banner.render(config, theme, activity))
        write("streak", theme, card_streak.render(contrib, theme, now))
        write("contributions", theme, card_contributions.render(contrib, theme, last_day))
        recent = card_recent.render(activity, theme) if activity else None
        if recent:
            write("recent", theme, recent)

    for path in glob.glob(os.path.join(profile, "recent*.svg")) + glob.glob(os.path.join(profile, "banner*.svg")):
        if path not in written:
            os.remove(path)  # no qualifying repos any more, or files from an older layout

    links, art = config.get("links") or [], config.get("art") or {}
    banner_alt = f"{config['name']}. {config['tagline']}" + "".join(f" {l['text']}: {l['url']}" for l in links)
    banner_md = picture("profile/banner", banner_alt, href=links[0]["url"] if links else None)
    recent_md = credit_md = ""
    if recent:
        shown = activity["repos"][:card_recent.MAX_REPOS]
        recent_alt = (f"Recently: {', '.join(r['name'] for r in shown)}. "
                      f"{activity['totals']['commits']:,} commits in the last 30 days")
        recent_md = picture("profile/recent", recent_alt,
                            href=f"https://github.com/{contrib['username']}?tab=repositories")
    if art.get("url") and art.get("credit"):
        credit_md = f'<sub><a href="{escape(art["url"], quote=True)}">Banner {escape(art["credit"])}</a></sub>'

    weeks = stats.weekly_streak(contrib["days"], last_day)
    streak_alt = (f"{contrib['current_streak']['length']} day streak; {weeks} weeks in a row; "
                  f"{contrib['total_contributions']:,} contributions in the last 12 months")
    window = stats.window_total(stats.grid(contrib["days"], last_day))
    with open(os.path.join(profile, "README.template.md")) as f:
        md = f.read()
    md = (md.replace("{{banner}}", banner_md)
            .replace("{{streak}}", picture("profile/streak", streak_alt))
            .replace("{{contributions}}", picture("profile/contributions", f"{window:,} contributions in the last six months"))
            .replace("{{recent}}", recent_md)
            .replace("{{credit}}", credit_md))
    with open(os.path.join(root, "README.md"), "w") as f:
        f.write(md)


def main() -> None:
    build(ROOT, datetime.now(timezone.utc))
    print("rendered profile cards and README.md")


if __name__ == "__main__":
    sys.exit(main())
