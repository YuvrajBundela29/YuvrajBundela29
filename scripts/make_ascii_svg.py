#!/usr/bin/env python3
"""
make_ascii_svg.py — Convert source-prepped.png → yuvraj-ascii.svg
A self-typing monochrome ASCII portrait with SMIL row-wipe animation.

Usage:
    python scripts/make_ascii_svg.py
"""

import pathlib
import numpy as np
from PIL import Image

# ── Config ────────────────────────────────────────────────────────────────────
SRC_PNG    = pathlib.Path("source-prepped.png")
OUT_SVG    = pathlib.Path("yuvraj-ascii.svg")

COLS       = 100          # character columns
ASPECT     = 0.50         # char h/w ratio for typical monospace font
RAMP       = " .`:-=+*cs#%@"   # bright (sparse) → dark (dense)
FONT_SIZE  = 7            # px — tune for desired portrait size
CHAR_W     = FONT_SIZE * 0.60
CHAR_H     = FONT_SIZE
FILL_COLOR = "#c0c0c0"    # monochrome light-grey
BG_COLOR   = "#0d1117"    # GitHub dark background

# Animation timing
ROW_DUR    = 0.06         # seconds per row reveal
CURSOR_W   = CHAR_W * 1.2

def image_to_ascii(img_path: pathlib.Path, cols: int) -> list[str]:
    img  = Image.open(img_path).convert("L")
    w, h = img.size
    rows = int(cols * (h / w) * ASPECT)
    img  = img.resize((cols, rows), Image.LANCZOS)
    arr  = np.array(img)
    n    = len(RAMP) - 1
    lines = []
    for row in arr:
        line = "".join(RAMP[int(p / 255 * n)] for p in row)
        lines.append(line)
    return lines

def escape(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def build_svg(lines: list[str]) -> str:
    n_rows   = len(lines)
    n_cols   = max(len(l) for l in lines)
    svg_w    = n_cols * CHAR_W
    svg_h    = n_rows * CHAR_H

    total_dur = n_rows * ROW_DUR + 1.0   # +1 s settling time
    parts: list[str] = []

    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg"'
        f' width="{svg_w:.1f}" height="{svg_h:.1f}"'
        f' viewBox="0 0 {svg_w:.1f} {svg_h:.1f}">\n'
    )
    parts.append(f'  <rect width="100%" height="100%" fill="{BG_COLOR}"/>\n')

    # One <clipPath> + <g> per row —————————————————————————————————————————
    parts.append("  <defs>\n")
    for i in range(n_rows):
        y0 = i * CHAR_H
        parts.append(
            f'    <clipPath id="cr{i}">'
            f'<rect x="0" y="{y0:.1f}" width="0" height="{CHAR_H:.1f}">'
            f'<animate attributeName="width" from="0" to="{svg_w:.1f}"'
            f' begin="{i * ROW_DUR:.3f}s" dur="{ROW_DUR * 0.85:.3f}s"'
            f' fill="freeze"/>'
            f'</rect></clipPath>\n'
        )
    parts.append("  </defs>\n")

    # Text rows ————————————————————————————————————————————————————————————
    for i, line in enumerate(lines):
        y   = (i + 1) * CHAR_H - 1
        t0  = i * ROW_DUR
        t_cursor_end = t0 + ROW_DUR * 0.85

        parts.append(f'  <g clip-path="url(#cr{i})">\n')
        parts.append(
            f'    <text x="0" y="{y:.1f}"'
            f' font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"'
            f' font-size="{FONT_SIZE}" fill="{FILL_COLOR}"'
            f' xml:space="preserve">{escape(line)}</text>\n'
        )
        # Cursor rect that rides the wipe edge
        parts.append(
            f'    <rect y="{i * CHAR_H:.1f}" height="{CHAR_H:.1f}" width="{CURSOR_W:.1f}"'
            f' fill="{FILL_COLOR}" opacity="0.7">\n'
            f'      <animate attributeName="x"'
            f' from="0" to="{svg_w:.1f}"'
            f' begin="{t0:.3f}s" dur="{ROW_DUR * 0.85:.3f}s"'
            f' fill="freeze"/>\n'
            f'      <animate attributeName="opacity"'
            f' from="0.7" to="0"'
            f' begin="{t_cursor_end:.3f}s" dur="0.05s"'
            f' fill="freeze"/>\n'
            f'    </rect>\n'
        )
        parts.append("  </g>\n")

    parts.append("</svg>\n")
    return "".join(parts)


def main() -> None:
    if not SRC_PNG.exists():
        raise FileNotFoundError(f"{SRC_PNG} not found — run prep_photo.py first.")
    print("[make_ascii_svg] Converting image to ASCII…")
    lines = image_to_ascii(SRC_PNG, COLS)
    print(f"[make_ascii_svg] Grid: {COLS} cols × {len(lines)} rows")
    svg   = build_svg(lines)
    OUT_SVG.write_text(svg, encoding="utf-8")
    print(f"[make_ascii_svg] Done → {OUT_SVG}")

if __name__ == "__main__":
    main()
