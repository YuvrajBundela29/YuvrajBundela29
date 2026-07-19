#!/usr/bin/env python3
"""
fetch_contributions.py — Scrape the public GitHub contribution calendar
for YuvrajBundela29 (no token required) and write data/contributions.json.

Usage:
    python scripts/fetch_contributions.py
"""

import json
import pathlib
import datetime
import sys

import requests
from bs4 import BeautifulSoup

USERNAME  = "YuvrajBundela29"
OUT_JSON  = pathlib.Path("data/contributions.json")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


def fetch_days() -> list[dict]:
    url = f"https://github.com/users/{USERNAME}/contributions"
    print(f"[fetch] GET {url}")
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    days: list[dict] = []
    for td in soup.select("td.ContributionCalendar-day"):
        date_str = td.get("data-date", "")
        if not date_str:
            continue
        # GitHub stores the count either in data-level or in a tooltip
        level = int(td.get("data-level", "0"))
        # Try to get the actual count from the title/tooltip span
        tooltip = td.find("tool-tip") or td.find("span", {"data-date": True})
        count = 0
        if tooltip:
            import re
            m = re.search(r"(\d+)\s+contribution", tooltip.get_text())
            if m:
                count = int(m.group(1))
        else:
            # fall back to a rough mapping from level
            count = [0, 1, 3, 6, 9, 15][min(level, 5)]
        days.append({"date": date_str, "count": count, "level": level})

    days.sort(key=lambda d: d["date"])
    return days


def compute_stats(days: list[dict]) -> dict:
    total  = sum(d["count"] for d in days)
    best   = max(days, key=lambda d: d["count"], default={"date": "", "count": 0})

    # Streaks
    cur_streak = longest = cur = 0
    for d in reversed(days):
        if d["count"] > 0:
            cur += 1
            longest = max(longest, cur)
        else:
            if cur_streak == 0:
                cur_streak = cur   # first break from today backwards
            cur = 0
    if cur_streak == 0:
        cur_streak = cur

    # Monthly totals
    monthly: dict[str, int] = {}
    for d in days:
        ym = d["date"][:7]
        monthly[ym] = monthly.get(ym, 0) + d["count"]

    return {
        "total":          total,
        "best_day":       best,
        "current_streak": cur_streak,
        "longest_streak": longest,
        "monthly":        monthly,
        "fetched_at":     datetime.datetime.utcnow().isoformat() + "Z",
    }


def main() -> None:
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    days  = fetch_days()
    if not days:
        print("[fetch] ERROR: no days found — HTML structure may have changed.", file=sys.stderr)
        sys.exit(1)
    stats = compute_stats(days)
    payload = {"days": days, "stats": stats}
    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(
        f"[fetch] {len(days)} days  |  "
        f"{stats['total']} total  |  "
        f"streak {stats['current_streak']}d  →  {OUT_JSON}"
    )


if __name__ == "__main__":
    main()
