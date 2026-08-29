#!/usr/bin/env python3
"""Manage external-only vocadito fixtures used to evaluate singing detection."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import urllib.request
import zipfile
from pathlib import Path, PurePosixPath


REPO_ROOT = Path(__file__).resolve().parents[1]
SAMPLE_LINK = REPO_ROOT / "build" / "real_instrument_expansion_samples"
VOCADITO_URL = "https://zenodo.org/records/5578807/files/vocadito.zip?download=1"
VOCADITO_MD5 = "dea40fd18f14d899643c4ba221b33a46"
VOCADITO_NAME = "vocadito.zip"


def external_root() -> Path:
    if not SAMPLE_LINK.exists():
        raise RuntimeError(f"external fixture link is missing: {SAMPLE_LINK}")
    return SAMPLE_LINK.resolve()


def digest(path: Path) -> str:
    checksum = hashlib.md5()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            checksum.update(block)
    return checksum.hexdigest()


def safe_extract(archive: zipfile.ZipFile, destination: Path) -> None:
    destination = destination.resolve()
    for member in archive.infolist():
        relative = PurePosixPath(member.filename)
        if relative.is_absolute() or ".." in relative.parts:
            raise RuntimeError(f"unsafe archive member: {member.filename}")
        target = (destination / relative).resolve()
        if not target.is_relative_to(destination):
            raise RuntimeError(f"archive member escapes destination: {member.filename}")
    archive.extractall(destination)


def candidates(root: Path) -> list[Path]:
    return sorted(
        path
        for path in root.rglob("*")
        if path.is_file()
        and path.suffix.lower() in {".tsv", ".csv", ".json", ".yaml", ".yml"}
        and ("manifest" in path.name.lower() or "fixture" in path.name.lower())
    )


def command_inspect(root: Path) -> int:
    vocal_root = root / "vocadito"
    manifests = candidates(root)
    print(f"fixture-link={SAMPLE_LINK}")
    print(f"fixture-root={root}")
    print(f"vocadito-root={vocal_root}")
    print(f"vocadito-present={'yes' if vocal_root.exists() else 'no'}")
    print("fixture-manifests=")
    for path in manifests:
        print(path.relative_to(root))
        with path.open(encoding="utf-8") as manifest:
            for index, line in enumerate(manifest):
                if index == 4:
                    break
                print(f"  {line.rstrip()}")
    if not vocal_root.exists():
        return 0

    audio = sorted(
        path.relative_to(vocal_root)
        for path in vocal_root.rglob("*")
        if path.is_file() and path.suffix.lower() in {".wav", ".flac", ".mp3", ".ogg"}
    )
    annotations = sorted(
        path.relative_to(vocal_root)
        for path in vocal_root.rglob("*")
        if path.is_file() and path.suffix.lower() in {".csv", ".json", ".txt", ".tsv"}
    )
    print(f"vocadito-audio-files={len(audio)}")
    print(f"vocadito-annotation-files={len(annotations)}")
    annotation_groups: dict[str, int] = {}
    for path in annotations:
        group = path.parts[1] if len(path.parts) > 1 else path.parent.name
        annotation_groups[group] = annotation_groups.get(group, 0) + 1
    print("vocadito-annotation-groups=")
    for group, count in sorted(annotation_groups.items()):
        print(f"{group}={count}")
    print("vocadito-audio-preview=")
    for path in audio[:20]:
        print(path)
    print("vocadito-annotation-preview=")
    for path in annotations[:20]:
        print(path)
    note_files = [path for path in annotations if "/Notes/" in f"/{path}"]
    print("vocadito-note-annotation-preview=")
    for path in note_files[:3]:
        print(path)
        with (vocal_root / path).open(encoding="utf-8") as annotation:
            for index, line in enumerate(annotation):
                if index == 4:
                    break
                print(f"  {line.rstrip()}")
    return 0


def command_plan(root: Path) -> int:
    archive = root / "_downloads" / VOCADITO_NAME
    plan = {
        "dataset": "vocadito: solo vocals with f0, note, and lyric annotations",
        "source_url": VOCADITO_URL,
        "archive": str(archive),
        "expected_md5": VOCADITO_MD5,
        "extract_destination": str(root / "vocadito"),
        "audio_is_external_only": True,
        "next_step": "run make apply-vocadito-fixtures, then inspect the extracted annotations before adding manifest entries",
    }
    print(json.dumps(plan, indent=2, sort_keys=True))
    return 0


def command_apply(root: Path) -> int:
    download_directory = root / "_downloads"
    archive = download_directory / VOCADITO_NAME
    destination = root / "vocadito"
    temporary = root / ".vocadito.extract.tmp"

    if destination.exists():
        print(f"vocadito already extracted: {destination}")
        return command_inspect(root)

    download_directory.mkdir(parents=True, exist_ok=True)
    if not archive.exists():
        print(f"downloading={VOCADITO_URL}")
        urllib.request.urlretrieve(VOCADITO_URL, archive)
    actual_md5 = digest(archive)
    if actual_md5 != VOCADITO_MD5:
        raise RuntimeError(
            f"unexpected archive checksum: expected {VOCADITO_MD5}, got {actual_md5}"
        )

    if temporary.exists():
        raise RuntimeError(
            f"stale temporary extraction exists: {temporary}; inspect and remove it before retrying"
        )
    temporary.mkdir()
    try:
        with zipfile.ZipFile(archive) as zip_file:
            safe_extract(zip_file, temporary)
        children = [path for path in temporary.iterdir()]
        source = children[0] if len(children) == 1 and children[0].is_dir() else temporary
        if source is temporary:
            temporary.rename(destination)
        else:
            source.rename(destination)
            temporary.rmdir()
    except Exception:
        shutil.rmtree(temporary, ignore_errors=True)
        raise
    return command_inspect(root)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("inspect", "plan", "apply"))
    args = parser.parse_args()
    root = external_root()
    if args.command == "inspect":
        return command_inspect(root)
    if args.command == "plan":
        return command_plan(root)
    return command_apply(root)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(1)
