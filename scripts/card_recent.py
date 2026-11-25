"""
Recently card: up to three repos in one image. (Slicing it per repo, so each
could link to its own repo, leaves hairline seams on GitHub at fractional
pixel sizes, so the whole card links to the repositories tab instead.)
"""
import stats
import textpath as tp
from svg import doc, hairline, label, outline, panel
from theme import PAD_X, PAD_Y, W, Theme

MAX_REPOS = 3
INNER_RIGHT = W - PAD_X


def _plural(count: int, word: str) -> str:
    return f"{count:,} {word}" + ("" if count == 1 else "s")


def _repo(y: float, repo: dict, theme: Theme) -> tuple[str, float]:
    """Draw one repo block starting at y; returns (svg, y after the block)."""
    meta = _plural(repo["commits"], "commit")
    if repo.get("merged"):
        meta += f" · {repo['merged']} merged"
    meta += f" · active {stats.fmt_date(repo['last_active'])}"
    meta_w = tp.measure(meta, "text-400", 12)
    lang = tp.clean(repo.get("language") or "", "text-400")
    lang_w = tp.measure(lang, "text-400", 12) + 10 if lang else 0
    name_room = max(60.0, INNER_RIGHT - PAD_X - meta_w - 16 - lang_w)
    name = tp.fit(repo["name"], "display-500", 20, name_room)
    base = y + 20
    out = tp.text(PAD_X, base, name, "display-500", 20, theme.ink)
    if lang:
        out += tp.text(PAD_X + tp.measure(name, "display-500", 20) + 10, base, lang, "text-400", 12, theme.muted)
    out += tp.text(INNER_RIGHT, base, meta, "text-400", 12, theme.muted, anchor="end")
    y += 26
    if repo.get("description"):
        desc = tp.fit(repo["description"], "text-400", 13, INNER_RIGHT - PAD_X)
        if desc:
            out += tp.text(PAD_X, y + 6 + 13, desc, "text-400", 13, theme.muted)
            y += 6 + 18
    for h in repo.get("highlights", []):
        title = tp.fit(h["title"], "text-400", 13, INNER_RIGHT - (PAD_X + 68))
        if not title:  # nothing drawable (emoji-only, say): no row rather than an empty pill
            continue
        y += 8
        out += outline(PAD_X, y + 1, 58, 17, 8.5, theme)
        out += tp.text(PAD_X + 29, y + 13.5, h["kind"], "text-400", 11, theme.muted, anchor="middle")
        out += tp.text(PAD_X + 68, y + 14, title, "text-400", 13, theme.ink)
        y += 19
    return out, y


def render(activity: dict, theme: Theme) -> str | None:
    """The whole card, or None when no repo qualifies."""
    repos = activity.get("repos", [])[:MAX_REPOS]
    if not repos:
        return None
    totals = activity["totals"]
    body = label(PAD_X, PAD_Y + 10, "Recently", theme)
    body += tp.text(INNER_RIGHT, PAD_Y + 10,
                    f"last 30 days · {_plural(totals['commits'], 'commit')} · {_plural(totals['repos'], 'repo')}",
                    "text-400", 12, theme.muted, anchor="end")
    y = PAD_Y + 15 + 16
    for i, repo in enumerate(repos):
        if i:
            body += hairline(PAD_X, y + 16.5, INNER_RIGHT, y + 16.5, theme)
            y += 32
        block, y = _repo(y, repo, theme)
        body += block
    height = y + PAD_Y
    return doc(height, panel(W, height, theme) + body)
