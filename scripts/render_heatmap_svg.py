#!/usr/bin/env python3
"""
render_heatmap_svg.py — Render contribution data as an animated SVG heatmap.

Usage:
    python scripts/render_heatmap_svg.py                      # defaults
    python scripts/render_heatmap_svg.py --input data/contributions.json

Output: contrib-heatmap.svg

The classic 53-week × 7-day calendar of rounded, colored boxes using a
GitHub-ish green ramp. Revealed once with a diagonal, line-after-line
slide-down (CSS keyframes that play on load, then freeze — no looping).

Includes a Less→More legend and a stats footer.
"""

import argparse
import json
from datetime import datetime, timedelta
from pathlib import Path

# ── Color palette: GitHub-ish green ramp ────────────────────────────
# Level 0 = no contributions, level 5 = neon top end
PALETTE = [
    "#161b22",  # 0 — none
    "#0e4429",  # 1 — low
    "#006d32",  # 2
    "#26a641",  # 3
    "#39d353",  # 4 — high
    "#69f0a0",  # 5 — neon top (for outlier days)
]

# Layout constants
CELL_SIZE = 13     # px per day box
CELL_GAP = 3       # px between boxes
CELL_RADIUS = 2    # corner radius
WEEKS = 53
DAYS = 7
PADDING_LEFT = 40  # space for day labels
PADDING_TOP = 30   # space for month labels
PADDING_RIGHT = 20
PADDING_BOTTOM = 60  # space for legend and stats

BG_COLOR = "#0d1117"
TEXT_COLOR = "#8b949e"
LABEL_COLOR = "#c9d1d9"
FONT_SIZE = 10
STATS_FONT_SIZE = 12

# Animation
ANIM_DURATION = 0.08   # seconds per column reveal
ANIM_STAGGER = 0.02    # seconds between column starts

DAY_LABELS = ["", "Mon", "", "Wed", "", "Fri", ""]
MONTH_LABELS = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
]


def load_data(path: str) -> dict:
    """Load contribution JSON."""
    return json.loads(Path(path).read_text(encoding="utf-8"))


def build_week_grid(days: list[dict]) -> list[list[dict | None]]:
    """
    Arrange days into a 53×7 grid (weeks × days).
    Each cell is either a day dict or None (empty).
    """
    if not days:
        return [[None] * DAYS for _ in range(WEEKS)]

    # Find the start date and its weekday
    first_date = datetime.strptime(days[0]["date"], "%Y-%m-%d")
    start_dow = first_date.weekday()  # 0=Mon, 6=Sun
    # GitHub calendar starts on Sunday, so adjust
    # Python: 0=Mon..6=Sun → GitHub: 0=Sun..6=Sat
    git_dow = (start_dow + 1) % 7

    # Build lookup
    day_map = {d["date"]: d for d in days}

    grid = [[None] * DAYS for _ in range(WEEKS)]

    # Fill the grid week by week
    current = first_date
    week = 0
    dow = git_dow

    for d in days:
        date = datetime.strptime(d["date"], "%Y-%m-%d")
        # Calculate grid position
        delta = (date - first_date).days
        col = (delta + git_dow) // 7
        row = (delta + git_dow) % 7

        if col < WEEKS:
            grid[col][row] = d

    return grid


def get_month_markers(days: list[dict]) -> list[tuple[int, str]]:
    """Return (week_index, month_label) for each month boundary."""
    if not days:
        return []

    first_date = datetime.strptime(days[0]["date"], "%Y-%m-%d")
    start_dow = (first_date.weekday() + 1) % 7  # GitHub Sunday=0

    markers = []
    last_month = None

    for d in days:
        date = datetime.strptime(d["date"], "%Y-%m-%d")
        month = date.month
        if month != last_month:
            delta = (date - first_date).days
            week_idx = (delta + start_dow) // 7
            if week_idx < WEEKS:
                markers.append((week_idx, MONTH_LABELS[month - 1]))
            last_month = month

    return markers


def map_level(level: int) -> str:
    """Map a contribution level (0–4) to a palette color."""
    return PALETTE[min(level, len(PALETTE) - 1)]


