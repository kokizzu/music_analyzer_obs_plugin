#!/usr/bin/env python3
"""Print the Basic Pitch integration points relevant to display-note recovery."""

from __future__ import annotations

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
FILES = (
    ROOT / "src/analyzer.cpp",
    ROOT / "src/basic_pitch_vocal_fusion.hpp",
    ROOT / "src/basic_pitch_onnx_decoder.hpp",
    ROOT / "src/basic_pitch_onnx_worker.hpp",
)
PATTERNS = (
    r"add_basic_pitch_vocal_fusion_candidates",
    r"basic_pitch_notes_ready_",
    r"basic_pitch_notes_",
    r"BasicPitch",
    r"PitchNote",
)
CONTEXT = 18


def print_matches(path: Path) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    matches: list[int] = []
    for index, line in enumerate(lines):
        if any(re.search(pattern, line) for pattern in PATTERNS):
            matches.append(index)

    print(f"## {path.relative_to(ROOT)}")
    if not matches:
        print("no matching integration symbols")
        return

    emitted: set[int] = set()
    for index in matches:
        start = max(0, index - CONTEXT)
        end = min(len(lines), index + CONTEXT + 1)
        visible = [line_number for line_number in range(start, end) if line_number not in emitted]
        if not visible:
            continue
        print(f"-- lines {visible[0] + 1}-{visible[-1] + 1}")
        for line_number in visible:
            print(f"{line_number + 1:6d}: {lines[line_number]}")
            emitted.add(line_number)


def main() -> int:
    for path in FILES:
        print_matches(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
