#!/usr/bin/env python3
"""Show the current analyzer-case log tail and runner state."""

from pathlib import Path


def main() -> None:
    path = Path("build/analyzer_cases.log")
    if not path.exists():
        raise SystemExit("No analyzer-case log exists yet.")
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    print(f"lines={len(lines)}")
    for term in ("melodic full mix no drums", "steady high-frequency OBS input", "analyzer_cases:"):
        matches = [line for line in lines if term.lower() in line.lower()]
        print(f"matches[{term}]={len(matches)}")
        for line in matches[-5:]:
            print(line)
    for line in lines[-60:]:
        print(line)


if __name__ == "__main__":
    main()
