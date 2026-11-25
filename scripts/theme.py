"""The two palettes and the layout constants every card shares."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Theme:
    name: str
    paper: str
    ink: str
    muted: str
    line_opacity: float  # hairlines are ink at this opacity
    accent: str


LIGHT = Theme("light", "#F3F1EB", "#141311", "#8B877F", 0.13, "#3B4B9A")
DARK = Theme("dark", "#111110", "#F2F0EA", "#807C75", 0.15, "#8C98E8")
THEMES = (LIGHT, DARK)

W = 648  # card width in SVG units; the mockups' card width
RADIUS = 18
PAD_X = 28
PAD_Y = 24
