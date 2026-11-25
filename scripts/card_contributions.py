"""Contributions card: the last 26 weeks as a grid of day squares."""
from datetime import date

import stats
import textpath as tp
from svg import doc, label, n, panel
from theme import PAD_X, PAD_Y, W, Theme

HEIGHT = 262
WEEKS = 26
GAP = 3
TOP = 53


def render(data: dict, theme: Theme, today: date) -> str:
    columns = stats.grid(data["days"], today, WEEKS)
    inner = W - 2 * PAD_X
    cell = (inner - (WEEKS - 1) * GAP) / WEEKS
    step = cell + GAP
    body = panel(W, HEIGHT, theme) + label(PAD_X, PAD_Y + 10, "Contributions", theme)
    body += tp.text(W - PAD_X, PAD_Y + 10, f"{stats.window_total(columns):,} in the last six months",
                    "text-400", 12, theme.muted, anchor="end")
    for c, col in enumerate(columns):
        for r, day in enumerate(col):
            if day is None:
                continue
            kind, opacity = stats.shade(day["count"])
            fill = (f'fill="{theme.accent}"' if kind == "accent"
                    else f'fill="{theme.ink}" fill-opacity="{n(opacity)}"')
            body += (f'<rect class="d" x="{n(PAD_X + c * step)}" y="{n(TOP + r * step)}" '
                     f'width="{n(cell)}" height="{n(cell)}" rx="4" {fill}/>')
    months_y = TOP + 7 * step - GAP + 19
    for c, name in stats.month_labels(columns):
        body += tp.text(PAD_X + c * step, months_y, name, "text-400", 12, theme.muted)
    return doc(HEIGHT, body)
