#!/usr/bin/env python3
"""Create a symlink-only real-note fixture selected from an existing manifest."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-manifest", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument(
        "--source-token",
        action="append",
        required=True,
        help="case-insensitive source or id token; repeat to union several instruments",
    )
    args = parser.parse_args()

    tokens = tuple(token.casefold() for token in args.source_token)
    source_root = args.source_manifest.parent.resolve()
    output = args.output
    audio_output = output / "audio"
    output.mkdir(parents=True, exist_ok=True)
    audio_output.mkdir(parents=True, exist_ok=True)

    selected: list[dict[str, str]] = []
    with args.source_manifest.open(newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        fields = reader.fieldnames or []
        for row in reader:
            source = row.get("source", "").casefold()
            sample_id = row.get("id", "").casefold()
            if any(token in source or token in sample_id for token in tokens):
                selected.append(row)

    if not selected:
        raise SystemExit(f"no rows matching {args.source_token!r} in {args.source_manifest}")

    manifest_path = output / "manifest.tsv"
    with manifest_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in selected:
            source_audio = source_root / row["path"]
            if not source_audio.is_file():
                raise SystemExit(f"missing source audio: {source_audio}")
            fixture_path = Path("audio") / source_audio.name
            destination = output / fixture_path
            if destination.is_symlink() and destination.resolve() != source_audio.resolve():
                destination.unlink()
            if not destination.exists():
                destination.symlink_to(source_audio)
            row["path"] = str(fixture_path)
            writer.writerow(row)

    print(f"prepared {len(selected)} symlinked rows: {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
