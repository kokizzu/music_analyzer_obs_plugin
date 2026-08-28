#!/usr/bin/env python3
"""Print high-signal completion and failure lines from the URMP gate log."""

from pathlib import Path


LOG = Path("build/test_analyzer_urmp.log")
KEYWORDS = ("passed", "failed", "failure", "checks", "error", "warning", "duration")


def main() -> None:
    if not LOG.exists():
        raise SystemExit(f"missing {LOG}; run make test-real-urmp-logged first")
    lines = LOG.read_text(encoding="utf-8", errors="replace").splitlines()
    if len(lines) <= 24:
        for line in lines:
            print(line)
        print(f"log_lines={len(lines)} log={LOG}")
        return
    matches = [line for line in lines if any(word in line.lower() for word in KEYWORDS)]
    for line in matches[-160:]:
        print(line)
    print(f"log_lines={len(lines)} log={LOG}")


if __name__ == "__main__":
    main()
