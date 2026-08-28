#!/usr/bin/env python3
"""Preview or remove only reviewed stale MIR-1K fixture audio files."""

from __future__ import annotations

import argparse
import hashlib
import pathlib


DESTINATION = pathlib.Path("tests/fixtures/mir1k_clean_vocals")
PLAN = pathlib.Path("build/mir1k_vocal_fixtures/stale_clean_vocal_fixture_plan.tsv")


def digest(path: pathlib.Path) -> str:
    checksum = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            checksum.update(chunk)
    return checksum.hexdigest()


def expected_paths() -> set[pathlib.Path]:
    manifest = DESTINATION / "manifest.tsv"
    if not manifest.is_file():
        raise SystemExit("destination manifest is missing")
    paths = {manifest.resolve()}
    for line in manifest.read_text(encoding="utf-8").splitlines()[1:]:
        fields = line.split("\t")
        if len(fields) >= 7:
            paths.add((DESTINATION / fields[6]).resolve())
    return paths


def plan() -> None:
    expected = expected_paths()
    stale = sorted(path for path in (DESTINATION / "audio").glob("*.wav") if path.resolve() not in expected)
    PLAN.parent.mkdir(parents=True, exist_ok=True)
    rows = ["path\tbytes\tsha256"]
    rows.extend(f"{path}\t{path.stat().st_size}\t{digest(path)}" for path in stale)
    PLAN.write_text("\n".join(rows) + "\n", encoding="utf-8")
    print(f"plan: {PLAN}")
    if stale:
        for path in stale:
            print(f"stale: {path} bytes={path.stat().st_size}")
    else:
        print("stale files: none")


def apply() -> None:
    if not PLAN.is_file():
        raise SystemExit("stale plan is missing; run the plan target and inspect it first")
    destination = DESTINATION.resolve()
    rows = PLAN.read_text(encoding="utf-8").splitlines()[1:]
    removed = 0
    for row in rows:
        fields = row.split("\t")
        if len(fields) != 3:
            raise SystemExit(f"invalid stale plan row: {row}")
        path = pathlib.Path(fields[0]).resolve()
        if destination not in path.parents or not path.is_file() or digest(path) != fields[2]:
            raise SystemExit(f"stale plan no longer matches: {path}")
        path.unlink()
        removed += 1
    print(f"removed reviewed stale files: {removed}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("plan", "apply"))
    mode = parser.parse_args().mode
    if mode == "plan":
        plan()
    else:
        apply()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
