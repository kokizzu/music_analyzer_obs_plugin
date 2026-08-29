#!/usr/bin/env python3
"""Report fixture cache paths and whether they resolve outside the checkout."""

from __future__ import annotations

import os
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "build"


def describe(path: Path) -> str:
    if not path.exists() and not path.is_symlink():
        return "missing"
    resolved = path.resolve()
    location = "external" if not resolved.is_relative_to(ROOT) else "in-repo"
    if path.is_symlink():
        return f"symlink -> {resolved} ({location})"
    return f"directory -> {resolved} ({location})"


def main() -> int:
    cache_names = (
        "InstrumentSamples",
        "drum_samples_spread",
        "real_note_samples",
        "real_audio_fixture_cache",
        "external_multitrack",
    )
    print(f"repository={ROOT}")
    for name in cache_names:
        print(f"build/{name}: {describe(BUILD / name)}")

    references: dict[str, list[str]] = {}
    sources = [ROOT / "Makefile", *sorted((ROOT / "scripts").glob("*.py"))]
    for source in sources:
        try:
            content = source.read_text(encoding="utf-8")
        except OSError:
            continue
        for line_number, line in enumerate(content.splitlines(), start=1):
            for match in re.finditer(
                r"build/[A-Za-z0-9_.-]*(?:sample|fixture|multitrack)[A-Za-z0-9_.-]*",
                line,
                re.I,
            ):
                references.setdefault(match.group(0), []).append(
                    f"{source.relative_to(ROOT)}:{line_number}"
                )

    print("download-cache-references:")
    for reference in sorted(references):
        print(f"  {reference}: {describe(ROOT / reference)}")
        for location in references[reference][:3]:
            print(f"    {location}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
