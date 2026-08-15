#!/usr/bin/env python3
"""Unit checks for the safe IRMAS archive and manifest helpers."""

from __future__ import annotations

import csv
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        archive = root / "irmas.zip"
        with zipfile.ZipFile(archive, "w") as output:
            output.writestr("Part1/example.wav", b"wav")
            output.writestr("Part1/example.txt", "pia\n")
        import hashlib
        checksum = hashlib.md5(archive.read_bytes()).hexdigest()
        subprocess.run([sys.executable, "scripts/validate_irmas_archive.py", "--archive", str(archive), "--md5", checksum], cwd=ROOT, check=True)
        extracted = root / "extracted"
        subprocess.run([sys.executable, "scripts/extract_irmas.py", "--archive", str(archive), "--output", str(extracted)], cwd=ROOT, check=True)
        prepared = root / "prepared"
        subprocess.run([sys.executable, "scripts/prepare_irmas_manifest.py", "--root", str(extracted), "--output", str(prepared), "--minimum-samples", "1"], cwd=ROOT, check=True)
        with (prepared / "manifest.tsv").open(newline="", encoding="utf-8") as source:
            rows = list(csv.DictReader(source, delimiter="\t"))
        assert len(rows) == 1
        assert rows[0]["family"] == "piano" and rows[0]["source"] == "irmas/piano"
        assert rows[0]["path"] == "../extracted/Part1/example.wav"
    print("irmas scripts: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
