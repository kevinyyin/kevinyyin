"""Small SVG helpers shared by the cards."""
import textpath as tp
from theme import RADIUS, W, Theme

REDUCED_MOTION = "@media (prefers-reduced-motion:reduce){*{animation:none!important}.fx{display:none}}"


def n(v: float) -> str:
    return f"{v:.2f}".rstrip("0").rstrip(".")


def doc(height: float, body: str, css: str = "", width: float = W) -> str:
    if "animation" in css:
        css += REDUCED_MOTION
    style = f"<style>{css}</style>" if css else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {n(width)} {n(height)}" '
            f'width="{n(width)}" height="{n(height)}" role="img">{style}{body}</svg>')


def panel_path(width: float, height: float, corners: str = "all", r: float = RADIUS) -> str:
    """Outline of a card; corners is all, left, right, top, bottom or none."""
    tl = tr = br = bl = 0.0
    if corners in ("all", "left", "top"):
        tl = r
    if corners in ("all", "right", "top"):
        tr = r
    if corners in ("all", "right", "bottom"):
        br = r
    if corners in ("all", "left", "bottom"):
        bl = r
    w, h = width, height
    return (f"M{n(tl)} 0H{n(w - tr)}A{n(tr)} {n(tr)} 0 0 1 {n(w)} {n(tr)}V{n(h - br)}"
            f"A{n(br)} {n(br)} 0 0 1 {n(w - br)} {n(h)}H{n(bl)}A{n(bl)} {n(bl)} 0 0 1 0 {n(h - bl)}"
            f"V{n(tl)}A{n(tl)} {n(tl)} 0 0 1 {n(tl)} 0Z")


def panel(width: float, height: float, theme: Theme, corners: str = "all") -> str:
    return f'<path d="{panel_path(width, height, corners)}" fill="{theme.paper}"/>'


def label(x: float, y: float, s: str, theme: Theme, fill: str | None = None, anchor: str = "start") -> str:
    return tp.text(x, y, s.upper(), "text-400", 11, fill or theme.muted, anchor=anchor, tracking=0.09)


def hairline(x1: float, y1: float, x2: float, y2: float, theme: Theme) -> str:
    return (f'<line x1="{n(x1)}" y1="{n(y1)}" x2="{n(x2)}" y2="{n(y2)}" stroke="{theme.ink}" '
            f'stroke-opacity="{theme.line_opacity}" stroke-width="1"/>')


def outline(x: float, y: float, w: float, h: float, r: float, theme: Theme) -> str:
    return (f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" rx="{n(r)}" fill="none" '
            f'stroke="{theme.ink}" stroke-opacity="{theme.line_opacity}" stroke-width="1"/>')


def value_size(s: str, font: str, size: float, max_width: float, tracking: float = 0.0) -> float:
    """size, shrunk just enough that s fits max_width."""
    w = tp.measure(s, font, size, tracking)
    return size if w <= max_width else size * max_width / w
