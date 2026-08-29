#!/usr/bin/env python3
"""Print the analysis snapshot declaration used by test diagnostics."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    candidates = []
    for directory in (ROOT / "include", ROOT / "src"):
        candidates.extend(directory.rglob("*.hpp"))
        candidates.extend(directory.rglob("*.h"))
    for path in sorted(candidates):
        lines = path.read_text(encoding="utf-8").splitlines()
        for start, line in enumerate(lines):
            if "struct AnalysisSnapshot" not in line:
                continue
            depth = 0
            for index in range(start, len(lines)):
                depth += lines[index].count("{") - lines[index].count("}")
                print(f"{path}:{index + 1}: {lines[index]}")
                if index > start and depth == 0:
                    return 0
    raise SystemExit("AnalysisSnapshot declaration not found")


if __name__ == "__main__":
    main()
