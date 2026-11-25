"""
Text as vector outlines. Every string on a card is shaped with HarfBuzz (so
kerning matches a browser) and drawn as one <path>, which means the cards look
the same everywhere, need no embedded fonts, and have geometry we can measure.
"""
import functools
import os
from xml.sax.saxutils import quoteattr

import uharfbuzz as hb
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

FONT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
FONT_FILES = {
    "display-600": "Outfit-SemiBold.ttf",
    "display-500": "Outfit-Medium.ttf",
    "text-400": "Inter-Regular.ttf",
    "text-500": "Inter-Medium.ttf",
}
FONT_KEYS = tuple(FONT_FILES)
FEATURES = {"kern": True, "liga": False}  # one glyph per character keeps i_dots simple


def _num(v: float) -> str:
    return f"{v:.2f}".rstrip("0").rstrip(".")


@functools.cache
def _font(key: str):
    path = os.path.join(FONT_DIR, FONT_FILES[key])
    tt = TTFont(path)
    hbfont = hb.Font(hb.Face(hb.Blob.from_file_path(path)))
    return tt, hbfont, tt.getGlyphSet(), tt["head"].unitsPerEm, tt.getBestCmap()


def clean(s: str, font: str) -> str:
    cmap = _font(font)[4]
    # keep what the font can draw; whitespace becomes a space; control characters and the rest are dropped
    kept = "".join(" " if c.isspace() else c if (ord(c) in cmap and c.isprintable()) else "" for c in s)
    return " ".join(kept.split())


@functools.cache
def _shape(s: str, font: str) -> tuple[tuple[str, float, float, float], ...]:
    """Glyphs in font units: (glyph name, x of origin, y offset, advance)."""
    if not s:  # HarfBuzz gives None, not [], for an empty buffer
        return ()
    tt, hbfont, _, _, _ = _font(font)
    buf = hb.Buffer()
    buf.add_str(s)
    buf.guess_segment_properties()
    hb.shape(hbfont, buf, FEATURES)
    out, x = [], 0.0
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        out.append((tt.getGlyphName(info.codepoint), x + pos.x_offset, pos.y_offset, pos.x_advance))
        x += pos.x_advance
    return tuple(out)


def _layout(s: str, font: str, size: float, tracking: float):
    """(glyphs as (name, x, y_offset) in SVG units before the y flip, total width)."""
    upem = _font(font)[3]
    k = size / upem
    gap = tracking * size
    glyphs = [(name, x * k + i * gap, yoff * k) for i, (name, x, yoff, _) in enumerate(_shape(s, font))]
    shaped = _shape(s, font)
    width = (sum(g[3] for g in shaped) * k + gap * (len(shaped) - 1)) if shaped else 0.0
    return glyphs, width


def measure(s: str, font: str, size: float, tracking: float = 0.0) -> float:
    return _layout(clean(s, font), font, size, tracking)[1]


def fit(s: str, font: str, size: float, max_width: float, tracking: float = 0.0) -> str:
    s = clean(s, font)
    if measure(s, font, size, tracking) <= max_width:
        return s
    lo, hi = 0, len(s)
    while lo < hi:  # longest prefix that fits with the ellipsis
        mid = (lo + hi + 1) // 2
        if measure(s[:mid].rstrip() + "…", font, size, tracking) <= max_width:
            lo = mid
        else:
            hi = mid - 1
    return s[:lo].rstrip() + "…"


def wrap(s: str, font: str, size: float, max_width: float) -> list[str]:
    lines, line = [], ""
    for word in clean(s, font).split():
        trial = f"{line} {word}".strip()
        if line and measure(trial, font, size) > max_width:
            lines.append(line)
            line = word
        else:
            line = trial
    return lines + [line] if line else lines


def _dotless(s: str, font: str) -> str:
    return s.replace("i", "ı") if 0x131 in _font(font)[4] else s


def text(x: float, y: float, s: str, font: str, size: float, fill: str, *, anchor: str = "start",
         tracking: float = 0.0, opacity: float | None = None, dotless: bool = False) -> str:
    """One <path> for the string, baseline at y. data-t carries the source text."""
    s = clean(s, font)
    drawn = _dotless(s, font) if dotless else s
    glyphs, width = _layout(drawn, font, size, tracking)
    x0 = x - {"start": 0.0, "middle": width / 2, "end": width}[anchor]
    _, _, glyphset, upem, _ = _font(font)
    k = size / upem
    pen = SVGPathPen(glyphset, ntos=_num)
    for name, gx, gy in glyphs:
        glyphset[name].draw(TransformPen(pen, (k, 0, 0, -k, x0 + gx, y - gy)))
    extra = f' fill-opacity="{_num(opacity)}"' if opacity is not None else ""
    return f'<path data-t={quoteattr(s)} d="{pen.getCommands()}" fill="{fill}"{extra}/>'


@functools.cache
def _dot_box(font: str) -> tuple[float, float, float]:
    """The dot of the letter i in font units: (centre x, centre y, radius), y up."""
    _, _, glyphset, _, cmap = _font(font)
    rec = DecomposingRecordingPen(glyphset)
    glyphset[cmap[ord("i")]].draw(rec)
    contours, cur = [], []
    for op, args in rec.value:
        cur.append((op, args))
        if op in ("closePath", "endPath"):
            contours.append(cur)
            cur = []
    boxes = []
    for contour in contours:
        bp = BoundsPen(glyphset)
        for op, args in contour:
            getattr(bp, op)(*args)
        boxes.append(bp.bounds)
    x0, y0, x1, y1 = max(boxes, key=lambda b: b[1])  # the highest contour is the dot
    return ((x0 + x1) / 2, (y0 + y1) / 2, (x1 - x0) / 2)


def i_dots(s: str, font: str, size: float, tracking: float = 0.0) -> list[tuple[float, float, float]]:
    """For each i in s: its dot as (cx, cy, r) relative to the text origin (y negative = above baseline)."""
    s = clean(s, font)
    glyphs, _ = _layout(_dotless(s, font), font, size, tracking)
    k = size / _font(font)[3]
    cx, cy, r = _dot_box(font)
    return [(gx + cx * k, -cy * k, r * k) for ch, (_, gx, _) in zip(s, glyphs) if ch == "i"]
