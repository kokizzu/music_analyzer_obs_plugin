#!/usr/bin/env python3
"""Ensure Windows hardware enumeration output reaches the diagnostic log."""

from pathlib import Path
import sys


SOURCE = Path(__file__).resolve().parents[1] / "src" / "standalone.cpp"


def main() -> int:
    source = SOURCE.read_text(encoding="utf-8")
    if 'freopen_s(&output_stream, log_path.c_str(), "a", stdout)' not in source:
        print("Windows diagnostic logger does not redirect stdout", file=sys.stderr)
        return 1
    if "setvbuf(stdout, nullptr, _IONBF, 0)" not in source:
        print("Windows diagnostic logger does not make stdout unbuffered", file=sys.stderr)
        return 1
    if "Windows hardware probe:" not in source:
        print("Windows hardware probe diagnostics are missing", file=sys.stderr)
        return 1
    print("Windows diagnostic output: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
