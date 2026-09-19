#!/usr/bin/env python3
"""Print deployment-script lines that decide whether the share is usable."""

from pathlib import Path


SOURCE = Path("scripts/deploy_windows_self_signed.py")
TOKENS = ("mount_info", "fallback", "mounted share", "SMB")
CONTEXT = 4


def main() -> int:
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    seen: set[int] = set()
    for index, line in enumerate(lines):
        if not any(token.lower() in line.lower() for token in TOKENS):
            continue
        for number in range(max(0, index - CONTEXT), min(len(lines), index + CONTEXT + 1)):
            seen.add(number)
    for number in sorted(seen):
        print(f"{number + 1}: {lines[number]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
