#!/usr/bin/env python3
"""Import complete ESMUC SATB recordings into a prepared multitrack manifest."""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import re
import tempfile
from pathlib import Path


ROLES = (("S", 52), ("A", 53), ("T", 54), ("B", 55))
STEM_RE = re.compile(r"^(?P<prefix>.+)_(?P<role>[SATB])(?P<index>\d+)\.wav$")


def midi_from_hz(frequency: float) -> int | None:
    if not math.isfinite(frequency) or frequency <= 0.0:
        return None
    midi = int(round(69 + 12 * math.log2(frequency / 440.0)))
    return midi if 21 <= midi <= 108 else None


def label_rows(path: Path) -> list[tuple[float, float, int]]:
    rows: list[tuple[float, float, int]] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        fields = line.split()
        if len(fields) < 3:
            continue
        try:
            start, frequency, duration = (float(fields[index]) for index in range(3))
        except ValueError:
            continue
        end = start + duration
        midi = midi_from_hz(frequency)
        if midi is not None and math.isfinite(start) and math.isfinite(end) and end > start:
            rows.append((start, end, midi))
    return rows


def write_notes(path: Path, rows: list[tuple[float, float, int]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as target:
        writer = csv.writer(target)
        writer.writerow(("start", "end", "note"))
        writer.writerows(rows)


def complete_groups(root: Path) -> dict[str, dict[str, Path]]:
    groups: dict[str, dict[str, Path]] = {}
    for audio in sorted(root.glob("*.wav")):
        match = STEM_RE.fullmatch(audio.name)
        if match is None or not audio.with_suffix(".lab").is_file():
            continue
        prefix, role = match["prefix"], match["role"]
        groups.setdefault(prefix, {}).setdefault(role, audio)
    return {
        prefix: tracks
        for prefix, tracks in groups.items()
        if all(role in tracks and label_rows(tracks[role].with_suffix(".lab")) for role, _ in ROLES)
    }


def build_manifest(root: Path, output: Path) -> list[dict[str, object]]:
    notes_root = output / "scores"
    notes_root.mkdir(parents=True, exist_ok=True)
    pieces: list[dict[str, object]] = []
    for prefix, tracks in sorted(complete_groups(root).items()):
        sources: list[dict[str, object]] = []
        for role, instrument in ROLES:
            audio = tracks[role]
            notes = notes_root / f"{prefix}_{role}.csv"
            write_notes(notes, label_rows(audio.with_suffix(".lab")))
            sources.append({"audio": str(audio.resolve()), "notes": str(notes.relative_to(output)), "instrument": instrument})
        pieces.append({"id": f"ESMUC_{prefix}", "sources": sources})
    return pieces


def prepare(root: Path, output: Path, minimum_pieces: int) -> int:
    if not (root / "README.md").is_file():
        raise ValueError(f"missing extracted ESMUC root: {root}")
    manifest = output / "manifest.json"
    if manifest.is_file():
        data = json.loads(manifest.read_text(encoding="utf-8"))
        pieces = data.get("pieces", []) if isinstance(data, dict) else []
        if isinstance(pieces, list) and len(pieces) >= minimum_pieces:
            return len(pieces)
        raise ValueError(f"refusing to replace incomplete prepared manifest: {manifest}")
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=output.parent, prefix=f".{output.name}.tmp-") as temporary:
        staged = Path(temporary)
        pieces = build_manifest(root, staged)
        if len(pieces) < minimum_pieces:
            raise ValueError(f"expected at least {minimum_pieces} complete ESMUC pieces, got {len(pieces)}")
        (staged / "manifest.json").write_text(json.dumps({"pieces": pieces}, indent=2) + "\n", encoding="utf-8")
        os.replace(staged, output)
    return len(pieces)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--minimum-pieces", type=int, default=19)
    args = parser.parse_args(argv)
    try:
        count = prepare(args.root, args.output, args.minimum_pieces)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        parser.error(str(error))
    print(f"prepare_esmuc_choir_dataset_manifest: complete={count} output={args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
