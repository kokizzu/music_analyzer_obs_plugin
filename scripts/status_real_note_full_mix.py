#!/usr/bin/env python3
"""Report active full-mix real-note fixture processes."""

import subprocess


def main() -> int:
    result = subprocess.run(["ps", "-eo", "pid=,args="], check=True, text=True,
                            capture_output=True)
    needles = ("analyzer_real_note_samples", "test-real-note-samples-full-mix")
    matches = [line.strip() for line in result.stdout.splitlines() if any(needle in line for needle in needles)]
    print("\n".join(matches) if matches else "no active full-mix real-note test")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
