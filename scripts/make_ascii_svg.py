#!/usr/bin/env python3
"""
make_ascii_svg.py — Convert a prepped grayscale image into an animated
monochrome ASCII-art SVG that "types" itself row by row.

Usage:
    python scripts/make_ascii_svg.py                     # defaults
    python scripts/make_ascii_svg.py --input custom.png  # custom source

Output: avi-ascii.svg

Animation: Each row is revealed left-to-right via a clip-rect animation
(SMIL <animate>), staggered top-to-bottom. A small cursor block rides
the wipe edge. The whole portrait prints once and freezes — no looping.
GitHub renders SMIL inside <img>-embedded SVGs.

Design: Monochrome, single light-gray fill (#c9d1d9). Per-character
rainbow coloring is exactly what makes most ASCII portraits look like
static — one color keeps it clean.
"""

import argparse
from pathlib import Path

from PIL import Image

# ── Density ramp: bright (sparse) → dark (dense) ────────────────────
# Leading space clears the background to nothing.
RAMP = " .`:-=+*cs#%@"

# Dimensions of the character grid
COLS = 100
ROWS = 53

# SVG character metrics (monospace)
CHAR_W = 6.6   # px per character
CHAR_H = 12    # px per row
FONT_SIZE = 11
FILL_COLOR = "#c9d1d9"  # GitHub-flavored light gray
BG_COLOR = "#0d1117"    # GitHub dark background
CURSOR_COLOR = "#58a6ff" # blue cursor block

# Animation timing
ROW_DURATION = 0.12    # seconds for each row to wipe in
ROW_STAGGER = 0.04     # seconds between row starts
FREEZE_FILL = "freeze" # hold final frame


def image_to_ascii_grid(image_path: str) -> list[str]:
    """Downsample image to a character grid using the density ramp."""
    img = Image.open(image_path).convert("L")
    img = img.resize((COLS, ROWS), Image.LANCZOS)

    rows = []
    for y in range(ROWS):
        line = []
        for x in range(COLS):
            brightness = img.getpixel((x, y))
            # Map 0–255 brightness to ramp index (bright=sparse, dark=dense)
            idx = int(brightness / 255 * (len(RAMP) - 1))
            line.append(RAMP[idx])
        rows.append("".join(line))
    return rows


def build_svg(grid: list[str]) -> str:
    """Build a self-contained SVG with row-by-row typing animation."""
    svg_w = COLS * CHAR_W + 20  # some padding
    svg_h = ROWS * CHAR_H + 20

    total_anim_time = ROWS * ROW_STAGGER + ROW_DURATION + 0.5

    parts = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {svg_w:.0f} {svg_h:.0f}" '
        f'width="{svg_w:.0f}" height="{svg_h:.0f}" '
        f'style="background:{BG_COLOR}">'
    )

    # Embedded style for the monospace font
    parts.append("""
<style>
  .ascii {
    font-family: 'Courier New', Courier, monospace;
    font-size: """ + str(FONT_SIZE) + """px;
    fill: """ + FILL_COLOR + """;
    white-space: pre;
    dominant-baseline: text-before-edge;
  }
  .cursor {
    fill: """ + CURSOR_COLOR + """;
  }
</style>
""")

    # Define clip paths and text rows
    for i, row_text in enumerate(grid):
        y = 10 + i * CHAR_H
        begin_time = i * ROW_STAGGER
        row_width = COLS * CHAR_W

        clip_id = f"clip-r{i}"
        group_id = f"row-{i}"

        # Clip path that animates from 0 width to full width
        parts.append(f'<defs>')
        parts.append(f'  <clipPath id="{clip_id}">')
        parts.append(
            f'    <rect x="10" y="{y}" width="0" height="{CHAR_H}">'
        )
        parts.append(
            f'      <animate attributeName="width" '
            f'from="0" to="{row_width:.1f}" '
            f'dur="{ROW_DURATION}s" '
            f'begin="{begin_time:.2f}s" '
            f'fill="{FREEZE_FILL}" />'
        )
        parts.append(f'    </rect>')
        parts.append(f'  </clipPath>')
        parts.append(f'</defs>')

        # Text row clipped by the animated rect
        # Escape XML special characters in the ASCII art
        safe_text = (
            row_text
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
        )
        parts.append(
            f'<text class="ascii" x="10" y="{y}" '
            f'clip-path="url(#{clip_id})">{safe_text}</text>'
        )

        # Cursor block that rides the wipe edge
        parts.append(
            f'<rect class="cursor" x="10" y="{y}" '
            f'width="{CHAR_W:.1f}" height="{CHAR_H}" opacity="0">'
        )
        # Fade in at row start
        parts.append(
            f'  <animate attributeName="opacity" '
            f'from="0" to="0.9" dur="0.01s" '
            f'begin="{begin_time:.2f}s" fill="{FREEZE_FILL}" />'
        )
        # Move across the row
        parts.append(
            f'  <animate attributeName="x" '
            f'from="10" to="{10 + row_width:.1f}" '
            f'dur="{ROW_DURATION}s" '
            f'begin="{begin_time:.2f}s" fill="{FREEZE_FILL}" />'
        )
        # Fade out when row is done
        parts.append(
            f'  <animate attributeName="opacity" '
            f'from="0.9" to="0" dur="0.05s" '
            f'begin="{begin_time + ROW_DURATION:.2f}s" '
            f'fill="{FREEZE_FILL}" />'
        )
        parts.append(f'</rect>')

    parts.append('</svg>')
    return "\n".join(parts)


def main():
    parser = argparse.ArgumentParser(
        description="Convert prepped photo to animated ASCII SVG"
    )
    parser.add_argument(
        "--input", "-i",
        default="source-prepped.png",
        help="Path to the prepped grayscale image (default: source-prepped.png)"
    )
    parser.add_argument(
        "--output", "-o",
        default="avi-ascii.svg",
        help="Output SVG path (default: avi-ascii.svg)"
    )
    args = parser.parse_args()

    if not Path(args.input).exists():
        print(f"[WARN] Source image not found: {args.input}")
        print("   Run prep_photo.py first, or provide --input path.")
        print("   Generating a demo grid with placeholder text...")
        # Generate a simple demo pattern
        grid = []
        for y in range(ROWS):
            row = []
            for x in range(COLS):
                # Create a circular gradient pattern as placeholder
                cx, cy = COLS / 2, ROWS / 2
                dist = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
                max_dist = (cx ** 2 + cy ** 2) ** 0.5
                brightness = min(255, int(dist / max_dist * 255))
                idx = int(brightness / 255 * (len(RAMP) - 1))
                row.append(RAMP[idx])
            grid.append("".join(row))
    else:
        grid = image_to_ascii_grid(args.input)

    svg = build_svg(grid)
    Path(args.output).write_text(svg, encoding="utf-8")
    print(f"[OK] ASCII SVG -> {args.output} ({COLS}x{ROWS} chars)")


if __name__ == "__main__":
    main()
