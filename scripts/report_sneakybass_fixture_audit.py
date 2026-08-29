#!/usr/bin/env python3
"""Print the persisted Sneakybass audit summary."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


SUMMARY = re.compile(r"^real_bass_fixture: (\d+)/(\d+) expected pitch classes detected$", re.MULTILINE)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--log", required=True, type=Path)
    args = parser.parse_args()
    if not args.log.is_file():
        print(f"sneakybass_audit_log_exists=false path={args.log}")
        return 1
    text = args.log.read_text(encoding="utf-8", errors="replace")
    print(f"sneakybass_audit_log_exists=true path={args.log}")
    for line in text.splitlines()[:3]:
        print(line)
    match = SUMMARY.search(text)
    if not match:
        print("sneakybass_audit_summary=<missing>")
        print("sneakybass_audit_output:")
        for line in text.splitlines()[4:24]:
            print(f"  {line}")
        return 1
    detected, total = (int(value) for value in match.groups())
    percent = 100.0 * detected / total if total else 0.0
    print(f"sneakybass_audit_summary=detected:{detected} total:{total} recall:{percent:.1f}%")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
