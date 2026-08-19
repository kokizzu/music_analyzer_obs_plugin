#!/usr/bin/env python3
"""Report locally available safe parallel download clients."""

from __future__ import annotations

import shutil


def main() -> int:
    found = False
    for name in ("aria2c", "axel"):
        path = shutil.which(name)
        if path:
            print(f"parallel_downloader={name} path={path}")
            found = True
    if not found:
        print("parallel_downloader=none")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
