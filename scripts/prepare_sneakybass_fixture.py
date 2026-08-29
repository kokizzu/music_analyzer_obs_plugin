#!/usr/bin/env python3
"""Stage a real, labelled CC0 Sneakybass fixture outside the repository."""

from __future__ import annotations

import argparse
import csv
import re
import shutil
import sys
import tempfile
import urllib.error
import urllib.request
import zipfile
from pathlib import Path


SOURCE_URL = "https://github.com/sfzinstruments/karoryfer.sneakybass/archive/refs/heads/master.zip"
SOURCE_PAGE = "https://github.com/sfzinstruments/karoryfer.sneakybass"
FIXTURE_NAME = "sneakybass"
PROGRAM_NAME = "sneakybass_double_bass_pizzicato"
MANIFEST_HEADER = [
    "family",
    "program",
    "program_name",
    "midi",
    "path",
    "note",
    "soundfont",
    "signature",
]
TOKEN = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)=(\"[^\"]*\"|[^\s]+)")
NOTE = re.compile(r"^([A-Ga-g])([#b]?)(-?\d+)$")


def note_to_midi(value: str) -> int | None:
    value = value.strip().replace("\"", "")
    if value.lstrip("-").isdigit():
        return int(value)
    match = NOTE.match(value)
    if not match:
        return None
    semitone = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}[match.group(1).upper()]
    if match.group(2) == "#":
        semitone += 1
    elif match.group(2) == "b":
        semitone -= 1
    return (int(match.group(3)) + 1) * 12 + semitone


def midi_name(midi: int) -> str:
    return ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")[midi % 12] + str(midi // 12 - 1)


def parse_sfz(path: Path, samples_by_name: dict[str, Path]) -> list[tuple[Path, int]]:
    """Extract exact attack sample/key pairs from practical SFZ region mappings."""
    inherited: dict[str, str] = {}
    region: dict[str, str] | None = None
    result: list[tuple[Path, int]] = []

    def finalize() -> None:
        nonlocal region
        if not region or "sample" not in region:
            return
        midi = note_to_midi(region.get("key", region.get("pitch_keycenter", "")))
        if midi is None or midi < 0 or midi > 127:
            return
        default_path = region.get("default_path", "").replace("\\", "/")
        sample = region["sample"].replace("\\", "/")
        candidate = (path.parent / default_path / sample).resolve()
        if not candidate.is_file():
            candidate = samples_by_name.get(Path(sample).name.lower(), candidate)
        if candidate.suffix.lower() == ".wav" and candidate.is_file():
            result.append((candidate, midi))

    for raw_line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw_line.split("//", 1)[0].strip()
        if not line:
            continue
        headers = re.findall(r"<([^>]+)>", line)
        for header in headers:
            header = header.lower()
            if header == "region":
                finalize()
                region = dict(inherited)
            elif header in {"control", "global", "master", "group"}:
                if region is not None:
                    finalize()
                    region = None
        values = {key.lower(): value.strip().strip('"') for key, value in TOKEN.findall(line)}
        if not values:
            continue
        if region is None:
            inherited.update(values)
        else:
            region.update(values)
    finalize()
    return result


def fixture_paths(store: Path) -> tuple[Path, Path, Path]:
    source_dir = store / "sources" / FIXTURE_NAME
    fixture_dir = store / "real-fixtures" / FIXTURE_NAME
    return source_dir, fixture_dir, source_dir / f"{FIXTURE_NAME}.zip"


def print_plan(store: Path, minimum_samples: int) -> None:
    source_dir, fixture_dir, archive = fixture_paths(store)
    print(f"store={store}")
    print(f"source_url={SOURCE_URL}")
    print(f"source_page={SOURCE_PAGE}")
    print("license=CC0-1.0")
    print(f"archive={archive}")
    print(f"fixture={fixture_dir}")
    print(f"minimum_samples={minimum_samples}")
    print("repository_write=false")
    print("downloaded_audio_location=external_store")


def download(url: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(destination.suffix + ".part")
    if temporary.is_file() and zipfile.is_zipfile(temporary):
        temporary.replace(destination)
        return
    offset = temporary.stat().st_size if temporary.is_file() else 0
    headers = {"User-Agent": "music-analyzer-fixture-importer/1"}
    if offset:
        headers["Range"] = f"bytes={offset}-"
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=90) as response:
        if offset and response.status != 206:
            raise RuntimeError(
                f"server did not resume partial archive at byte {offset}; preserving {temporary}"
            )
        mode = "ab" if offset else "wb"
        with temporary.open(mode) as output:
            shutil.copyfileobj(response, output)
    temporary.replace(destination)


