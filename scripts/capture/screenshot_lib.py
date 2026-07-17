# pyright: reportMissingImports=false, reportMissingTypeArgument=false
"""Shared access layer for the screenshot manifest (scripts/capture/manifest.yaml).

Public API for the WebP optimizer, the diff gate, and the mkdocs `shot()` macro.
Keeping load/save/lookup in one place guarantees all three tools agree on the
manifest shape and on how an ID maps to a file under docs/assets/.

Reads use PyYAML (a mkdocs dependency, always present at docs-build time). Writes
lazily use ruamel round-trip to preserve the hand-authored schema comments; that
path only runs in the capture/CLI environment, never during `mkdocs build`.
"""

from __future__ import annotations

import os
import re
from pathlib import Path

import yaml

# Roots are env-overridable so the pilot can be lifted into a central toolkit
# (or tested from another checkout) without editing the module. Defaults keep
# the in-repo layout working with zero configuration.
REPO_ROOT = Path(
    os.environ.get("CAPTURE_REPO_ROOT", Path(__file__).resolve().parents[2])
).resolve()
MANIFEST_PATH = Path(
    os.environ.get(
        "CAPTURE_MANIFEST", REPO_ROOT / "scripts" / "capture" / "manifest.yaml"
    )
).resolve()
ASSETS_ROOT = Path(
    os.environ.get("CAPTURE_ASSETS_ROOT", REPO_ROOT / "docs" / "assets")
).resolve()

_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_REQUIRED_FIELDS = ("id", "file", "alt")


class ManifestError(ValueError):
    """Raised when the manifest violates the stable-ID / file-path contract."""


class Shot:
    def __init__(self, raw: dict) -> None:
        self._raw = raw

    @property
    def id(self) -> str:
        return self._raw["id"]

    @property
    def file(self) -> str:
        return self._raw["file"]

    @property
    def alt(self) -> str:
        return self._raw["alt"]

    @property
    def diff_threshold(self) -> float:
        return float(self._raw.get("diff_threshold", 0.02))

    @property
    def asset_path(self) -> Path:
        return ASSETS_ROOT / self.file

    @property
    def display_path(self) -> Path:
        try:
            return self.asset_path.relative_to(REPO_ROOT)
        except ValueError:
            return self.asset_path


class Manifest:
    def __init__(self, path: Path = MANIFEST_PATH) -> None:
        self.path = path
        self._data = yaml.safe_load(path.read_text(encoding="utf-8"))
        self._index: dict[str, dict] = {}
        seen_files: dict[str, str] = {}
        for entry in self._data.get("screenshots", []):
            self._validate(entry, seen_files)
            self._index[entry["id"]] = entry
            seen_files[entry["file"]] = entry["id"]
        self._pending: dict[str, dict[str, str]] = {}

    def _validate(self, entry: dict, seen_files: dict[str, str]) -> None:
        for field in _REQUIRED_FIELDS:
            if not entry.get(field):
                raise ManifestError(f"Entry {entry.get('id', '?')} missing '{field}'")
        shot_id, file = entry["id"], entry["file"]
        if shot_id in self._index:
            raise ManifestError(f"Duplicate screenshot id: {shot_id}")
        if file in seen_files:
            raise ManifestError(
                f"Duplicate file '{file}' ({shot_id} and {seen_files[file]})"
            )
        file_path = Path(file)
        if file_path.is_absolute() or ".." in file_path.parts:
            raise ManifestError(
                f"{shot_id}: file must be relative under docs/assets: {file}"
            )
        if file_path.suffix != ".webp":
            raise ManifestError(
                f"{shot_id}: file must be .webp, got {file_path.suffix}"
            )
        if file_path.stem != shot_id:
            raise ManifestError(
                f"{shot_id}: id must equal file stem ({file_path.stem})"
            )
        threshold = entry.get("diff_threshold", 0.02)
        if not isinstance(threshold, (int, float)) or not 0 <= threshold <= 1:
            raise ManifestError(
                f"{shot_id}: diff_threshold must be in [0, 1], got {threshold}"
            )
        for date_field in ("captured", "verified"):
            value = entry.get(date_field)
            if value is not None and not _DATE_RE.match(str(value)):
                raise ManifestError(
                    f"{shot_id}: {date_field} must be YYYY-MM-DD, got {value!r}"
                )

    @property
    def target_width(self) -> int:
        return int(self._data.get("meta", {}).get("target_width", 1440))

    @property
    def webp_quality(self) -> int:
        return int(self._data.get("meta", {}).get("webp_quality", 82))

    def __contains__(self, shot_id: str) -> bool:
        return shot_id in self._index

    def __iter__(self):
        return (Shot(e) for e in self._index.values())

    def get(self, shot_id: str) -> Shot:
        if shot_id not in self._index:
            try:
                where = self.path.relative_to(REPO_ROOT)
            except ValueError:
                where = self.path
            raise KeyError(
                f"Unknown screenshot id '{shot_id}'. Add it to {where} first."
            )
        return Shot(self._index[shot_id])

    def set_verified(self, shot_id: str, date: str) -> None:
        self._index[shot_id]["verified"] = date
        self._pending.setdefault(shot_id, {})["verified"] = date

    def set_captured(self, shot_id: str, date: str) -> None:
        self._index[shot_id]["captured"] = date
        self._index[shot_id]["verified"] = date
        self._pending.setdefault(shot_id, {}).update(captured=date, verified=date)

    def save(self) -> None:
        from ruamel.yaml import YAML

        ryaml = YAML()
        ryaml.preserve_quotes = True
        ryaml.width = 4096
        doc = ryaml.load(self.path.read_text(encoding="utf-8"))
        for entry in doc.get("screenshots", []):
            changes = self._pending.get(entry["id"])
            if changes:
                entry.update(changes)
        with self.path.open("w", encoding="utf-8") as handle:
            ryaml.dump(doc, handle)
        self._pending.clear()
