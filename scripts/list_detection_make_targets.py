#!/usr/bin/env python3
"""List Makefile targets related to detection and external device diagnostics."""

from pathlib import Path
import sys


def main() -> None:
    lines = Path("Makefile").read_text(encoding="utf-8").splitlines()
    requested = sys.argv[1] if len(sys.argv) == 2 else ""
    if requested:
        for index, line in enumerate(lines):
            if line.startswith(f"{requested}:"):
                for context_line in lines[index:index + 18]:
                    print(context_line)
                return
        raise SystemExit(f"Makefile target not found: {requested}")
    for index, line in enumerate(lines):
        if not line or line[0].isspace() or ":" not in line:
            continue
        target = line.split(":", 1)[0]
        lowered = target.lower()
        if any(token in lowered for token in ("detect", "analyzer", "fret", "android")):
            print(target)
        if target == "list-detection-make-targets":
            print("-- target context --")
            for context_line in lines[index:index + 6]:
                print(context_line)


if __name__ == "__main__":
    main()
