#!/usr/bin/env python3
"""Turn a self-contained guide page (as exported from Claude) into a fast static page.

The exported pages carry every photo as base64 inside <script>PHS.add({...})</script>
tags, which makes them 7-11 MB. This script writes each photo to its own .webp file,
replaces those tags with one small id -> file map, and points the page's photo loader
at the files. Photos then download only when they scroll into view, and the browser
can cache them.

Usage:
    python3 tools/import_guide.py <exported.html> <slug>

Example:
    python3 tools/import_guide.py ~/Downloads/hanoi.html hanoi
    -> writes guides/hanoi/index.html and guides/hanoi/photos/*.webp
"""
import base64
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Links between guides inside the exported pages point at claude.ai.
# On the site they should switch tabs instead.
CROSS_LINKS = {
    "https://claude.ai/artifact/SYbu1wSyRyesXSDkcFVpHc": "hanoi",
    "https://claude.ai/artifact/JdU52F9sGaD1J5vBCC6GQv": "danang",
}

ADD_RE = re.compile(r"<script>PHS\.add\((\{.*?\})\)</script>", re.S)
DATA_URI = '"data:image/webp;base64,"+b'


def main(src: str, slug: str) -> None:
    html = Path(src).read_text(encoding="utf-8")
    out_dir = ROOT / "guides" / slug
    photos = out_dir / "photos"
    if photos.exists():
        shutil.rmtree(photos)
    photos.mkdir(parents=True)

    mapping = {}
    for m in ADD_RE.finditer(html):
        for pid, b64 in json.loads(m.group(1)).items():
            if not re.fullmatch(r"[0-9a-f]+", pid):
                sys.exit(f"unexpected photo id {pid!r}")
            (photos / f"{pid}.webp").write_bytes(base64.b64decode(b64))
            mapping[pid] = f"photos/{pid}.webp"
    if not mapping:
        sys.exit("no PHS.add photo blocks found; has the page format changed?")

    # Swap the first photo block for the file map and drop the rest.
    first = True

    def swap(_):
        nonlocal first
        if first:
            first = False
            return "<script>PHS.add(" + json.dumps(mapping, separators=(",", ":")) + ")</script>"
        return ""

    html = ADD_RE.sub(swap, html)
    html = re.sub(r"\n{2,}(<script>PHS\.done\(\)</script>)", r"\n\1", html)

    # The loader built data: URIs from the base64; now each value is already a URL.
    n = html.count(DATA_URI)
    if n != 2:
        sys.exit(f"expected 2 data-URI builders in the photo loader, found {n}")
    html = html.replace(DATA_URI, "b")

    for url, target in CROSS_LINKS.items():
        html = html.replace(f'href="{url}"', f'href="../../#{target}" target="_top"')
    if "claude.ai/artifact/" in html:
        sys.exit("an unmapped claude.ai link is left in the page; add it to CROSS_LINKS")

    (out_dir / "index.html").write_text(html, encoding="utf-8")
    size = sum(p.stat().st_size for p in photos.iterdir())
    print(f"{slug}: page {len(html.encode()) // 1024} KB, {len(mapping)} photos, {size // 1024} KB of photos")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
