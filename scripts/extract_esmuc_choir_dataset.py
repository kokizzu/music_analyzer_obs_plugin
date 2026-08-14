#!/usr/bin/env python3
"""Safely extract the validated flat ESMUC Choir Dataset outside the repository."""

from __future__ import annotations

import argparse
import os
import shutil
import tempfile
import zipfile
from pathlib import Path

from validate_esmuc_choir_dataset import safe_member


READY_FILE = "README.md"


def discard_stale_staging(output: Path) -> int:
    prefix = f".{output.name}.tmp-"
    removed = 0
    for path in output.parent.glob(f"{prefix}*"):
        if not path.is_dir() or not path.name.startswith(prefix):
            raise ValueError(f"refusing to remove unexpected staging path: {path}")
        shutil.rmtree(path)
        removed += 1
    return removed


def extract(archive_path: Path, output: Path) -> int:
    if (output / READY_FILE).is_file():
        return sum(1 for path in output.rglob("*") if path.is_file())
    if output.exists():
        raise ValueError(f"refusing to replace incomplete extraction: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=output.parent, prefix=f".{output.name}.tmp-") as temporary:
        staged = Path(temporary)
        with zipfile.ZipFile(archive_path) as archive:
            members = [entry for entry in archive.infolist() if not entry.is_dir()]
            for entry in members:
                if not safe_member(entry.filename):
                    raise ValueError(f"unsafe archive member: {entry.filename}")
                target = staged / entry.filename
                target.parent.mkdir(parents=True, exist_ok=True)
                with archive.open(entry) as source, target.open("wb") as destination:
                    shutil.copyfileobj(source, destination)
        if not (staged / READY_FILE).is_file():
            raise ValueError(f"missing {READY_FILE} after extraction")
        os.replace(staged, output)
    return sum(1 for path in output.rglob("*") if path.is_file())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--discard-stale-staging", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.discard_stale_staging:
            removed = discard_stale_staging(args.output)
            print(f"extract_esmuc_choir_dataset: discarded stale staging={removed}")
            return 0
        files = extract(args.archive, args.output)
    except (OSError, ValueError, zipfile.BadZipFile) as error:
        parser.error(str(error))
    print(f"extract_esmuc_choir_dataset: extracted files={files} output={args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
