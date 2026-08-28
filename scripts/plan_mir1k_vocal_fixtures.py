#!/usr/bin/env python3
"""Validate prerequisites and document the MIR-1K real-vocal fixture import."""

from pathlib import Path
import shutil


ROOT = Path(__file__).resolve().parents[1]
ARCHIVE_URL = "https://figshare.com/ndownloader/files/10256751"


def main() -> int:
    print("MIR-1K fixture import plan")
    print(f"source: {ARCHIVE_URL}")
    print("license: CC BY 4.0")
    print("archive size: approximately 760 MB")
    print("planned output: build/mir1k_vocal_fixtures")
    print("planned fixture policy: stable voiced excerpts from the vocal channel, with manual pitch contours")
    print("tools:")
    for tool in ("7z", "7zz", "unrar", "ffmpeg"):
        print(f"  {tool}: {shutil.which(tool) or 'missing'}")
    manifest = ROOT / "build/real_note_samples/manifest.tsv"
    if manifest.is_file():
        header = manifest.read_text(encoding="utf-8").splitlines()[0]
        print(f"existing manifest header: {header}")
    else:
        print("existing manifest: missing")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
