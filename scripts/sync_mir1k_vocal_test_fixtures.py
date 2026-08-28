#!/usr/bin/env python3
"""Plan or apply the curated MIR-1K clean-vocal fixture copy."""

from __future__ import annotations

import argparse
import hashlib
import pathlib
import shutil


SOURCE = pathlib.Path("build/mir1k_vocal_fixtures/clean_vocals")
DESTINATION = pathlib.Path("tests/fixtures/mir1k_clean_vocals")
PLAN = pathlib.Path("build/mir1k_vocal_fixtures/clean_vocal_fixture_plan.tsv")


def digest(path: pathlib.Path) -> str:
    checksum = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            checksum.update(chunk)
    return checksum.hexdigest()


def source_files() -> list[pathlib.Path]:
    manifest = SOURCE / "manifest.tsv"
    if not manifest.is_file():
        raise SystemExit("generated MIR-1K fixtures are missing; run make prepare-mir1k-vocal-fixtures first")
    paths = [manifest]
    for line in manifest.read_text(encoding="utf-8").splitlines()[1:]:
        fields = line.split("\t")
        if len(fields) < 7:
            continue
        path = SOURCE / fields[6]
        if not path.is_file():
            raise SystemExit(f"fixture manifest references missing audio: {path}")
        paths.append(path)
    return paths


def write_plan(files: list[pathlib.Path]) -> None:
    PLAN.parent.mkdir(parents=True, exist_ok=True)
    rows = ["source\tdestination\tbytes\tsha256"]
    for path in files:
        relative = path.relative_to(SOURCE)
        rows.append(f"{path}\t{DESTINATION / relative}\t{path.stat().st_size}\t{digest(path)}")
    PLAN.write_text("\n".join(rows) + "\n", encoding="utf-8")
    print(f"plan: {PLAN}")
    print(f"files: {len(files)}")
    print(f"bytes: {sum(path.stat().st_size for path in files)}")


def apply(files: list[pathlib.Path]) -> None:
    write_plan(files)
    for path in files:
        relative = path.relative_to(SOURCE)
        destination = DESTINATION / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, destination)
    print(f"applied fixture files: {len(files)}")
    print(f"destination: {DESTINATION}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("plan", "apply"))
    args = parser.parse_args()
    files = source_files()
    if args.mode == "plan":
        write_plan(files)
    else:
        apply(files)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
