#!/usr/bin/env python3
"""
render_heatmap_svg.py — Read data/contributions.json and render
contrib-heatmap.svg: a 53-week × 7-day calendar of rounded boxes
that slide in diagonally (CSS keyframe, plays once, then freezes).

Usage:
    python scripts/render_heatmap_svg.py
"""

import json
import pathlib
import datetime

IN_JSON  = pathlib.Path("data/contributions.json")
OUT_SVG  = pathlib.Path("contrib-heatmap.svg")

# ── Visual config ────────────────────────────────────────────────────────────
CELL      = 11          # px per cell
GAP       = 3           # px gap between cells
RADIUS    = 2           # corner radius
PAD_TOP   = 28          # space for month labels
PAD_LEFT  = 30          # space for day-of-week labels
PAD_BOT   = 54          # space for legend + stats footer
PAD_RIGHT = 20

PALETTE   = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]
#             none        level1     level2     level3     level4     level5 (neon top)

BG        = "#0d1117"
TEXT_COL  = "#8b949e"
FONT      = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
FS        = 9

STEP      = CELL + GAP
DAYS      = ["Mon", "", "Wed", "", "Fri", "", ""]
MONTHS    = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]


def load_data() -> tuple[dict[str, dict], dict]:
    data  = json.loads(IN_JSON.read_text(encoding="utf-8"))
    days  = {d["date"]: d for d in data["days"]}
    stats = data["stats"]
    return days, stats


def build_weeks(days_map: dict[str, dict]) -> list[list[dict | None]]:
    """Build a list of 53 columns, each 7 rows (Mon→Sun)."""
    today = datetime.date.today()
    # Start from 371 days ago, aligned to Monday
    start = today - datetime.timedelta(days=371)
    start -= datetime.timedelta(days=start.weekday())  # back to Monday

    weeks: list[list[dict | None]] = []
    cur = start
    while cur <= today:
        week = []
        for _ in range(7):
            if cur <= today:
                ds   = cur.isoformat()
                week.append(days_map.get(ds, {"date": ds, "count": 0, "level": 0}))
            else:
                week.append(None)
            cur += datetime.timedelta(days=1)
        weeks.append(week)
    # Keep at most 53 weeks
    return weeks[-53:]


def diagonal_delay(col: int, row: int) -> float:
    """Stagger reveal by anti-diagonal so boxes cascade down-right."""
    return (col + row) * 0.012   # seconds


def svg_cell(x: float, y: float, cell: dict, col: int, row: int) -> str:
    level = min(cell.get("level", 0), 5)
    color = PALETTE[level]
    delay = diagonal_delay(col, row)
    return (
        f'<rect x="{x:.1f}" y="{y:.1f}" width="{CELL}" height="{CELL}"'
        f' rx="{RADIUS}" ry="{RADIUS}" fill="{color}"'
        f' style="opacity:0;animation:reveal 0.3s {delay:.3f}s forwards">'
        f'<title>{cell["date"]}: {cell["count"]} contribution'
        f'{"s" if cell["count"] != 1 else ""}</title>'
        f'</rect>\n'
    )


def main() -> None:
    if not IN_JSON.exists():
        raise FileNotFoundError(f"{IN_JSON} not found — run fetch_contributions.py first.")

    days_map, stats = load_data()
    weeks            = build_weeks(days_map)

    n_weeks = len(weeks)
    canvas_w = PAD_LEFT + n_weeks * STEP + PAD_RIGHT
    canvas_h = PAD_TOP + 7 * STEP + PAD_BOT

    parts: list[str] = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg"'
        f' width="{canvas_w}" height="{canvas_h}"'
        f' viewBox="0 0 {canvas_w} {canvas_h}">\n'
    )
    parts.append(f'  <rect width="{canvas_w}" height="{canvas_h}" rx="8" fill="{BG}"/>\n')

    # ── CSS animation (plays once, freezes) ───────────────────────────────────
    parts.append(
        "  <style>\n"
        "    @keyframes reveal {\n"
        "      from { opacity: 0; transform: translateY(-4px); }\n"
        "      to   { opacity: 1; transform: translateY(0); }\n"
        "    }\n"
        "  </style>\n"
    )

    # ── Month labels ──────────────────────────────────────────────────────────
    last_month = -1
    for ci, week in enumerate(weeks):
        first_day = next((d for d in week if d is not None), None)
        if first_day is None:
            continue
        m = int(first_day["date"][5:7])
        if m != last_month:
            x = PAD_LEFT + ci * STEP
            parts.append(
                f'  <text x="{x}" y="{PAD_TOP - 6}"'
                f' font-family="{FONT}" font-size="{FS}" fill="{TEXT_COL}">'
                f'{MONTHS[m - 1]}</text>\n'
            )
            last_month = m

    # ── Day-of-week labels ────────────────────────────────────────────────────
    for ri, label in enumerate(DAYS):
        if label:
            y = PAD_TOP + ri * STEP + CELL - 1
            parts.append(
                f'  <text x="{PAD_LEFT - 4}" y="{y}"'
                f' font-family="{FONT}" font-size="{FS}"'
                f' fill="{TEXT_COL}" text-anchor="end">{label}</text>\n'
            )

    # ── Cells ─────────────────────────────────────────────────────────────────
    for ci, week in enumerate(weeks):
        for ri, cell in enumerate(week):
            if cell is None:
                continue
            x = PAD_LEFT + ci * STEP
            y = PAD_TOP  + ri * STEP
            parts.append("  " + svg_cell(x, y, cell, ci, ri))

    # ── Legend ────────────────────────────────────────────────────────────────
    grid_bot = PAD_TOP + 7 * STEP
    leg_y    = grid_bot + 14
    leg_x    = canvas_w - PAD_RIGHT - 6 * (CELL + 3)
    parts.append(
        f'  <text x="{leg_x - 6}" y="{leg_y + CELL - 1}"'
        f' font-family="{FONT}" font-size="{FS}" fill="{TEXT_COL}" text-anchor="end">Less</text>\n'
    )
    for li, col in enumerate(PALETTE):
        lx = leg_x + li * (CELL + 3)
        parts.append(
            f'  <rect x="{lx}" y="{leg_y}" width="{CELL}" height="{CELL}"'
            f' rx="{RADIUS}" ry="{RADIUS}" fill="{col}"/>\n'
        )
    parts.append(
        f'  <text x="{leg_x + 6 * (CELL + 3)}" y="{leg_y + CELL - 1}"'
        f' font-family="{FONT}" font-size="{FS}" fill="{TEXT_COL}">More</text>\n'
    )

    # ── Stats footer ──────────────────────────────────────────────────────────
    st        = stats
    total     = st.get("total", 0)
    cur_str   = st.get("current_streak", 0)
    lon_str   = st.get("longest_streak", 0)
    best      = st.get("best_day", {})
    best_txt  = f'{best.get("count", 0)} on {best.get("date", "")}'

    stat_y    = leg_y + CELL + 18
    parts.append(
        f'  <text x="{PAD_LEFT}" y="{stat_y}"'
        f' font-family="{FONT}" font-size="{FS}" fill="{TEXT_COL}">'
        f'{total:,} contributions in the last year'
        f'  ·  streak {cur_str}d  ·  best {best_txt}'
        f'</text>\n'
    )

    parts.append("</svg>\n")

    OUT_SVG.write_text("".join(parts), encoding="utf-8")
    print(f"[render_heatmap] Done → {OUT_SVG}  ({total:,} contributions)")


if __name__ == "__main__":
    main()
