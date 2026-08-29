#!/usr/bin/env python3
"""Print manifest and audio-loading paths from the real-note test executable."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "tests" / "analyzer_real_note_samples.cpp"


def main() -> int:
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    manifest_start = next(index for index, line in enumerate(lines) if line.startswith("bool read_manifest("))
    depth = 0
    manifest_end = manifest_start
    for index in range(manifest_start, len(lines)):
        depth += lines[index].count("{") - lines[index].count("}")
        if index > manifest_start and depth == 0:
            manifest_end = index
            break
    print(f"--- {SOURCE}:{manifest_start + 1} read_manifest ---")
    for index in range(manifest_start, manifest_end + 1):
        print(f"{index + 1:6d}  {lines[index]}")

    main_start = next(index for index, line in enumerate(lines) if line.startswith("int main("))
    print(f"--- {SOURCE}:{main_start + 1} main sample loop ---")
    for index in range(main_start, min(len(lines), main_start + 290)):
        print(f"{index + 1:6d}  {lines[index]}")

    attribute_start = next(index for index, line in enumerate(lines) if line.startswith("void append_attribute_rows("))
    depth = 0
    entered = False
    attribute_end = attribute_start
    for index in range(attribute_start, len(lines)):
        opens = lines[index].count("{")
        depth += opens - lines[index].count("}")
        entered = entered or opens > 0
        if entered and depth == 0:
            attribute_end = index
            break
    print(f"--- {SOURCE}:{attribute_start + 1} append_attribute_rows ---")
    for index in range(attribute_start, attribute_end + 1):
        print(f"{index + 1:6d}  {lines[index]}")

    matches = [index for index, line in enumerate(lines) if "manifest" in line.lower() or "load_" in line.lower()]
    printed: set[int] = set()
    for match in matches:
        start = max(0, match - 5)
        end = min(len(lines), match + 16)
        if any(index in printed for index in range(start, end)):
            continue
        print(f"--- {SOURCE}:{match + 1} ---")
        for index in range(start, end):
            printed.add(index)
            print(f"{index + 1:6d}  {lines[index]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
