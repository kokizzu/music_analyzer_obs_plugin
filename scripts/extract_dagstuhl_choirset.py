#!/usr/bin/env python3
"""Safely extract the validated DCS archive into the external sample store."""

import argparse
import os
import shutil
import tempfile
import zipfile
from pathlib import Path

from validate_dagstuhl_choirset import safe_member


def extract(archive_path: Path, output: Path) -> int:
    ready_root = output / "DagstuhlChoirSet"
    if (ready_root / "README.md").is_file():
        return sum(1 for path in output.rglob("*") if path.is_file())
    if output.exists():
        raise ValueError(f"refusing to replace incomplete extraction: {output}")
    output_parent = output.parent
    output_parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=output_parent, prefix=f".{output.name}.tmp-") as temp_name:
        temp = Path(temp_name)
        with zipfile.ZipFile(archive_path) as archive:
            members = [member for member in archive.infolist() if not member.is_dir()]
            for member in members:
                if not safe_member(member.filename):
                    raise ValueError(f"unsafe archive member: {member.filename}")
                if member.filename.startswith("__MACOSX/"):
                    continue
                target = temp / member.filename
                target.parent.mkdir(parents=True, exist_ok=True)
                with archive.open(member) as source, open(target, "wb") as destination:
                    shutil.copyfileobj(source, destination)
        root = temp / "DagstuhlChoirSet"
        if not (root / "README.md").is_file():
            raise ValueError("missing DagstuhlChoirSet README after extraction")
        os.replace(temp, output)
        return sum(1 for path in output.rglob("*") if path.is_file())


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        files = extract(args.archive, args.output)
    except (OSError, ValueError, zipfile.BadZipFile) as exc:
        print(f"extract_dagstuhl_choirset: {exc}")
        return 1
    print(f"extract_dagstuhl_choirset: extracted files={files} output={args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
