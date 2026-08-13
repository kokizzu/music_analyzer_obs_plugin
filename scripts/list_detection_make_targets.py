#!/usr/bin/env python3
"""List detection-oriented Make targets without invoking shell search tools."""

import re
import sys
from pathlib import Path


def main() -> None:
    makefile = Path(__file__).resolve().parents[1] / "Makefile"
    lines = makefile.read_text(encoding="utf-8").splitlines()
    matcher = re.compile(r"^([A-Za-z0-9_.-]+):")
    if len(sys.argv) == 2:
        target = sys.argv[1]
        for index, line in enumerate(lines):
            if line.startswith(f"{target}:"):
                for recipe_line in lines[index : index + 8]:
                    if recipe_line and not recipe_line.startswith("."):
                        print(recipe_line)
                return
        raise SystemExit(f"target not found: {target}")

    targets: list[str] = []
    for line in lines:
        match = matcher.match(line)
        if match and any(token in match.group(1) for token in ("guitar", "chord", "note", "drum")):
            targets.append(match.group(1))
    for target in sorted(set(targets)):
        print(target)


if __name__ == "__main__":
    main()
