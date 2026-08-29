#!/usr/bin/env python3
"""Plan and apply a labeled VocalSet/Vocadito expansion of the real-note fixture."""

from __future__ import annotations

import csv
import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STORE = (ROOT / "build" / "InstrumentSamples").resolve()
FIXTURE = (ROOT / "build" / "real_note_samples").resolve()
PLAN = ROOT / "build" / "real_note_vocal_fixture_plan.tsv"
SOURCES = (
    ("vocalset_samples", 96),
    ("vocadito_samples", 96),
)


def qualities_float(row: dict[str, str], key: str) -> float | None:
    for item in row.get("qualities", "").split(","):
        name, separator, value = item.partition("=")
        if separator and name == key:
            try:
                return float(value)
            except ValueError:
                return None
    return None


def eligible_rows(dataset: str, quota: int, existing_ids: set[str]) -> list[dict[str, str]]:
    manifest = STORE / dataset / "manifest.tsv"
    with manifest.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    usable = [
        row
        for row in rows
        if row.get("id") not in existing_ids
        and row.get("family") == "vocals"
        and (cents := qualities_float(row, "cents")) is not None
        and abs(cents) <= 9.0
        and (duration := qualities_float(row, "duration")) is not None
        and duration >= 0.40
        and (STORE / dataset / row["path"]).is_file()
    ]
    usable.sort(key=lambda row: (int(row["midi"]), row.get("source", ""), row["id"]))
    if len(usable) <= quota:
        return usable
    return [usable[index * len(usable) // quota] for index in range(quota)]


def build_plan() -> list[dict[str, str]]:
    with (FIXTURE / "manifest.tsv").open(encoding="utf-8", newline="") as stream:
        existing = list(csv.DictReader(stream, delimiter="\t"))
    existing_ids = {row["id"] for row in existing}
    selected: list[dict[str, str]] = []
    for dataset, quota in SOURCES:
        for row in eligible_rows(dataset, quota, existing_ids):
            source = STORE / dataset / row["path"]
            destination = FIXTURE / "audio" / "vocals" / f"{row['id']}.wav"
            selected.append({
                "id": row["id"],
                "family": "vocals",
                "nsynth_family": "vocal",
                "source": row["source"],
                "midi": row["midi"],
                "note": row["note"],
                "path": str(destination.relative_to(FIXTURE)),
                "qualities": row["qualities"],
                "source_path": str(source),
            })
    selected.sort(key=lambda row: (int(row["midi"]), row["source"], row["id"]))
    return selected


def write_plan(rows: list[dict[str, str]]) -> None:
    PLAN.parent.mkdir(parents=True, exist_ok=True)
    with PLAN.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=(
            "id", "family", "nsynth_family", "source", "midi", "note", "path", "qualities", "source_path",
        ), delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def print_plan(rows: list[dict[str, str]]) -> None:
    print(f"fixture={FIXTURE}")
    print(f"plan={PLAN}")
    print(f"selected={len(rows)}")
    for row in rows:
        print(f"link {row['source_path']} -> {FIXTURE / row['path']}")


def apply_plan() -> None:
    if not PLAN.is_file():
        raise SystemExit("missing plan; run make plan-real-note-vocal-fixture first")
    with PLAN.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    manifest = FIXTURE / "manifest.tsv"
    with manifest.open(encoding="utf-8", newline="") as stream:
        existing = list(csv.DictReader(stream, delimiter="\t"))
    existing_ids = {row["id"] for row in existing}
    additions = [row for row in rows if row["id"] not in existing_ids]
    for row in additions:
        source = Path(row["source_path"])
        destination = FIXTURE / row["path"]
        if not source.is_file():
            raise SystemExit(f"missing planned source: {source}")
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists() or destination.is_symlink():
            if destination.resolve() != source.resolve():
                raise SystemExit(f"destination already differs: {destination}")
        else:
            destination.symlink_to(source)
    if not additions:
        print("applied=0 already-present")
        return
    backup = manifest.with_suffix(".tsv.before-vocal-expansion")
    if not backup.exists():
        backup.write_bytes(manifest.read_bytes())
    fields = ("id", "family", "nsynth_family", "source", "midi", "note", "path", "qualities")
    with manifest.open("a", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, delimiter="\t", extrasaction="ignore")
        writer.writerows(additions)
    print(f"applied={len(additions)} backup={backup}")


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in {"plan", "apply"}:
        raise SystemExit("usage: manage_real_note_vocal_fixture.py plan|apply")
    if sys.argv[1] == "plan":
        rows = build_plan()
        write_plan(rows)
        print_plan(rows)
    else:
        apply_plan()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
