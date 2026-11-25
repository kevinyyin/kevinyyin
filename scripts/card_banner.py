"""
Banner. With artwork it is two slices side by side (so each half can carry its
own link): the name with its spark on the left, the animated pixel-art scene
fading into the paper on the right. With config["art"] set to null it is one
slice with a "Now building" panel instead.
"""
import base64
import os

import textpath as tp
from svg import doc, label, n, outline, panel, panel_path
from theme import PAD_X, W, Theme

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
HEIGHT = 208
LEFT_W = 318
ART_W = W - LEFT_W
FADE_END = 0.62          # the art is fully opaque from this fraction of its slice
NAME_SIZE = 128          # the name is drawn at mockup size, then scaled
NAME_SCALE = 232 / 525
NAME_TRACKING = -5 / 128
CREDIT_FILL = "#F6EFE2"

SPARK_CSS = (
    ".da,.db,.rg,.lv{{transform-box:fill-box;transform-origin:center}}"
    ".da{{animation:da 6s infinite}}.db{{animation:db 6s infinite}}.rg{{animation:rg 6s infinite}}"
    ".sp{{offset-rotate:0deg;animation:sp 6s infinite}}.tr{{animation:tr 6s infinite}}"
    "@keyframes da{{0%,3%,14%,100%{{transform:scale(1)}}8%{{transform:scale(1.3)}}}}"
    "@keyframes sp{{0%,9%{{offset-distance:0%;opacity:0}}10%{{offset-distance:0%;opacity:1;"
    "animation-timing-function:cubic-bezier(.45,0,.55,1)}}32%{{offset-distance:100%;opacity:1}}"
    "33%,100%{{offset-distance:100%;opacity:0}}}}"
    "@keyframes tr{{0%,9%{{stroke-dashoffset:1;opacity:0}}10%{{stroke-dashoffset:1;opacity:.8;"
    "animation-timing-function:cubic-bezier(.45,0,.55,1)}}32%{{stroke-dashoffset:0;opacity:.8}}"
    "52%,100%{{stroke-dashoffset:0;opacity:0}}}}"
    "@keyframes db{{0%,31%,62%,100%{{transform:scale(1);fill:{ink}}}34%{{transform:scale(1.45);fill:{accent}}}"
    "48%{{transform:scale(1);fill:{accent}}}}}"
    "@keyframes rg{{0%,32%{{transform:scale(1);opacity:0}}33%{{transform:scale(1);opacity:.9}}"
    "56%,100%{{transform:scale(3.4);opacity:0}}}}"
)
PULSE_CSS = ".lv{animation:lv 2.4s ease-out infinite}@keyframes lv{0%{transform:scale(1);opacity:.7}100%{transform:scale(3);opacity:0}}"


def _name(config: dict, theme: Theme) -> str:
    """The name at mockup size: dotless letters, our own dots, and the spark between the first two."""
    name = config["name"]
    out = tp.text(0, NAME_SIZE, name, "display-600", NAME_SIZE, theme.ink, tracking=NAME_TRACKING, dotless=True)
    dots = [(cx, NAME_SIZE + cy, r) for cx, cy, r in tp.i_dots(name, "display-600", NAME_SIZE, NAME_TRACKING)]
    if len(dots) >= 2:
        (ax, ay, ar), (bx, by, br) = dots[0], dots[1]
        arc = f"M{n(ax)} {n(ay)}Q{n((ax + bx) / 2)} {n(min(ay, by) - 92)} {n(bx)} {n(by)}"
        out += (f'<path class="fx tr" d="{arc}" fill="none" stroke="{theme.accent}" stroke-width="3" '
                'stroke-linecap="round" pathLength="1" stroke-dasharray="1" opacity="0"/>')
        out += (f'<circle class="fx rg" cx="{n(bx)}" cy="{n(by)}" r="{n(br)}" fill="none" '
                f'stroke="{theme.accent}" stroke-width="2" opacity="0"/>')
    for i, (cx, cy, r) in enumerate(dots):
        cls = ' class="da"' if i == 0 and len(dots) >= 2 else ' class="db"' if i == 1 else ""
        out += f'<circle{cls} cx="{n(cx)}" cy="{n(cy)}" r="{n(r)}" fill="{theme.ink}"/>'
    if len(dots) >= 2:
        out += f'<circle class="fx sp" r="7" fill="{theme.accent}" opacity="0" style="offset-path:path(\'{arc}\')"/>'
    return f'<g transform="translate({PAD_X - 2},35.5) scale({NAME_SCALE:.4f})">{out}</g>'


