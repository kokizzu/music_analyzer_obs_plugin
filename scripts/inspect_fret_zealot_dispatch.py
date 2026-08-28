#!/usr/bin/env python3
"""Print Android Fret Zealot packet dispatch and debounce context."""

from __future__ import annotations

from pathlib import Path


ROOT = Path("android/app/src/main/java/dev/benalu/musicanalyzer")
TERMS = (
    "sendStableFretZealotPacket",
    "lastFretZealotPacket",
    "retryFretZealotAutoReconciliation",
    "refreshFretZealotOutput",
    "refreshOutputs",
)


def main() -> int:
    matches: list[tuple[Path, int, list[str]]] = []
    for path in sorted(ROOT.rglob("*.java")):
        lines = path.read_text(encoding="utf-8").splitlines()
        for index, line in enumerate(lines):
            if any(term in line for term in TERMS):
                matches.append((path, index, lines))

    print(f"fret_zealot_dispatch matches={len(matches)}")
    emitted: set[tuple[Path, int]] = set()
    for path, index, lines in matches:
        print(f"[{path}]")
        for line_index in range(max(0, index - 8), min(len(lines), index + 20)):
            key = (path, line_index)
            if key in emitted:
                continue
            emitted.add(key)
            print(f"{line_index + 1}: {lines[line_index]}")
    return 0 if matches else 1


if __name__ == "__main__":
    raise SystemExit(main())
