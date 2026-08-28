#!/usr/bin/env python3
"""Summarize the downloaded ENST-Drums archive without extracting it."""

from __future__ import annotations

import argparse
import hashlib
import re
import tarfile
from collections import Counter
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("archive", type=Path)
    return parser.parse_args()


def md5sum(path: Path) -> str:
    digest = hashlib.md5()  # noqa: S324 - verifies the publisher's supplied checksum.
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    archive = parse_args().archive
    if not archive.is_file():
        raise SystemExit(f"inspect_enst_drums_archive: missing archive: {archive}")

    suffixes: Counter[str] = Counter()
    top_levels: Counter[str] = Counter()
    annotation_labels: Counter[str] = Counter()
    rim_annotation_preview = ""
    rim_members: list[str] = []
    member_samples: list[str] = []
    regular_members = 0
    with tarfile.open(archive, "r:gz") as contents:
        for member in contents:
            if not member.isfile():
                continue
            regular_members += 1
            path = Path(member.name)
            if len(member_samples) < 20:
                member_samples.append(member.name)
            if "rim-shot" in member.name:
                rim_members.append(member.name)
            suffixes[path.suffix.lower() or "<none>"] += 1
            if path.parts:
                top_levels[path.parts[0]] += 1
            if "/annotation/" in member.name and path.suffix.lower() == ".txt":
                match = re.match(r"^\d+_(.+)_(?:sticks|brushes|mallets|pedal)_x\d+$", path.stem)
                if match:
                    annotation_labels[match.group(1)] += 1
                if not rim_annotation_preview and "hits_rim-shot" in path.stem:
                    source = contents.extractfile(member)
                    if source is not None:
                        rim_annotation_preview = source.read(1024).decode("utf-8", errors="replace").replace("\n", " | ").strip()

    audio_count = sum(suffixes[suffix] for suffix in (".flac", ".wav", ".mp3"))
    midi_count = sum(suffixes[suffix] for suffix in (".mid", ".midi"))
    print(f"archive={archive}")
    print(f"size_bytes={archive.stat().st_size}")
    print(f"md5={md5sum(archive)}")
    print(f"regular_members={regular_members}")
    print(f"audio_members={audio_count}")
    print(f"midi_members={midi_count}")
    print("top_levels=" + ",".join(f"{name}:{count}" for name, count in sorted(top_levels.items())))
    print("suffixes=" + ",".join(f"{name}:{count}" for name, count in sorted(suffixes.items())))
    print("annotation_labels=" + ",".join(f"{name}:{count}" for name, count in sorted(annotation_labels.items())))
    print("rim_annotation_preview=" + rim_annotation_preview)
    print("rim_members=" + ",".join(rim_members))
    print("member_samples=" + ",".join(member_samples))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
