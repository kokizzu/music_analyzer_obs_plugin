#!/usr/bin/env python3
"""Print URMP diagnostics and note-tracking code around pre-envelope candidates."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FILES = (ROOT / "tests/analyzer_urmp.cpp", ROOT / "src/analyzer.cpp")


def main() -> int:
    for path in FILES:
        if not path.is_file():
            continue
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        if path.name == "analyzer_urmp.cpp":
            print(f"## {path.relative_to(ROOT)} source-name call site")
            for index in range(1940, min(2010, len(lines))):
                print(f"{index + 1:6d}: {lines[index]}")
        terms = ("pre-envelope", "source_hint_for_instrument") if path.name == "analyzer_urmp.cpp" else ("other_new_notes",)
        matches = [index for index, line in enumerate(lines) if any(term in line for term in terms)]
        print(f"## {path.relative_to(ROOT)} matches={len(matches)}")
        emitted: set[int] = set()
        for match in matches:
            start = max(0, match - 24)
            end = min(len(lines), match + 40)
            for index in range(start, end):
                if index in emitted:
                    continue
                print(f"{index + 1:6d}: {lines[index]}")
                emitted.add(index)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
