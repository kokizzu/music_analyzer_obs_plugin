#!/usr/bin/env python3
"""Safely extract the checked MIR-1K archive into InstrumentSamples."""

from __future__ import annotations

import argparse
import os
import shutil
import tarfile
import tempfile
from pathlib import Path

from validate_mir1k_dataset import safe_member


READY_FILE = ".mir1k-extraction-complete"


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
        return sum(1 for path in output.rglob("*") if path.is_file() and path.name != READY_FILE)
    if output.exists():
        raise ValueError(f"refusing to replace incomplete extraction: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=output.parent, prefix=f".{output.name}.tmp-") as temporary:
        staged = Path(temporary)
        with tarfile.open(archive_path, "r:gz") as archive:
            for member in archive.getmembers():
                if not safe_member(member):
                    raise ValueError(f"unsafe archive member: {member.name}")
                if member.isdir():
                    continue
                target = staged / member.name
                target.parent.mkdir(parents=True, exist_ok=True)
                source = archive.extractfile(member)
                if source is None:
                    raise ValueError(f"cannot read archive member: {member.name}")
                with source, target.open("wb") as destination:
                    shutil.copyfileobj(source, destination)
        file_count = sum(1 for path in staged.rglob("*") if path.is_file())
        if file_count == 0:
            raise ValueError("archive has no extractable files")
        (staged / READY_FILE).write_text("MIR-1K extraction complete\n", encoding="utf-8")
        os.replace(staged, output)
    return file_count


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--discard-stale-staging", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.discard_stale_staging:
            removed = discard_stale_staging(args.output)
            print(f"extract_mir1k_dataset: discarded stale staging={removed}")
            return 0
        files = extract(args.archive, args.output)
    except (OSError, ValueError, tarfile.TarError) as error:
        parser.error(str(error))
    print(f"extract_mir1k_dataset: extracted files={files} output={args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
