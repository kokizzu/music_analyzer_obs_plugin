#!/usr/bin/env python3
"""Print the deterministic IDMT-SMT-Bass archive import plan."""

from __future__ import annotations

import pathlib


ROOT = pathlib.Path("build/InstrumentSamples/idmt_smt_bass")
URL = "https://zenodo.org/records/7188892/files/IDMT-SMT-BASS.zip?download=1"


def main() -> int:
    print(f"archive: {ROOT / 'IDMT-SMT-BASS.zip'}")
    print(f"extract root: {ROOT / 'source'}")
    print(f"url: {URL}")
    print("operation: resumable download, ZIP validation, then extraction under build only")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
