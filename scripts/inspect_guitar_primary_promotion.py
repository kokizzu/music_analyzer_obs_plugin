#!/usr/bin/env python3
"""Print the guitar plain-triad promotion guards used for the visible primary label."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PATH = ROOT / "src/analyzer.cpp"
NAMES = (
    "float plain_guitar_component_primary_score(",
    "void promote_supported_plain_guitar_primary(",
    "void promote_weak_visible_root_later_plain_guitar_primary(",
    "void prune_promoted_plain_guitar_primary_aliases(",
)


def print_function(lines: list[str], signature: str) -> None:
    start = next(index for index, line in enumerate(lines) if line.startswith(signature))
    depth = 0
    opened = False
    for index in range(start, len(lines)):
        depth += lines[index].count("{")
        opened = opened or "{" in lines[index]
        depth -= lines[index].count("}")
        if opened and depth == 0:
            print(f"## {index - (index - start) + 1}-{index + 1}")
            for line_index in range(start, index + 1):
                print(f"{line_index + 1}: {lines[line_index]}")
            return
    raise RuntimeError(f"unterminated {signature}")


def main() -> int:
    lines = PATH.read_text(encoding="utf-8").splitlines()
    for signature in NAMES:
        print_function(lines, signature)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
