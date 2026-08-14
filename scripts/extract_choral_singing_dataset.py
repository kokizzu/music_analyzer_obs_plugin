#!/usr/bin/env python3
"""Safely extract the validated Choral Singing Dataset outside the repository."""

from __future__ import annotations

import argparse
import os
import shutil
import tempfile
import zipfile
from pathlib import Path

from validate_choral_singing_dataset import safe_member


READY_ROOT = "ChoralSingingDataset"


def extract(archive_path: Path, output: Path) -> int:
    ready_root = output / READY_ROOT
    if (ready_root / "README.txt").is_file():
        return sum(1 for path in output.rglob("*") if path.is_file())
    if output.exists():
        raise ValueError(f"refusing to replace incomplete extraction: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=output.parent, prefix=f".{output.name}.tmp-") as temporary:
        temp = Path(temporary)
        with zipfile.ZipFile(archive_path) as archive:
            members = [entry for entry in archive.infolist() if not entry.is_dir()]
            for entry in members:
                if not safe_member(entry.filename):
                    raise ValueError(f"unsafe archive member: {entry.filename}")
                target = temp / entry.filename
                target.parent.mkdir(parents=True, exist_ok=True)
                with archive.open(entry) as source, target.open("wb") as destination:
                    shutil.copyfileobj(source, destination)
        if not (temp / READY_ROOT / "README.txt").is_file():
            raise ValueError("missing ChoralSingingDataset README after extraction")
        os.replace(temp, output)
    return sum(1 for path in output.rglob("*") if path.is_file())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        files = extract(args.archive, args.output)
    except (OSError, ValueError, zipfile.BadZipFile) as error:
        parser.error(str(error))
    print(f"extract_choral_singing_dataset: extracted files={files} output={args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
