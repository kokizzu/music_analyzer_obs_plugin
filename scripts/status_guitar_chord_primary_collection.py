#!/usr/bin/env python3
"""Report whether the repository's guitar chord collection is still running."""

import subprocess


def main() -> int:
    result = subprocess.run(["ps", "-eo", "pid=,args="], check=True, text=True,
                            capture_output=True)
    needles = ("collect_guitar_chord_primary_attributes.py", "analyzer_guitarset")
    matches = [line.strip() for line in result.stdout.splitlines() if any(needle in line for needle in needles)]
    print("\n".join(matches) if matches else "no active guitar chord collection")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
