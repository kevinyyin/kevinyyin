#!/usr/bin/env python3
"""Write preview/index.html: the cards on GitHub-like light and dark pages (local only, git-ignored)."""
import os
import re

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
ORDER = ("banner", "streak", "contributions")


def _column(theme: str, bg: str) -> str:
    def img(slug: str, style: str = "width:100%") -> str:
        path = os.path.join(ROOT, "profile", f"{slug}-{theme}.svg")
        return f'<img src="../profile/{slug}-{theme}.svg" style="{style};vertical-align:top">' if os.path.exists(path) else ""

    readme = os.path.join(ROOT, "README.md")
    body = open(readme).read() if os.path.exists(readme) else ""
    if "<picture>" in body:  # the real README markup, with this theme's images forced
        body = re.sub(r"<!--.*?-->", "", body, flags=re.S)
        body = re.sub(r"<source[^>]*>", "", body).replace("./profile/", "../profile/")
        if theme == "dark":
            body = body.replace("-light.svg", "-dark.svg")
        body = re.sub(r"\n\s*\n", "<p></p>", body.strip())
    else:  # before the README exists: whatever cards are in profile/
        row = img("banner-left", "width:49.074%") + img("banner-art", "width:50.926%")
        parts = [row] + [img(s) for s in ORDER]
        parts.append("".join(img(f"recent-{i}") for i in (1, 2, 3)))
        body = "".join(f"<p>{p}</p>" for p in parts if p)
    return f'<div style="background:{bg};padding:24px"><div style="width:846px;margin:0 auto;font-size:0">{body}</div></div>'


def main() -> None:
    os.makedirs(os.path.join(ROOT, "preview"), exist_ok=True)
    html = ('<!doctype html><meta charset="utf-8"><style>body{margin:0}p{margin:0 0 16px}img{max-width:100%}</style>'
            + _column("light", "#ffffff") + _column("dark", "#0d1117"))
    with open(os.path.join(ROOT, "preview", "index.html"), "w") as f:
        f.write(html)
    print("wrote preview/index.html")


if __name__ == "__main__":
    main()
