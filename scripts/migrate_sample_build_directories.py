#!/usr/bin/env python3
"""Move build sample/corpus directories into an external store and symlink them back."""

from __future__ import annotations

import argparse
import fnmatch
import os
from pathlib import Path
import shutil
import sys
import uuid


SAMPLE_DIRECTORY_NAMES = {
    "guitarset",
    "real_note_samples",
    "real_sample_sources",
}
SAMPLE_DIRECTORY_PATTERNS = (
    "*_samples",
    "*_samples_*",
    "*-fixture",
    "*-fixture-*",
    "*-musicnet-fixture",
)


def is_sample_directory(path: Path) -> bool:
    return path.name in SAMPLE_DIRECTORY_NAMES or any(
        fnmatch.fnmatch(path.name, pattern) for pattern in SAMPLE_DIRECTORY_PATTERNS
    )


def resolve_link(path: Path) -> Path:
    target = Path(os.readlink(path))
    return target if target.is_absolute() else (path.parent / target).resolve()


def file_size(path: Path) -> int:
    return sum(entry.stat().st_size for entry in path.rglob("*") if entry.is_file())


def candidates(build: Path) -> list[Path]:
    return sorted(
        (
            path
            for path in build.iterdir()
            if path.is_dir() and not path.is_symlink() and is_sample_directory(path)
        ),
        key=lambda path: path.name,
    )


def describe(build: Path, store: Path) -> int:
    sample_paths = candidates(build)
    print(f"sample_build_migration: build={build} store={store}")
    for path in sample_paths:
        destination = store / "build-cache" / path.name
        print(
            "sample_build_migration: candidate="
            f"{path} bytes={file_size(path)} destination={destination}"
        )
    return 0


def migrate_one(source: Path, destination: Path) -> None:
    if destination.exists() or destination.is_symlink():
        raise RuntimeError(f"refusing to overwrite external destination {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(f".{destination.name}.migrating-{uuid.uuid4().hex}")
    source_bytes = file_size(source)
    try:
        shutil.copytree(source, temporary, copy_function=shutil.copy2)
        copied_bytes = file_size(temporary)
        if copied_bytes != source_bytes:
            raise RuntimeError(
                f"copied size mismatch for {source}: source={source_bytes} copied={copied_bytes}"
            )
        temporary.rename(destination)
        shutil.rmtree(source)
        source.symlink_to(destination, target_is_directory=True)
    except Exception:
        if temporary.exists():
            shutil.rmtree(temporary)
        raise
    print(f"sample_build_migration: migrated={source} bytes={source_bytes} target={destination}")


def migrate(build: Path, store: Path) -> int:
    if not store.is_dir():
        print(f"sample_build_migration: external store is unavailable: {store}", file=sys.stderr)
        return 1
    for source in candidates(build):
        migrate_one(source, store / "build-cache" / source.name)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", required=True, type=Path)
    parser.add_argument("--store", required=True, type=Path)
    parser.add_argument("--status", action="store_true")
    args = parser.parse_args()
    build = args.build.resolve()
    store = args.store.resolve()
    if not build.is_dir():
        print(f"sample_build_migration: build directory is unavailable: {build}", file=sys.stderr)
        return 1
    return describe(build, store) if args.status else migrate(build, store)


if __name__ == "__main__":
    raise SystemExit(main())
