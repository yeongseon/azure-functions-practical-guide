# pyright: reportMissingImports=false, reportImplicitRelativeImport=false
"""Downscale a source PNG to the manifest target width and encode WebP.

Usage:
    python3 scripts/capture/optimize_webp.py <source.png> --id <shot-id>

Writes the .webp next to its manifest `file` path under docs/assets/ and stamps
`captured`/`verified` on the manifest entry. Intended to run right after a raw
Playwright capture produces a 1600px-wide PNG.
"""

from __future__ import annotations

import argparse
import datetime as _dt
from pathlib import Path

from PIL import Image

from screenshot_lib import Manifest


def encode(source: Path, dest: Path, target_width: int, quality: int) -> int:
    image = Image.open(source)
    if image.mode not in ("RGB", "RGBA"):
        image = image.convert("RGB")
    if image.width > target_width:
        height = round(image.height * target_width / image.width)
        image = image.resize((target_width, height), Image.LANCZOS)
    dest.parent.mkdir(parents=True, exist_ok=True)
    image.save(dest, format="WEBP", quality=quality, method=6)
    return dest.stat().st_size


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="Source PNG to encode")
    parser.add_argument("--id", required=True, help="Manifest screenshot id")
    args = parser.parse_args()

    manifest = Manifest()
    shot = manifest.get(args.id)
    size = encode(
        args.source, shot.asset_path, manifest.target_width, manifest.webp_quality
    )
    manifest.set_captured(args.id, _dt.date.today().isoformat())
    manifest.save()

    rel = shot.display_path
    print(f"wrote {rel} ({size / 1024:.0f} KB)")
    if size > 200 * 1024:
        print(f"WARNING: {rel} exceeds 200 KB target")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
