"""Streak card: the ring with the current streak, and four number tiles."""
from datetime import date, datetime

import stats
import textpath as tp
from svg import doc, label, n, outline, panel, value_size
from theme import PAD_X, PAD_Y, W, Theme

HEIGHT = 266
CSS = ".orb{animation:orb 16s linear infinite;transform-origin:100px 100px}@keyframes orb{to{transform:rotate(360deg)}}"


def _ring(data: dict, theme: Theme) -> str:
    """Drawn in a 200-unit box, as in the mockup, then placed at 0.9 scale."""
    number = str(data["current_streak"]["length"])
    size = value_size(number, "display-500", 64, 130, -2 / 64)
    return (
        '<svg x="38" y="44" width="180" height="180" viewBox="0 0 200 200">'
        f'<circle cx="100" cy="100" r="82" fill="none" stroke="{theme.ink}" stroke-opacity="{theme.line_opacity}" stroke-width="2"/>'
        f'<circle cx="100" cy="100" r="82" fill="none" stroke="{theme.accent}" stroke-width="3" stroke-dasharray="3 5.59"/>'
        f'<g class="orb"><circle cx="100" cy="18" r="6" fill="{theme.ink}"/></g>'
        + tp.text(100, 100 + size * 0.19, number, "display-500", size, theme.ink, anchor="middle", tracking=-2 / 64)
        + tp.text(100, 136, "day streak", "text-400", 13, theme.muted, anchor="middle")
        + "</svg>"
    )


def _tile(x: float, y: float, w: float, h: float, name: str, value: str, unit: str, sub: str, theme: Theme) -> str:
    size = value_size(value, "display-500", 32, 150, -0.03)
    out = outline(x, y, w, h, 14, theme) + label(x + 16, y + 25, name, theme)
    out += tp.text(x + 16, y + 62, value, "display-500", size, theme.ink, tracking=-0.03)
    if unit:
        out += tp.text(x + 16 + tp.measure(value, "display-500", size, -0.03) + 6, y + 62, unit, "display-500", 14, theme.ink)
    return out + tp.text(x + 16, y + 81, sub, "text-400", 12, theme.muted)


def render(data: dict, theme: Theme, now: datetime) -> str:
    today = date.fromisoformat(data["days"][-1]["date"])  # saved data is shown as saved, never re-dated
    weeks = stats.weekly_streak(data["days"], today)
    best = data["best_day"]
    body = panel(W, HEIGHT, theme) + label(PAD_X, PAD_Y + 10, "Streak", theme) + _ring(data, theme)
    body += tp.text(128, 241, stats.streak_caption(data), "text-400", 12, theme.muted, anchor="middle")
    x0, tw, th, gap = 256, 177, 97, 10
    tiles = [
        ("Weekly streak", str(weeks), "week" if weeks == 1 else "weeks", "in a row with activity"),
        ("Active days", f"{data['active_days']:,}", "", "in the last 12 months"),
        ("Contributions", f"{data['total_contributions']:,}", "", "in the last 12 months"),
        ("Best day", f"{best['count']:,}", "", stats.fmt_date(best["date"], year=True)),
    ]
    for i, (name, value, unit, sub) in enumerate(tiles):
        body += _tile(x0 + (i % 2) * (tw + gap), 31 + (i // 2) * (th + gap), tw, th, name, value, unit, sub, theme)
    stale = stats.as_of(data["generated_at"], now)
    if stale:
        body += tp.text(W - PAD_X, HEIGHT - 9, stale, "text-400", 11, theme.muted, anchor="end")
    return doc(HEIGHT, body, CSS)
