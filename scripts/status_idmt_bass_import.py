#!/usr/bin/env python3
"""Report resumable IDMT-SMT-Bass archive import progress."""

from __future__ import annotations

import pathlib


ROOT = pathlib.Path("build/InstrumentSamples/idmt_smt_bass")


def main() -> int:
    partial = ROOT / "IDMT-SMT-BASS.zip.part"
    archive = ROOT / "IDMT-SMT-BASS.zip"
    print(f"partial bytes: {partial.stat().st_size if partial.exists() else 0}")
    print(f"archive bytes: {archive.stat().st_size if archive.exists() else 0}")
    active: list[str] = []
    for proc in pathlib.Path("/proc").iterdir():
        if not proc.name.isdigit():
            continue
        try:
            command = (proc / "cmdline").read_bytes().replace(b"\0", b" ").decode("utf-8", "replace")
        except OSError:
            continue
        if "import_idmt_bass_archive.py" in command or "IDMT-SMT-BASS.zip.part" in command:
            active.append(f"pid={proc.name} {command}")
    print("active importers:")
    print("\n".join(active) if active else "none")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