def _text_block(config: dict, theme: Theme) -> str:
    out = label(PAD_X, 25.5, config["label"], theme, fill=theme.accent) + _name(config, theme)
    y = 128.0
    for line in tp.wrap(config["tagline"], "text-400", 14, 270):
        out += tp.text(PAD_X, y, line, "text-400", 14, theme.ink)
        y += 20.3
    x = PAD_X
    for link in config.get("links", []):
        caption = f"{link['text']} ↗"
        w = tp.measure(caption, "text-400", 12) + 26
        out += outline(x, 166.5, w, 27, 13.5, theme) + tp.text(x + 13, 184.3, caption, "text-400", 12, theme.ink)
        x += w + 8
    return out


def _spark_css(theme: Theme) -> str:
    return SPARK_CSS.format(ink=theme.ink, accent=theme.accent)


def _art_slice(art: dict, theme: Theme) -> str:
    with open(os.path.join(ROOT, art["strip"]), "rb") as f:
        data = base64.b64encode(f.read()).decode()
    fw, fh, inset = art["frame_w"], art["frame_h"], art.get("inset", 0)
    cols, rows = art["cols"], art["rows"]
    sheet_w, sheet_h = fw * cols, fh * rows
    row_secs = cols / art["fps"]
    css = (f".ax{{animation:ax {n(row_secs)}s steps({cols}) infinite}}"
           f".ay{{animation:ay {n(row_secs * rows)}s steps({rows}) infinite}}"
           f"@keyframes ax{{to{{transform:translateX(-{sheet_w}px)}}}}"
           f"@keyframes ay{{to{{transform:translateY(-{sheet_h}px)}}}}")
    body = (
        "<defs>"
        f'<clipPath id="c"><path d="{panel_path(ART_W, HEIGHT, "right")}"/></clipPath>'
        f'<linearGradient id="g" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="{n(ART_W * FADE_END)}" y2="0">'
        '<stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#fff"/></linearGradient>'
        f'<mask id="m" maskUnits="userSpaceOnUse" x="0" y="0" width="{ART_W}" height="{HEIGHT}">'
        f'<rect width="{ART_W}" height="{HEIGHT}" fill="url(#g)"/></mask>'
        "</defs>"
        + panel(ART_W, HEIGHT, theme, "right")
        + '<g clip-path="url(#c)"><g mask="url(#m)">'
        # one frame of the sheet shows through this window; the two step animations walk the grid
        f'<svg width="{ART_W}" height="{HEIGHT}" viewBox="{inset} {inset} {fw - 2 * inset} {fh - 2 * inset}" '
        'preserveAspectRatio="xMidYMid slice">'
        f'<g class="ay"><g class="ax"><image width="{sheet_w}" height="{sheet_h}" '
        f'style="image-rendering:pixelated" href="data:image/png;base64,{data}"/></g></g>'
        "</svg></g></g>"
    )
    if art.get("credit"):
        body += tp.text(ART_W - 12, HEIGHT - 12, art["credit"], "text-400", 11, CREDIT_FILL, anchor="end", opacity=0.8)
    return doc(HEIGHT, body, css, width=ART_W)


def _now_building(activity: dict | None, theme: Theme) -> str:
    repos = (activity or {}).get("repos") or []
    if not repos:
        return ""
    repo = repos[0]
    w, h = 188, 122
    x, y = W - PAD_X - w, HEIGHT - 24 - h
    out = outline(x, y, w, h, 14, theme)
    out += f'<circle class="fx lv" cx="{x + 21}" cy="{y + 21}" r="4" fill="{theme.accent}"/>'
    out += f'<circle cx="{x + 21}" cy="{y + 21}" r="4" fill="{theme.accent}"/>'
    out += label(x + 34, y + 25, "Now building", theme)
    out += tp.text(x + 16, y + 63, tp.fit(repo["name"], "display-500", 26, w - 32), "display-500", 26, theme.ink,
                   tracking=-0.02)
    count = repo.get("commits", 0)
    out += tp.text(x + 16, y + 84, f"{count:,} commit{'' if count == 1 else 's'} this month", "text-400", 12, theme.muted)
    if repo.get("language"):
        out += tp.text(x + 16, y + 102, repo["language"], "text-400", 12, theme.muted)
    return out


def render(config: dict, theme: Theme, activity: dict | None) -> list[tuple[str, str, float, str | None]]:
    """[(slug, svg, width in card units, link or None), ...] left to right."""
    links = config.get("links") or []
    main_link = links[0]["url"] if links else None
    art = config.get("art")
    if art:
        left = doc(HEIGHT, panel(LEFT_W, HEIGHT, theme, "left") + _text_block(config, theme),
                   _spark_css(theme), width=LEFT_W)
        return [("banner-left", left, LEFT_W, main_link), ("banner-art", _art_slice(art, theme), ART_W, art.get("url"))]
    body = panel(W, HEIGHT, theme) + _text_block(config, theme) + _now_building(activity, theme)
    return [("banner", doc(HEIGHT, body, _spark_css(theme) + PULSE_CSS), W, main_link)]
