#!/usr/bin/env python3
"""
fetch_contributions.py — Scrape real GitHub contribution data (no token needed).

Usage:
    python scripts/fetch_contributions.py
    python scripts/fetch_contributions.py --username someone-else

GitHub serves the contribution calendar as public HTML at:
    https://github.com/users/<username>/contributions

This parses the day cells with BeautifulSoup and writes:
    data/contributions.json

The JSON includes raw days plus derived stats (current streak, longest
streak, best day, total count).
"""

import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

USERNAME = "mrparasssingh"
OUTPUT = "data/contributions.json"


def fetch_contribution_html(username: str) -> str:
    """Fetch the public contribution calendar fragment."""
    url = f"https://github.com/users/{username}/contributions"
    resp = requests.get(url, timeout=30, headers={
        "User-Agent": "Mozilla/5.0 (profile-readme-generator)"
    })
    resp.raise_for_status()
    return resp.text


def parse_contributions(html: str) -> list[dict]:
    """
    Parse contribution day cells from the HTML.

    Each <td> has:
      - data-date="YYYY-MM-DD"
      - data-level="0"–"4"  (contribution intensity)
      - A <tool-tip> child with text like "5 contributions on March 14th."
    """
    soup = BeautifulSoup(html, "html.parser")
    days = []

    for td in soup.find_all("td", class_="ContributionCalendar-day"):
        date_str = td.get("data-date")
        level = int(td.get("data-level", 0))

        if not date_str:
            continue

        # Extract contribution count from the tooltip text
        count = 0
        tooltip = td.find_next("tool-tip")
        if tooltip:
            text = tooltip.get_text(strip=True)
            # "5 contributions on March 14th." or "No contributions on..."
            if text.startswith("No "):
                count = 0
            else:
                try:
                    count = int(text.split()[0])
                except (ValueError, IndexError):
                    count = 0

        days.append({
            "date": date_str,
            "count": count,
            "level": level,
        })

    # Sort by date
    days.sort(key=lambda d: d["date"])
    return days


def compute_stats(days: list[dict]) -> dict:
    """Derive streak and aggregate stats from day-level data."""
    total = sum(d["count"] for d in days)

    # Best single day
    best_day = max(days, key=lambda d: d["count"]) if days else None

    # Current streak (consecutive days ending at most recent day with count > 0)
    current_streak = 0
    for d in reversed(days):
        if d["count"] > 0:
            current_streak += 1
        else:
            # Allow today to be zero if it's the current date
            if d == days[-1]:
                continue
            break

    # Longest streak
    longest_streak = 0
    streak = 0
    for d in days:
        if d["count"] > 0:
            streak += 1
            longest_streak = max(longest_streak, streak)
        else:
            streak = 0

    # Monthly totals
    monthly = {}
    for d in days:
        month = d["date"][:7]  # "YYYY-MM"
        monthly[month] = monthly.get(month, 0) + d["count"]

    return {
        "total_contributions": total,
        "total_days": len(days),
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "best_day": best_day,
        "monthly_totals": monthly,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Fetch GitHub contributions (no token needed)"
    )
    parser.add_argument(
        "--username", "-u",
        default=USERNAME,
        help=f"GitHub username (default: {USERNAME})"
    )
    parser.add_argument(
        "--output", "-o",
        default=OUTPUT,
        help=f"Output JSON path (default: {OUTPUT})"
    )
    args = parser.parse_args()

    print(f"Fetching contributions for {args.username}...")
    html = fetch_contribution_html(args.username)

    days = parse_contributions(html)
    stats = compute_stats(days)

    result = {
        "username": args.username,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "stats": stats,
        "days": days,
    }

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    print(f"[OK] {stats['total_contributions']} contributions across "
          f"{stats['total_days']} days")
    print(f"  Current streak: {stats['current_streak']} days")
    print(f"  Longest streak: {stats['longest_streak']} days")
    if stats["best_day"]:
        print(f"  Best day: {stats['best_day']['date']} "
              f"({stats['best_day']['count']} contributions)")
    print(f"  -> {args.output}")


if __name__ == "__main__":
    main()