def build_heatmap_svg(data: dict) -> str:
    """Build the animated contribution heatmap SVG."""
    days = data.get("days", [])
    stats = data.get("stats", {})
    username = data.get("username", "user")

    grid = build_week_grid(days)
    month_markers = get_month_markers(days)

    svg_w = PADDING_LEFT + WEEKS * (CELL_SIZE + CELL_GAP) + PADDING_RIGHT
    svg_h = PADDING_TOP + DAYS * (CELL_SIZE + CELL_GAP) + PADDING_BOTTOM

    parts = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {svg_w} {svg_h}" '
        f'width="{svg_w}" height="{svg_h}" '
        f'style="background:{BG_COLOR}">'
    )

    # CSS for animation
    anim_rules = ""
    for w in range(WEEKS):
        delay = w * ANIM_STAGGER
        anim_rules += f"""
    .week-{w} {{
      animation: slideReveal {ANIM_DURATION}s ease-out {delay:.3f}s both;
    }}"""

    parts.append(f"""<style>
    @keyframes slideReveal {{
      from {{
        opacity: 0;
        transform: translateY(-8px);
      }}
      to {{
        opacity: 1;
        transform: translateY(0);
      }}
    }}
    .day-label {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica,
                   Arial, sans-serif;
      font-size: {FONT_SIZE}px;
      fill: {TEXT_COLOR};
    }}
    .month-label {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica,
                   Arial, sans-serif;
      font-size: {FONT_SIZE}px;
      fill: {TEXT_COLOR};
    }}
    .stats-text {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica,
                   Arial, sans-serif;
      font-size: {STATS_FONT_SIZE}px;
      fill: {LABEL_COLOR};
    }}
    .legend-label {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica,
                   Arial, sans-serif;
      font-size: {FONT_SIZE}px;
      fill: {TEXT_COLOR};
    }}
    {anim_rules}
</style>""")

    # ── Month labels ─────────────────────────────────────────────────
    for week_idx, label in month_markers:
        x = PADDING_LEFT + week_idx * (CELL_SIZE + CELL_GAP)
        parts.append(
            f'<text class="month-label" x="{x}" y="{PADDING_TOP - 8}">'
            f'{label}</text>'
        )

    # ── Day-of-week labels ───────────────────────────────────────────
    for i, label in enumerate(DAY_LABELS):
        if label:
            y = PADDING_TOP + i * (CELL_SIZE + CELL_GAP) + CELL_SIZE - 2
            parts.append(
                f'<text class="day-label" x="{PADDING_LEFT - 8}" y="{y}" '
                f'text-anchor="end">{label}</text>'
            )

    # ── Day boxes (grouped by week for animation) ────────────────────
    for w in range(WEEKS):
        parts.append(f'<g class="week-{w}">')
        for d in range(DAYS):
            cell = grid[w][d]
            if cell is None:
                continue
            x = PADDING_LEFT + w * (CELL_SIZE + CELL_GAP)
            y = PADDING_TOP + d * (CELL_SIZE + CELL_GAP)
            color = map_level(cell["level"])
            parts.append(
                f'  <rect x="{x}" y="{y}" '
                f'width="{CELL_SIZE}" height="{CELL_SIZE}" '
                f'rx="{CELL_RADIUS}" ry="{CELL_RADIUS}" '
                f'fill="{color}" />'
            )
        parts.append('</g>')

    # ── Legend (Less → More) ─────────────────────────────────────────
    legend_y = PADDING_TOP + DAYS * (CELL_SIZE + CELL_GAP) + 16
    legend_x_start = svg_w - PADDING_RIGHT - len(PALETTE) * (CELL_SIZE + CELL_GAP) - 60

    parts.append(
        f'<text class="legend-label" x="{legend_x_start}" y="{legend_y + 10}">'
        f'Less</text>'
    )
    for i, color in enumerate(PALETTE):
        lx = legend_x_start + 32 + i * (CELL_SIZE + CELL_GAP)
        parts.append(
            f'<rect x="{lx}" y="{legend_y}" '
            f'width="{CELL_SIZE}" height="{CELL_SIZE}" '
            f'rx="{CELL_RADIUS}" ry="{CELL_RADIUS}" fill="{color}" />'
        )
    more_x = legend_x_start + 32 + len(PALETTE) * (CELL_SIZE + CELL_GAP) + 4
    parts.append(
        f'<text class="legend-label" x="{more_x}" y="{legend_y + 10}">'
        f'More</text>'
    )

    # ── Stats footer ─────────────────────────────────────────────────
    total = stats.get("total_contributions", 0)
    parts.append(
        f'<text class="stats-text" x="{PADDING_LEFT}" y="{legend_y + 10}">'
        f'{total:,} contributions in the last year</text>'
    )

    parts.append('</svg>')
    return "\n".join(parts)


def main():
    parser = argparse.ArgumentParser(
        description="Render contribution heatmap SVG"
    )
    parser.add_argument(
        "--input", "-i",
        default="data/contributions.json",
        help="Path to contributions JSON (default: data/contributions.json)"
    )
    parser.add_argument(
        "--output", "-o",
        default="contrib-heatmap.svg",
        help="Output SVG path (default: contrib-heatmap.svg)"
    )
    args = parser.parse_args()

    if not Path(args.input).exists():
        print(f"[WARN] Data file not found: {args.input}")
        print("   Run fetch_contributions.py first.")
        return

    data = load_data(args.input)
    svg = build_heatmap_svg(data)

    Path(args.output).write_text(svg, encoding="utf-8")
    total = data.get("stats", {}).get("total_contributions", 0)
    print(f"[OK] Heatmap SVG -> {args.output} ({total:,} contributions)")


if __name__ == "__main__":
    main()
