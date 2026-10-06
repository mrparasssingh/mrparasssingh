#!/usr/bin/env python3
"""
prep_photo.py — Remove background, boost contrast (CLAHE), composite on white.

Usage:
    python scripts/prep_photo.py source-photo.jpg

Output: source-prepped.png (grayscale, white background, high-contrast face)

Why CLAHE?  A flatly-lit face converts to a dark, unreadable blob in ASCII.
CLAHE (Contrast-Limited Adaptive Histogram Equalization) pulls out real
highlights and shadows from an otherwise flat exposure.
"""

import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from rembg import remove


def prep_photo(input_path: str, output_path: str = "source-prepped.png") -> None:
    """Full pipeline: background removal → CLAHE → white composite."""

    # ── 1. Remove background with rembg ──────────────────────────────
    raw = Path(input_path).read_bytes()
    nobg = remove(raw)  # returns PNG bytes with alpha channel

    img = Image.open(__import__("io").BytesIO(nobg)).convert("RGBA")

    # ── 2. Composite onto pure white ─────────────────────────────────
    #    White maps to spaces in the ASCII ramp, so the background
    #    disappears and only the subject prints.
    white_bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
    composited = Image.alpha_composite(white_bg, img)
    gray = composited.convert("L")  # grayscale

    # ── 3. Boost local contrast with CLAHE ───────────────────────────
    arr = np.array(gray)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(arr)

    result = Image.fromarray(enhanced)
    result.save(output_path)
    print(f"[OK] Saved prepped photo -> {output_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/prep_photo.py <source-photo>")
        sys.exit(1)

    src = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else "source-prepped.png"
    prep_photo(src, out)
