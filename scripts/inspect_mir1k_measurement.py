#!/usr/bin/env python3
"""Inspect MIR-1K analyzer artifacts without rerunning the analyzer."""

from __future__ import annotations

import argparse
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--measurement", required=True, type=Path)
    parser.add_argument("--attributes", required=True, type=Path)
    args = parser.parse_args(argv)
    for label, path in (("measurement", args.measurement), ("attributes", args.attributes)):
        print(f"inspect_mir1k_measurement: {label}={'present' if path.is_file() else 'missing'}" +
              (f" bytes={path.stat().st_size}" if path.is_file() else ""))
    if args.measurement.is_file():
        lines = args.measurement.read_text(encoding="utf-8", errors="replace").splitlines()
        for line in lines[-24:]:
            print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
