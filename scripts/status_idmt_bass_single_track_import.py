#!/usr/bin/env python3
"""Report active compact-IDMT importer processes without changing them."""

from __future__ import annotations

import subprocess


def main() -> int:
    result = subprocess.run(
        ["pgrep", "-af", "import_idmt_bass_single_track_archive.py"],
        text=True,
        capture_output=True,
        check=False,
    )
    print(result.stdout.rstrip() or "no active compact IDMT bass importer")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
