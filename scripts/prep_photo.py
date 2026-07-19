#!/usr/bin/env python3
"""
prep_photo.py — Remove background, boost local contrast with CLAHE,
composite onto pure white, save as grayscale PNG.

Usage:
    python scripts/prep_photo.py source-photo.jpg
"""

import sys
import pathlib
import numpy as np
from PIL import Image
import cv2
from rembg import remove

def prep(src_path: str) -> None:
    src = pathlib.Path(src_path)
    if not src.exists():
        print(f"[prep_photo] ERROR: {src_path!r} not found.", file=sys.stderr)
        sys.exit(1)

    # ── 1. Remove background ──────────────────────────────────────────────────
    print("[prep_photo] Removing background…")
    with open(src, "rb") as fh:
        raw = fh.read()
    no_bg_bytes = remove(raw)                          # returns RGBA PNG bytes
    rgba = Image.open(__import__("io").BytesIO(no_bg_bytes)).convert("RGBA")

    # ── 2. Boost local contrast with CLAHE ────────────────────────────────────
    print("[prep_photo] Boosting local contrast (CLAHE)…")
    rgb  = rgba.convert("RGB")
    arr  = np.array(rgb, dtype=np.uint8)
    lab  = cv2.cvtColor(arr, cv2.COLOR_RGB2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    l_eq  = clahe.apply(l)
    lab_eq = cv2.merge([l_eq, a, b])
    boosted_arr = cv2.cvtColor(lab_eq, cv2.COLOR_LAB2RGB)
    boosted_rgb = Image.fromarray(boosted_arr)

    # Reattach the alpha mask from the rembg result
    boosted_rgba = boosted_rgb.copy()
    boosted_rgba.putalpha(rgba.getchannel("A"))

    # ── 3. Composite onto white ───────────────────────────────────────────────
    print("[prep_photo] Compositing onto white…")
    white = Image.new("RGBA", boosted_rgba.size, (255, 255, 255, 255))
    white.paste(boosted_rgba, mask=boosted_rgba.getchannel("A"))
    gray  = white.convert("L")

    out_path = src.parent / "source-prepped.png"
    gray.save(out_path)
    print(f"[prep_photo] Done → {out_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/prep_photo.py <source-photo>", file=sys.stderr)
        sys.exit(1)
    prep(sys.argv[1])
