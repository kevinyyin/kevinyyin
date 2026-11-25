#!/usr/bin/env python3
"""
Fetch the last 30 days of public work from the GitHub REST API and write
data/activity.json for the "Recently" card. Needs GH_PROFILE_USER; uses
GITHUB_TOKEN when set. On any failure the saved file is left untouched and
the script exits 1, so the cards keep rendering from the last good data.
"""
import json
import os
import sys
from datetime import datetime, timedelta, timezone

import requests

OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "activity.json")
API = "https://api.github.com"
MAX_COMMIT_PAGES = 10


def _login(obj: dict, key: str) -> str:
    return ((obj.get(key) or {}).get("login")) or ""


def _subject(commit: dict) -> str:
    return commit["commit"]["message"].split("\n", 1)[0].strip()


def pick_highlights(merged: list[dict], commits: list[dict], limit: int = 2) -> list[dict]:
    out = [{"kind": "merged", "title": p["title"].strip(), "date": p["merged_at"][:10]}
           for p in sorted(merged, key=lambda p: p["merged_at"], reverse=True)]
    titles = [h["title"] for h in out]
    for c in sorted(commits, key=lambda c: c["commit"]["author"]["date"], reverse=True):
        subject = _subject(c)
        if subject.startswith("Merge ") or _login(c, "author").endswith("[bot]"):
            continue
        if any(subject.startswith(t) for t in titles):  # squash-merge commit repeats its PR title
            continue
        out.append({"kind": "commit", "title": subject, "date": c["commit"]["author"]["date"][:10]})
    return out[:limit]


def build_activity(user: str, repos: list[dict], commits: dict[str, list[dict]],
                   pulls: dict[str, list[dict]], now: datetime, window_days: int = 30) -> dict:
    since = (now - timedelta(days=window_days)).strftime("%Y-%m-%dT%H:%M:%SZ")
    rows = []
    for r in repos:
        if r.get("private") or r.get("fork") or _login(r, "owner") != user or r["name"] == user:
            continue
        mine = [c for c in commits.get(r["name"], [])
                if _login(c, "author") == user and c["commit"]["author"]["date"] >= since]
        if not mine:
            continue
        merged = [p for p in pulls.get(r["name"], [])
                  if p.get("merged_at") and p["merged_at"] >= since and _login(p, "user") == user]
        rows.append({
            "name": r["name"],
            "url": r["html_url"],
            "description": r.get("description"),
            "language": r.get("language"),
            "commits": len(mine),
            "merged": len(merged),
            "last_active": max(c["commit"]["author"]["date"] for c in mine)[:10],
            "highlights": pick_highlights(merged, mine),
        })
    rows.sort(key=lambda r: (r["last_active"], r["commits"]), reverse=True)
    return {
        "username": user,
        "fetched_at": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "window_days": window_days,
        "totals": {"repos": len(rows), "commits": sum(r["commits"] for r in rows)},
        "repos": rows,
    }


def _get(path: str, headers: dict, **params):
    resp = requests.get(API + path, headers=headers, params=params, timeout=30)
    if resp.status_code == 409:  # empty repository
        return []
    resp.raise_for_status()
    return resp.json()


def main() -> None:
    user = os.environ["GH_PROFILE_USER"]
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "profile-readme-bot/1.0"}
    if os.environ.get("GITHUB_TOKEN"):
        headers["Authorization"] = f"Bearer {os.environ['GITHUB_TOKEN']}"
    now = datetime.now(timezone.utc)
    since = (now - timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%SZ")
    try:
        repos = _get(f"/users/{user}/repos", headers, type="owner", sort="pushed", per_page=100)
        commits, pulls = {}, {}
        for r in repos:
            if r.get("private") or r.get("fork") or r["name"] == user or (r.get("pushed_at") or "") < since:
                continue
            got = []
            for page in range(1, MAX_COMMIT_PAGES + 1):
                batch = _get(f"/repos/{user}/{r['name']}/commits", headers,
                             author=user, since=since, per_page=100, page=page)
                got += batch
                if len(batch) < 100:
                    break
            commits[r["name"]] = got
            pulls[r["name"]] = _get(f"/repos/{user}/{r['name']}/pulls", headers,
                                    state="closed", sort="updated", direction="desc", per_page=50)
        data = build_activity(user, repos, commits, pulls, now)
    except (requests.RequestException, KeyError, TypeError, ValueError) as e:
        print(f"activity fetch failed, keeping the saved file: {e}", file=sys.stderr)
        sys.exit(1)
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w") as f:
        json.dump(data, f, indent=1)
    print(f"wrote {OUT_PATH}: {data['totals']['repos']} repos, {data['totals']['commits']} commits")


if __name__ == "__main__":
    main()
