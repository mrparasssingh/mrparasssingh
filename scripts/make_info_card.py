#!/usr/bin/env python3
"""
make_info_card.py — Generate a neofetch-style info card SVG.

Usage:
    python scripts/make_info_card.py               # animated
    STATIC=1 python scripts/make_info_card.py      # frozen frame for previews

Output: info-card.svg

The card shows role, current/previous work, tech stack, and highlights
in a terminal-aesthetic layout. Each line fades and slides in on a short
stagger so the panel looks like it's printing next to the ASCII portrait.

Customise the INFO_LINES list below to match your own details.
"""

import os
from pathlib import Path

# ── Configuration ────────────────────────────────────────────────────
USERNAME = "mrparasssingh"
DISPLAY_NAME = "Paras Singh"
OUTPUT = "info-card.svg"

# Color tokens (GitHub dark theme)
BG = "#0d1117"
BORDER = "#30363d"
TITLE_COLOR = "#58a6ff"
KEY_COLOR = "#79c0ff"
VALUE_COLOR = "#c9d1d9"
ACCENT = "#39d353"    # green accent for highlights
MUTED = "#8b949e"
SEPARATOR = "#21262d"

# Layout
CARD_W = 460
CARD_H = 310
PADDING = 24
LINE_H = 26
FONT_SIZE = 13
TITLE_FONT_SIZE = 15

# Neofetch-style info lines: (key, value, optional_color_override)
INFO_LINES = [
    ("", f"{DISPLAY_NAME}@github", TITLE_COLOR),
    ("", "─" * 30, SEPARATOR),
    ("Role", "Developer & Builder", None),
    ("Now", "Building cool things", None),
    ("Prev", "Learning & experimenting", None),
    ("Stack", "Python · JavaScript · Git", None),
    ("Editor", "VS Code", None),
    ("Shell", "PowerShell / Bash", None),
    ("", "─" * 30, SEPARATOR),
    ("🏆", "Open to collaboration", ACCENT),
    ("📫", "Reach me on GitHub", ACCENT),
]

# Animation
LINE_STAGGER = 0.15   # seconds between each line
LINE_DURATION = 0.3   # seconds for each line's fade-in
STATIC_MODE = os.environ.get("STATIC", "0") == "1"


def build_info_card() -> str:
    """Build the neofetch-style info card SVG."""
    # Calculate card height dynamically
    num_lines = len(INFO_LINES)
    content_h = PADDING * 2 + num_lines * LINE_H + 20
    card_h = max(CARD_H, content_h)

    parts = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {CARD_W} {card_h}" '
        f'width="{CARD_W}" height="{card_h}" '
        f'style="background:{BG}">'
    )

    # Styles
    anim_css = ""
    if not STATIC_MODE:
        anim_css = """
    .info-line {
      opacity: 0;
      transform: translateX(-10px);
      animation-fill-mode: forwards;
    }"""
        # Generate keyframe animation for line fade-in
        for i in range(num_lines):
            delay = i * LINE_STAGGER
            anim_css += f"""
    .info-line-{i} {{
      animation: fadeSlideIn {LINE_DURATION}s ease-out {delay:.2f}s forwards;
    }}"""
        anim_css += """
    @keyframes fadeSlideIn {
      from {
        opacity: 0;
        transform: translateX(-10px);
      }
      to {
        opacity: 1;
        transform: translateX(0);
      }
    }"""
    else:
        anim_css = """
    .info-line {
      opacity: 1;
    }"""

    parts.append(f"""<style>
    .key {{
      font-family: 'Courier New', Courier, monospace;
      font-size: {FONT_SIZE}px;
      fill: {KEY_COLOR};
      font-weight: bold;
    }}
    .val {{
      font-family: 'Courier New', Courier, monospace;
      font-size: {FONT_SIZE}px;
      fill: {VALUE_COLOR};
    }}
    .title {{
      font-family: 'Courier New', Courier, monospace;
      font-size: {TITLE_FONT_SIZE}px;
      font-weight: bold;
    }}
    .separator {{
      font-family: 'Courier New', Courier, monospace;
      font-size: {FONT_SIZE}px;
      fill: {MUTED};
    }}
    {anim_css}
</style>""")

    # Card border (rounded rect)
    parts.append(
        f'<rect x="1" y="1" width="{CARD_W - 2}" height="{card_h - 2}" '
        f'rx="8" ry="8" fill="{BG}" stroke="{BORDER}" stroke-width="1" />'
    )

    # Terminal dots (macOS-style)
    dot_y = 16
    for j, color in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
        parts.append(
            f'<circle cx="{PADDING + j * 20}" cy="{dot_y}" r="5" fill="{color}" />'
        )

    # Info lines
    y_start = dot_y + 30
    for i, (key, value, color_override) in enumerate(INFO_LINES):
        y = y_start + i * LINE_H
        line_class = f"info-line info-line-{i}" if not STATIC_MODE else "info-line"

        if not key:
            # Title or separator line
            fill = color_override or VALUE_COLOR
            css_class = "title" if i == 0 else "separator"
            parts.append(
                f'<text class="{css_class} {line_class}" '
                f'x="{PADDING}" y="{y}" fill="{fill}">{_esc(value)}</text>'
            )
        else:
            # Key: Value pair
            val_color = color_override or VALUE_COLOR
            parts.append(f'<g class="{line_class}">')
            parts.append(
                f'  <text class="key" x="{PADDING}" y="{y}">{_esc(key)}</text>'
            )
            # Offset value after key
            key_offset = PADDING + len(key) * 8 + 12
            parts.append(
                f'  <text class="val" x="{key_offset}" y="{y}" '
                f'fill="{val_color}">{_esc(value)}</text>'
            )
            parts.append(f'</g>')

    parts.append('</svg>')
    return "\n".join(parts)


def _esc(text: str) -> str:
    """Escape XML special characters."""
    return (
        text
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("'", "&apos;")
    )


def main():
    svg = build_info_card()
    Path(OUTPUT).write_text(svg, encoding="utf-8")
    mode = "STATIC" if STATIC_MODE else "animated"
    print(f"[OK] Info card ({mode}) -> {OUTPUT}")


if __name__ == "__main__":
    main()
