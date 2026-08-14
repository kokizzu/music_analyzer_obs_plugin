#!/usr/bin/env python3
"""Import CSD SATB stems and section-note labels into a prepared manifest."""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import re
import tempfile
from pathlib import Path


ROLES = (("soprano", 52), ("alto", 53), ("tenor", 54), ("bass", 55))
WORKS = ("ER", "LI", "ND")
SINGER_INDICES = range(1, 5)


def midi_from_hz(frequency: float) -> int | None:
    if not math.isfinite(frequency) or frequency <= 0.0:
        return None
    midi = int(round(69 + 12 * math.log2(frequency / 440.0)))
    return midi if 21 <= midi <= 108 else None


def label_rows(path: Path) -> list[tuple[float, float, int]]:
    rows: list[tuple[float, float, int]] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        fields = [field for field in re.split(r"[\s,;]+", line.strip()) if field]
        if len(fields) < 3:
            continue
        try:
            start, frequency, duration = (float(fields[index]) for index in range(3))
        except ValueError:
            continue
        midi = midi_from_hz(frequency)
        end = start + duration
        if midi is not None and math.isfinite(start) and math.isfinite(end) and end > start:
            rows.append((start, end, midi))
    return rows


def write_notes(path: Path, rows: list[tuple[float, float, int]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as target:
        writer = csv.writer(target)
        writer.writerow(("start", "end", "note"))
        writer.writerows(rows)


def build_manifest(root: Path, output: Path) -> list[dict[str, object]]:
    notes_root = output / "scores"
    notes_root.mkdir(parents=True, exist_ok=True)
    pieces: list[dict[str, object]] = []
    for work in WORKS:
        for singer_index in SINGER_INDICES:
            sources: list[dict[str, object]] = []
            for role, instrument in ROLES:
                stem = root / f"CSD_{work}_{role}_{singer_index}.wav"
                labels = root / f"CSD_{work}_{role}_notes.lab"
                rows = label_rows(labels) if labels.is_file() else []
                if not stem.is_file() or not rows:
                    sources = []
                    break
                notes = notes_root / f"CSD_{work}_{role}_{singer_index}.csv"
                write_notes(notes, rows)
                sources.append({"audio": str(stem.resolve()), "notes": str(notes.relative_to(output)), "instrument": instrument})
            if len(sources) == len(ROLES):
                pieces.append({"id": f"CSD_{work}_Singer{singer_index}", "sources": sources})
    return pieces


def prepare(root: Path, output: Path, minimum_pieces: int) -> int:
    if not (root / "README.txt").is_file():
        raise ValueError(f"missing extracted CSD root: {root}")
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
            raise ValueError(f"expected at least {minimum_pieces} complete CSD pieces, got {len(pieces)}")
        (staged / "manifest.json").write_text(json.dumps({"pieces": pieces}, indent=2) + "\n", encoding="utf-8")
        os.replace(staged, output)
    return len(pieces)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--minimum-pieces", type=int, default=12)
    args = parser.parse_args(argv)
    try:
        count = prepare(args.root, args.output, args.minimum_pieces)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        parser.error(str(error))
    print(f"prepare_choral_singing_dataset_manifest: complete={count} output={args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
