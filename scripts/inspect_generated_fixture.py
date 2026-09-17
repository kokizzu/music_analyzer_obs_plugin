#!/usr/bin/env python3
"""Inspect the known untracked audio fixture without reading binary content."""

from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "third_party" / "beat_and_tempo_tracking" / "demos" / "offline" / "3_min_90_bpm.wav"


def main() -> int:
    if not PATH.exists():
        print(f"missing: {PATH}")
        return 0
    digest = hashlib.sha256(PATH.read_bytes()).hexdigest()
    stat = PATH.stat()
    print(f"path: {PATH}")
    print(f"bytes: {stat.st_size}")
    print(f"sha256: {digest}")
    ignored = subprocess.run(
        ["git", "check-ignore", "--quiet", str(PATH.relative_to(ROOT))],
        cwd=ROOT,
        check=False,
    ).returncode == 0
    print(f"ignored: {'yes' if ignored else 'no'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
