"""Rules every generated card must obey (see the plan's Global Constraints)."""
import re
import xml.etree.ElementTree as ET


def check(svg: str) -> ET.Element:
    root = ET.fromstring(svg)  # must be well-formed XML
    tags = {el.tag.split("}")[-1] for el in root.iter()}
    assert "script" not in tags, "no scripts in cards"
    assert "text" not in tags, "text must be outlines"
    for ref in re.findall(r'href="([^"]*)"', svg) + re.findall(r"url\(([^)]*)\)", svg):
        assert "http" not in ref, f"external reference: {ref[:60]}"
    if "animation" in svg:
        assert "prefers-reduced-motion" in svg
    return root
