"""
Recently card. One SVG per repo so each can link to its repo; the README
stacks them with no gap so they read as a single card.
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
        y += 8
        out += outline(PAD_X, y + 1, 58, 17, 8.5, theme)
        out += tp.text(PAD_X + 29, y + 13.5, h["kind"], "text-400", 11, theme.muted, anchor="middle")
        title = tp.fit(h["title"], "text-400", 13, INNER_RIGHT - (PAD_X + 68))
        out += tp.text(PAD_X + 68, y + 14, title, "text-400", 13, theme.ink)
        y += 19
    return out, y


def render(activity: dict, theme: Theme) -> list[str]:
    repos = activity.get("repos", [])[:MAX_REPOS]
    slices = []
    for i, repo in enumerate(repos):
        first, last = i == 0, i == len(repos) - 1
        if first:
            totals = activity["totals"]
            head = label(PAD_X, PAD_Y + 10, "Recently", theme)
            head += tp.text(INNER_RIGHT, PAD_Y + 10,
                            f"last 30 days · {_plural(totals['commits'], 'commit')} · {_plural(totals['repos'], 'repo')}",
                            "text-400", 12, theme.muted, anchor="end")
            y = PAD_Y + 15 + 16
        else:
            head = hairline(PAD_X, 0.5, INNER_RIGHT, 0.5, theme)
            y = 16
        block, y = _repo(y, repo, theme)
        height = y + (PAD_Y if last else 16)
        corners = "all" if first and last else "top" if first else "bottom" if last else "none"
        slices.append(doc(height, panel(W, height, theme, corners) + head + block))
    return slices
