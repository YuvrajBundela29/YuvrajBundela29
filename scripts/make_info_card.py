#!/usr/bin/env python3
"""
make_info_card.py — Generate a neofetch-style animated SVG info card.
Customised for Yuvraj Singh Bundela (YuvrajBundela29).

Usage:
    python scripts/make_info_card.py          # animated
    STATIC=1 python scripts/make_info_card.py # frozen frame for preview
"""

import os
import pathlib

OUT_SVG  = pathlib.Path("info-card.svg")
STATIC   = os.getenv("STATIC", "0") == "1"

# ── Card Content ──────────────────────────────────────────────────────────────
TITLE    = "YuvrajBundela29@github"
OS_LINE  = "Jhansi, India  \u00b7  he/him"

ROWS = [
    # (key_color, key,          value_color, value)
    ("#39d353", "Name",        "#c0c0c0", "Yuvraj Singh Bundela"),
    ("#39d353", "Role",        "#c0c0c0", "CSE Student  \u00b7  Cyber Security & AI Enthusiast"),
    ("#39d353", "Education",   "#c0c0c0", "B.Tech @SRGI Jhansi  \u00b7  B.Sc.(Hons) AI @IITG"),
    ("#39d353", "Stack",       "#c0c0c0", "Python \u00b7 JS/TS \u00b7 React \u00b7 Node \u00b7 C/C++ \u00b7 Java"),
    ("#39d353", "Also",        "#c0c0c0", "ML / AI  \u00b7  Docker  \u00b7  DevOps"),
    ("#39d353", "Highlights",  "#c0c0c0", "OSS Contributor  \u00b7  Competitive Programmer"),
    ("#39d353", "Content",     "#c0c0c0", "Creator / Blogger  \u00b7  Freelance Developer"),
    ("#39d353", "LinkedIn",    "#58a6ff", "in/yuvraj-singh-bundela-2a5227262"),
]

# ── Layout ────────────────────────────────────────────────────────────────────
W         = 490
FONT      = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
FS_TITLE  = 12
FS_BODY   = 11
PAD_X     = 18
PAD_Y     = 20
LINE_H    = 22
BG        = "#0d1117"
BORDER    = "#30363d"
TITLE_COL = "#58a6ff"

STAGGER   = 0.12   # seconds between line reveals

def line_h_total() -> int:
    return PAD_Y * 2 + LINE_H * 2 + LINE_H * len(ROWS) + 25

def anim(i: int, delay_extra: float = 0.0) -> str:
    if STATIC:
        return ""
    t = i * STAGGER + delay_extra
    return (
        f' opacity="0">'
        f'<animate attributeName="opacity" from="0" to="1"'
        f' begin="{t:.2f}s" dur="0.25s" fill="freeze"/>'
        f'<animateTransform attributeName="transform" type="translate"'
        f' from="0 6" to="0 0"'
        f' begin="{t:.2f}s" dur="0.25s" fill="freeze"/>'
    )

