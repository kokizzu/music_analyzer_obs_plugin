#!/usr/bin/env python3
"""Inventory the SCMS ZIP without extracting its large audio payload."""

from __future__ import annotations

import argparse
import collections
import zipfile
from pathlib import Path, PurePosixPath


ANNOTATION_SUFFIXES = frozenset({".csv", ".lab"})
EXAMPLE_SUFFIXES = frozenset({".wav", ".flac", ".mp3", ".csv", ".lab"})


def preview_annotation(archive: zipfile.ZipFile, member: zipfile.ZipInfo) -> str:
    """Return a short, single-line preview without extracting a member to disk."""
    with archive.open(member) as source:
        text = source.read(512).decode("utf-8", errors="replace")
    return " ".join(text.splitlines())[:240]


def inspect(path: Path) -> dict[str, object]:
    with zipfile.ZipFile(path) as archive:
        members = [member for member in archive.infolist() if not member.is_dir()]
        examples: dict[str, str] = {}
        annotation_previews: dict[str, str] = {}
        for member in members:
            suffix = Path(member.filename).suffix.lower()
            if suffix in EXAMPLE_SUFFIXES and suffix not in examples:
                examples[suffix] = member.filename
            if suffix in ANNOTATION_SUFFIXES and suffix not in annotation_previews:
                annotation_previews[suffix] = f"{member.filename}: {preview_annotation(archive, member)}"
    roots: collections.Counter[str] = collections.Counter()
    extensions: collections.Counter[str] = collections.Counter()
    sizes: collections.Counter[str] = collections.Counter()
    for member in members:
        parts = PurePosixPath(member.filename).parts
        roots[parts[0] if parts else "--"] += 1
        suffix = Path(member.filename).suffix.lower() or "[none]"
        extensions[suffix] += 1
        sizes[suffix] += member.file_size
    return {
        "members": len(members),
        "roots": roots,
        "extensions": extensions,
        "sizes": sizes,
        "examples": examples,
        "annotation_previews": annotation_previews,
    }


def summary(path: Path) -> str:
    result = inspect(path)
    lines = [f"scms_archive: {path}", f"members: {result['members']}", "roots:"]
    lines.extend(f"  {key}: {count}" for key, count in sorted(result["roots"].items()))
    lines.append("extensions:")
    for key in sorted(result["extensions"]):
        lines.append(
            f"  {key}: {result['extensions'][key]} files {result['sizes'][key]} bytes"
        )
    if result["examples"]:
        lines.append("examples:")
        lines.extend(f"  {key}: {result['examples'][key]}" for key in sorted(result["examples"]))
    if result["annotation_previews"]:
        lines.append("annotation_previews:")
        lines.extend(
            f"  {key}: {result['annotation_previews'][key]}"
            for key in sorted(result["annotation_previews"])
        )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        print(summary(args.archive), end="")
    except (OSError, zipfile.BadZipFile) as error:
        parser.error(str(error))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
