#!/usr/bin/env python3
"""Build an external, labeled real-instrument regression manifest.

No audio is copied.  The generated manifest references the already prepared,
external IDMT and Iowa fixture sets through relative paths.
"""

from __future__ import annotations

import argparse
import csv
import os
from collections import Counter
from dataclasses import dataclass
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
BUILD = REPO / "build"
REAL_ROOT = BUILD / "real_note_samples"
EXPANSION_LINK = BUILD / "real_instrument_expansion_samples"
EXPANSION_NAME = "real_instrument_expansion_samples"
HEADER = ("id", "family", "nsynth_family", "source", "midi", "note", "path", "qualities")
@dataclass(frozen=True)
class Fixture:
    identifier: str
    family: str
    source: str
    midi: int
    note: str
    relative_path: str
    qualities: str


@dataclass(frozen=True)
class SourceSelection:
    directory_name: str
    family: str
    source_name: str
    limit: int
    manifest_family: str | None = None
    balance_sources: bool = False


SOURCES = (
    SourceSelection("idmt_bass_lines_samples", "bass", "idmt-bass-lines", 600),
    SourceSelection("idmt_guitar_samples", "guitar", "idmt-guitar", 600),
    SourceSelection("iowa_piano_samples", "piano", "iowa-piano", 120),
    SourceSelection("tinysol_samples", "bass", "tinysol", 300, "bass", True),
    SourceSelection("tinysol_samples", "other", "tinysol", 600, "other", True),
    SourceSelection("tinysol_samples", "piano", "tinysol", 240, "piano", True),
)


def load_manifest(directory: Path, selection: SourceSelection) -> list[Fixture]:
    manifest = directory / "manifest.tsv"
    if not manifest.is_file():
        raise RuntimeError(f"missing manifest: {manifest}")
    fixtures: list[Fixture] = []
    with manifest.open(newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if selection.manifest_family and row.get("family") != selection.manifest_family:
                continue
            try:
                midi = int(row["midi"])
            except (KeyError, ValueError) as error:
                raise RuntimeError(f"invalid MIDI in {manifest}: {row}") from error
            path = directory / row["path"]
            if not path.is_file():
                raise RuntimeError(f"missing labeled audio: {path}")
            fixtures.append(
                Fixture(
                    identifier=row["id"],
                    family=selection.family,
                    source=(f"{selection.source_name}-{row['source']}"
                            if selection.balance_sources else selection.source_name),
                    midi=midi,
                    note=row.get("note", f"midi-{midi}"),
                    relative_path=str(path.resolve()),
                    qualities=row.get("qualities", ""),
                )
            )
    return fixtures


def evenly_select(fixtures: list[Fixture], limit: int) -> list[Fixture]:
    ordered = sorted(fixtures, key=lambda item: (item.midi, item.identifier, item.relative_path))
    if len(ordered) <= limit:
        return ordered
    # Keep pitch and playing-style coverage broad without favoring a recording's
    # filesystem ordering or selecting only the lowest notes.
    positions = [(index * (len(ordered) - 1)) // (limit - 1) for index in range(limit)]
    return [ordered[position] for position in positions]


def evenly_select_by_source(fixtures: list[Fixture], limit: int) -> list[Fixture]:
    grouped: dict[str, list[Fixture]] = {}
    for fixture in fixtures:
        grouped.setdefault(fixture.source, []).append(fixture)
    names = sorted(grouped)
    if not names or len(fixtures) <= limit:
        return sorted(fixtures, key=lambda item: (item.midi, item.identifier, item.relative_path))
    selected: list[Fixture] = []
    base, remainder = divmod(limit, len(names))
    for index, name in enumerate(names):
        quota = base + (1 if index < remainder else 0)
        selected.extend(evenly_select(grouped[name], quota))
    return sorted(selected, key=lambda item: (item.source, item.midi, item.identifier, item.relative_path))


def selected_fixtures() -> list[Fixture]:
    selected: list[Fixture] = []
    for selection in SOURCES:
        fixtures = load_manifest(BUILD / selection.directory_name, selection)
        if selection.balance_sources:
            selected.extend(evenly_select_by_source(fixtures, selection.limit))
        else:
            selected.extend(evenly_select(fixtures, selection.limit))
    return selected


def expansion_root() -> Path:
    if not REAL_ROOT.is_dir():
        raise RuntimeError(f"missing external real-note root: {REAL_ROOT}")
    return REAL_ROOT.resolve().parent / EXPANSION_NAME


def relative_audio_path(root: Path, fixture: Fixture) -> str:
    return os.path.relpath(fixture.relative_path, root)


def render_manifest(root: Path, fixtures: list[Fixture]) -> str:
    rows = ["\t".join(HEADER)]
    for fixture in fixtures:
        row = (
            fixture.identifier,
            fixture.family,
            fixture.family,
            fixture.source,
            str(fixture.midi),
            fixture.note,
            relative_audio_path(root, fixture),
            fixture.qualities,
        )
        rows.append("\t".join(row))
    return "\n".join(rows) + "\n"


def describe(fixtures: list[Fixture]) -> None:
    by_family = Counter(item.family for item in fixtures)
    by_source = Counter(item.source for item in fixtures)
    print(f"fixtures={len(fixtures)}")
    print("families=" + " ".join(f"{name}={count}" for name, count in sorted(by_family.items())))
    print("sources=" + " ".join(f"{name}={count}" for name, count in sorted(by_source.items())))
    for family in sorted(by_family):
        notes = [item.midi for item in fixtures if item.family == family]
        print(f"range-{family}=midi:{min(notes)}-{max(notes)} unique:{len(set(notes))}")


def apply() -> None:
    fixtures = selected_fixtures()
    root = expansion_root()
    content = render_manifest(root, fixtures)
    root.mkdir(parents=True, exist_ok=True)
    manifest = root / "manifest.tsv"
    if not manifest.is_file() or manifest.read_text() != content:
        temporary = root / "manifest.tsv.tmp"
        temporary.write_text(content)
        temporary.replace(manifest)
    if EXPANSION_LINK.exists() or EXPANSION_LINK.is_symlink():
        if not EXPANSION_LINK.is_symlink() or EXPANSION_LINK.resolve() != root:
            raise RuntimeError(f"fixture link already points elsewhere: {EXPANSION_LINK}")
    else:
        EXPANSION_LINK.symlink_to(root)
    print(f"manifest={manifest}")
    print(f"link={EXPANSION_LINK} -> {root}")
    describe(fixtures)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("plan", "apply"))
    mode = parser.parse_args().mode
    fixtures = selected_fixtures()
    if mode == "plan":
        print(f"external-root={expansion_root()}")
        print(f"link={EXPANSION_LINK}")
        describe(fixtures)
        return
    apply()


if __name__ == "__main__":
    main()
