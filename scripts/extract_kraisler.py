#!/usr/bin/env python3
"""Safely extract KRAISLER into the external sample store."""

import argparse
import os
import shutil
import tempfile
import zipfile
from pathlib import Path

from validate_kraisler_archive import safe_member, validate_archive


def has_layout(root: Path, minimum_tracks: int) -> bool:
    wav_root = next((path for path in root.rglob("performance_wav") if path.is_dir()), None)
    midi_root = next((path for path in root.rglob("performance_midi") if path.is_dir()), None)
    annotation_root = next((path for path in root.rglob("annotation_csv") if path.is_dir()), None)
    if not wav_root or not midi_root or not annotation_root:
        return False
    complete = {
        path.name[:2]
        for path in wav_root.glob("??_PF_dry.wav")
        if (wav_root / f"{path.name[:2]}_VN_dry.wav").is_file()
        and (wav_root / f"{path.name[:2]}_mix_dry.wav").is_file()
        and (midi_root / f"{path.name[:2]}_PF.mid").is_file()
        and (annotation_root / f"{path.name[:2]}_notes_VN.csv").is_file()
    }
    return len(complete) >= minimum_tracks


def extract(archive_path: Path, output: Path, expected_md5: str, minimum_tracks: int) -> int:
    validate_archive(str(archive_path), expected_md5, minimum_tracks)
    if output.exists():
        if has_layout(output, minimum_tracks):
            return sum(1 for path in output.rglob("*") if path.is_file())
        raise ValueError(f"refusing to replace incomplete extraction: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=output.parent, prefix=f".{output.name}.tmp-") as temp_name:
        temp = Path(temp_name)
        with zipfile.ZipFile(archive_path) as archive:
            for member in archive.infolist():
                if member.is_dir():
                    continue
                if not safe_member(member.filename):
                    raise ValueError(f"unsafe archive member: {member.filename}")
                target = temp / member.filename
                target.parent.mkdir(parents=True, exist_ok=True)
                with archive.open(member) as source, open(target, "wb") as destination:
                    shutil.copyfileobj(source, destination)
        if not has_layout(temp, minimum_tracks):
            raise ValueError("missing KRAISLER performance_wav, performance_midi, or annotation_csv layout")
        os.replace(temp, output)
    return sum(1 for path in output.rglob("*") if path.is_file())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--expected-md5", default="")
    parser.add_argument("--minimum-tracks", type=int, default=20)
    args = parser.parse_args(argv)
    try:
        files = extract(args.archive, args.output, args.expected_md5, args.minimum_tracks)
    except (OSError, ValueError, zipfile.BadZipFile) as exc:
        print(f"extract_kraisler: {exc}")
        return 1
    print(f"extract_kraisler: extracted files={files} output={args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