def svg() -> str:
    h  = line_h_total()
    p: list[str] = []

    p.append(
        f'<svg xmlns="http://www.w3.org/2000/svg"'
        f' width="{W}" height="{h}"'
        f' viewBox="0 0 {W} {h}">\n'
    )
    # Background + border
    p.append(f'  <rect width="{W}" height="{h}" rx="8" fill="{BG}"/>\n')
    p.append(
        f'  <rect width="{W}" height="{h}" rx="8"'
        f' fill="none" stroke="{BORDER}" stroke-width="1"/>\n'
    )

    # ── Title bar ─────────────────────────────────────────────────────────────
    title_y = PAD_Y + FS_TITLE
    title_g_open = f'  <g transform="translate(0,0)"'
    if STATIC:
        p.append(
            f'  <text x="{PAD_X}" y="{title_y}"'
            f' font-family="{FONT}" font-size="{FS_TITLE}"'
            f' fill="{TITLE_COL}" font-weight="bold">{TITLE}</text>\n'
        )
    else:
        p.append(
            f'  <g opacity="0">'
            f'<animate attributeName="opacity" from="0" to="1"'
            f' begin="0s" dur="0.3s" fill="freeze"/>'
            f'<animateTransform attributeName="transform" type="translate"'
            f' from="0 8" to="0 0" begin="0s" dur="0.3s" fill="freeze"/>\n'
            f'  <text x="{PAD_X}" y="{title_y}"'
            f' font-family="{FONT}" font-size="{FS_TITLE}"'
            f' fill="{TITLE_COL}" font-weight="bold">{TITLE}</text>\n'
            f'  </g>\n'
        )

    # Separator line
    sep_y  = title_y + 8
    if STATIC:
        p.append(f'  <line x1="{PAD_X}" y1="{sep_y}" x2="{W - PAD_X}" y2="{sep_y}" stroke="{BORDER}" stroke-width="1"/>\n')
    else:
        p.append(
            f'  <line x1="{PAD_X}" y1="{sep_y}" x2="{W - PAD_X}" y2="{sep_y}"'
            f' stroke="{BORDER}" stroke-width="1" opacity="0">'
            f'<animate attributeName="opacity" from="0" to="1"'
            f' begin="0.25s" dur="0.1s" fill="freeze"/></line>\n'
        )

    # OS line (github url)
    os_y = sep_y + LINE_H
    if STATIC:
        p.append(
            f'  <text x="{PAD_X}" y="{os_y}"'
            f' font-family="{FONT}" font-size="{FS_BODY}"'
            f' fill="#8b949e">{OS_LINE}</text>\n'
        )
    else:
        p.append(
            f'  <g opacity="0">'
            f'<animate attributeName="opacity" from="0" to="1"'
            f' begin="0.3s" dur="0.2s" fill="freeze"/>'
            f'<animateTransform attributeName="transform" type="translate"'
            f' from="0 5" to="0 0" begin="0.3s" dur="0.2s" fill="freeze"/>\n'
            f'  <text x="{PAD_X}" y="{os_y}"'
            f' font-family="{FONT}" font-size="{FS_BODY}"'
            f' fill="#8b949e">{OS_LINE}</text>\n'
            f'  </g>\n'
        )

    # ── Data rows ─────────────────────────────────────────────────────────────
    row_start_y = os_y + LINE_H + 4
    for i, (kc, key, vc, val) in enumerate(ROWS):
        y = row_start_y + i * LINE_H
        delay = 0.45 + i * STAGGER
        key_x = PAD_X
        sep_x = key_x + 90
        val_x = sep_x + 12

        # Escape special XML chars in key and val
        es_key = key.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        es_val = val.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

        if STATIC:
            p.append(
                f'  <text x="{key_x}" y="{y}" font-family="{FONT}"'
                f' font-size="{FS_BODY}" fill="{kc}">{es_key}</text>\n'
                f'  <text x="{sep_x}" y="{y}" font-family="{FONT}"'
                f' font-size="{FS_BODY}" fill="#8b949e">│</text>\n'
                f'  <text x="{val_x}" y="{y}" font-family="{FONT}"'
                f' font-size="{FS_BODY}" fill="{vc}">{es_val}</text>\n'
            )
        else:
            p.append(
                f'  <g opacity="0">'
                f'<animate attributeName="opacity" from="0" to="1"'
                f' begin="{delay:.2f}s" dur="0.25s" fill="freeze"/>'
                f'<animateTransform attributeName="transform" type="translate"'
                f' from="0 5" to="0 0"'
                f' begin="{delay:.2f}s" dur="0.25s" fill="freeze"/>\n'
                f'  <text x="{key_x}" y="{y}" font-family="{FONT}"'
                f' font-size="{FS_BODY}" fill="{kc}">{es_key}</text>\n'
                f'  <text x="{sep_x}" y="{y}" font-family="{FONT}"'
                f' font-size="{FS_BODY}" fill="#8b949e">│</text>\n'
                f'  <text x="{val_x}" y="{y}" font-family="{FONT}"'
                f' font-size="{FS_BODY}" fill="{vc}">{es_val}</text>\n'
                f'  </g>\n'
            )

    # ── Color dots ────────────────────────────────────────────────────────────
    dot_y  = row_start_y + len(ROWS) * LINE_H + 6
    colors = ["#ff7b72", "#ffa657", "#e3b341", "#3fb950", "#58a6ff", "#bc8cff", "#ff7b72", "#ffa657"]
    dot_r  = 5
    dot_gap = 14
    if STATIC:
        for ci, color in enumerate(colors):
            cx = PAD_X + dot_r + ci * dot_gap
            p.append(f'  <circle cx="{cx}" cy="{dot_y}" r="{dot_r}" fill="{color}"/>\n')
    else:
        delay_d = 0.45 + len(ROWS) * STAGGER
        p.append(
            f'  <g opacity="0">'
            f'<animate attributeName="opacity" from="0" to="1"'
            f' begin="{delay_d:.2f}s" dur="0.3s" fill="freeze"/>\n'
        )
        for ci, color in enumerate(colors):
            cx = PAD_X + dot_r + ci * dot_gap
            p.append(f'  <circle cx="{cx}" cy="{dot_y}" r="{dot_r}" fill="{color}"/>\n')
        p.append("  </g>\n")

    p.append("</svg>\n")
    return "".join(p)


def main() -> None:
    out = svg()
    OUT_SVG.write_text(out, encoding="utf-8")
    mode = "static" if STATIC else "animated"
    print(f"[make_info_card] Done ({mode}) -> {OUT_SVG}")

if __name__ == "__main__":
    main()