def extract(archive: Path, source_dir: Path) -> Path:
    if source_dir.is_dir() and any(source_dir.rglob("*.sfz")):
        return source_dir
    with tempfile.TemporaryDirectory(prefix="sneakybass-", dir=source_dir.parent) as temporary:
        temporary_path = Path(temporary)
        with zipfile.ZipFile(archive) as payload:
            payload.extractall(temporary_path)
        roots = [entry for entry in temporary_path.iterdir() if entry.is_dir()]
        if len(roots) != 1:
            raise RuntimeError("expected one top-level directory in Sneakybass archive")
        staged = roots[0]
        if source_dir.exists():
            shutil.rmtree(source_dir)
        staged.replace(source_dir)
    return source_dir


def write_manifest(source_dir: Path, fixture_dir: Path, minimum_samples: int) -> int:
    samples_by_name: dict[str, Path] = {}
    for sample in source_dir.rglob("*.wav"):
        key = sample.name.lower()
        if key in samples_by_name:
            raise RuntimeError(f"ambiguous Sneakybass sample basename: {sample.name}")
        samples_by_name[key] = sample.resolve()
    mappings: dict[tuple[Path, int], None] = {}
    for sfz in sorted(source_dir.rglob("*.sfz")):
        for sample, midi in parse_sfz(sfz, samples_by_name):
            mappings[(sample, midi)] = None
    rows = sorted(mappings, key=lambda item: (item[1], str(item[0])))
    if len(rows) < minimum_samples:
        raise RuntimeError(f"only found {len(rows)} labelled WAV mappings; need at least {minimum_samples}")
    fixture_dir.mkdir(parents=True, exist_ok=True)
    source_link = fixture_dir / "source"
    if source_link.exists() or source_link.is_symlink():
        if not source_link.is_symlink() or source_link.resolve() != source_dir.resolve():
            raise RuntimeError(f"fixture source link has an unexpected target: {source_link}")
    else:
        source_link.symlink_to(source_dir, target_is_directory=True)
    manifest = fixture_dir / "manifest.tsv"
    with manifest.open("w", encoding="utf-8", newline="") as output:
        writer = csv.writer(output, delimiter="\t", lineterminator="\n")
        writer.writerow(MANIFEST_HEADER)
        for sample, midi in rows:
            writer.writerow(
                [
                    "bass",
                    "0",
                    PROGRAM_NAME,
                    str(midi),
                    str(Path("source") / sample.relative_to(source_dir)),
                    midi_name(midi),
                    SOURCE_PAGE,
                    "cc0-1.0",
                ]
            )
    provenance = fixture_dir / "PROVENANCE.tsv"
    provenance.write_text(
        "fixture\tsource\tlicense\tformat\tmappings\n"
        f"{FIXTURE_NAME}\t{SOURCE_PAGE}\tCC0-1.0\twav\t{len(rows)}\n",
        encoding="utf-8",
    )
    return len(rows)


def verify(store: Path, minimum_samples: int) -> int:
    source_dir, fixture_dir, _ = fixture_paths(store)
    manifest = fixture_dir / "manifest.tsv"
    if not manifest.is_file():
        raise RuntimeError(f"missing fixture manifest: {manifest}")
    with manifest.open(encoding="utf-8", newline="") as input_file:
        rows = list(csv.DictReader(input_file, delimiter="\t"))
    if len(rows) < minimum_samples:
        raise RuntimeError(f"fixture has {len(rows)} samples; need at least {minimum_samples}")
    for row in rows:
        if row["family"] != "bass":
            raise RuntimeError(f"unexpected family in manifest: {row['family']}")
        sample = fixture_dir / row["path"]
        if not sample.is_file():
            raise RuntimeError(f"missing manifest sample: {sample}")
        if source_dir not in sample.resolve().parents:
            raise RuntimeError(f"sample escapes source directory: {sample}")
    print(f"prepare_sneakybass_fixture: verified {len(rows)} external real bass samples")
    return len(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("plan", "apply", "verify"))
    parser.add_argument("--store", required=True, type=Path)
    parser.add_argument("--minimum-samples", type=int, default=100)
    args = parser.parse_args()
    if args.minimum_samples < 1:
        raise SystemExit("--minimum-samples must be positive")
    store = args.store.resolve()
    if args.action == "plan":
        print_plan(store, args.minimum_samples)
        return 0
    if args.action == "apply":
        _, _, archive = fixture_paths(store)
        if not archive.is_file():
            print(f"prepare_sneakybass_fixture: downloading {SOURCE_URL}")
            download(SOURCE_URL, archive)
        source_dir, fixture_dir, _ = fixture_paths(store)
        extract(archive, source_dir)
        count = write_manifest(source_dir, fixture_dir, args.minimum_samples)
        print(f"prepare_sneakybass_fixture: prepared {count} external real bass samples")
    verify(store, args.minimum_samples)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, RuntimeError, urllib.error.URLError, zipfile.BadZipFile) as error:
        print(f"prepare_sneakybass_fixture: {error}", file=sys.stderr)
        raise SystemExit(1)
