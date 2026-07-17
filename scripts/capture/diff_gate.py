# pyright: reportMissingImports=false, reportImplicitRelativeImport=false
"""Perceptual diff gate for re-captures.

Compares a freshly captured PNG against the WebP currently committed for a shot.
If the fraction of changed pixels is below the shot's `diff_threshold`, the UI is
considered unchanged: the committed image is left byte-identical and only the
manifest `verified` date is bumped (no noisy image churn in git). Above the
threshold, the new capture is encoded and `captured` is stamped.

Usage:
    python3 scripts/capture/diff_gate.py <fresh.png> --id <shot-id>

Exit codes:
    0  handled (encoded a first-time capture, skipped as unchanged, or re-encoded)
    2  shot id not found in the manifest

If the shot exists in the manifest but no committed image is on disk yet, the
fresh PNG is encoded as the first-time capture (not an error).
"""

from __future__ import annotations

import argparse
import datetime as _dt
import sys
from pathlib import Path

from PIL import Image, ImageChops

from optimize_webp import encode
from screenshot_lib import Manifest


def changed_fraction(a: Image.Image, b: Image.Image) -> float:
    a = a.convert("RGB")
    b = b.convert("RGB")
    if a.size != b.size:
        b = b.resize(a.size, Image.LANCZOS)
    diff = ImageChops.difference(a, b)
    grayscale = diff.convert("L")
    mask = grayscale.point(lambda px: 255 if px > 16 else 0)
    changed = mask.histogram()[255]
    return changed / (a.width * a.height)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("fresh", type=Path, help="Freshly captured PNG")
    parser.add_argument("--id", required=True, help="Manifest screenshot id")
    args = parser.parse_args()

    manifest = Manifest()
    if args.id not in manifest:
        print(f"unknown id: {args.id}", file=sys.stderr)
        return 2
    shot = manifest.get(args.id)
    today = _dt.date.today().isoformat()

    if not shot.asset_path.exists():
        size = encode(
            args.fresh, shot.asset_path, manifest.target_width, manifest.webp_quality
        )
        manifest.set_captured(args.id, today)
        manifest.save()
        print(f"new capture: {shot.file} ({size / 1024:.0f} KB)")
        return 0

    fraction = changed_fraction(Image.open(shot.asset_path), Image.open(args.fresh))
    if fraction < shot.diff_threshold:
        manifest.set_verified(args.id, today)
        manifest.save()
        print(
            f"unchanged ({fraction:.4%} < {shot.diff_threshold:.2%}): "
            f"verified={today}, image untouched"
        )
        return 0

    size = encode(
        args.fresh, shot.asset_path, manifest.target_width, manifest.webp_quality
    )
    manifest.set_captured(args.id, today)
    manifest.save()
    print(
        f"changed ({fraction:.4%} >= {shot.diff_threshold:.2%}): re-encoded {shot.display_path} ({size / 1024:.0f} KB)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
