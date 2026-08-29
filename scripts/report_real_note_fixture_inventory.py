#!/usr/bin/env python3
"""Summarize externally stored real-note fixtures by their manifest family."""

from collections import Counter
import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1] / "build" / "real_note_samples"
AUDIO_SUFFIXES = {".flac", ".m4a", ".mp3", ".ogg", ".opus", ".wav"}
FAMILIES = ("bass", "guitar", "piano", "vocals", "other", "drums")
CANDIDATE_ROOTS = (
    "idmt_bass_lines_samples",
    "idmt_bass_single_track_fixture",
    "gaps_guitar_samples",
    "idmt_guitar_samples",
    "iowa_piano_samples",
    "maps_piano_samples",
    "tinysol_samples",
)


def fixture_family(path: Path) -> str:
    lower_parts = "/".join(part.lower() for part in path.parts)
    for family in FAMILIES:
        if family in lower_parts:
            return family
    return "unclassified"


def compact_counts(counts: Counter[str], limit: int = 20) -> str:
    ordered = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    shown = ordered[:limit]
    remainder = sum(count for _, count in ordered[limit:])
    rendered = " ".join(f"{name}={count}" for name, count in shown)
    return f"{rendered} remaining={remainder}" if remainder else rendered


def manifest_preview(path: Path) -> str:
    delimiter = "\t" if path.suffix.lower() == ".tsv" else ","
    with path.open(newline="") as handle:
        rows = csv.reader(handle, delimiter=delimiter)
        header = next(rows, [])
        sample = next(rows, [])
    return f"columns={','.join(header)} sample={'|'.join(sample)}"


def main() -> None:
    if not ROOT.is_dir():
        raise SystemExit(f"missing fixture root: {ROOT}")

    all_files = [path for path in ROOT.rglob("*") if path.is_file()]
    files = [path for path in all_files if path.suffix.lower() in AUDIO_SUFFIXES]
    by_family = Counter(fixture_family(path.relative_to(ROOT)) for path in files)
    by_suffix = Counter(path.suffix.lower() or "[none]" for path in all_files)
    by_parent = Counter(path.relative_to(ROOT).parts[0] if path.relative_to(ROOT).parts else "." for path in all_files)

    print(f"root={ROOT.resolve()} external={ROOT.is_symlink()} fixtures={len(files)}")
    print("families=" + " ".join(f"{family}={by_family[family]}" for family in (*FAMILIES, "unclassified")))
    print("file-types=" + " ".join(f"{suffix}={count}" for suffix, count in sorted(by_suffix.items())))
    print("top-level-sources:")
    for parent, count in sorted(by_parent.items(), key=lambda item: (-item[1], item[0])):
        print(f"  {parent}={count}")
    print("audio-examples:")
    for path in sorted(files)[:12]:
        print(f"  {path.relative_to(ROOT)}")

    manifest = ROOT / "manifest.tsv"
    if not manifest.is_file():
        return
    with manifest.open(newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    print("manifest-columns=" + ",".join(rows[0].keys()) if rows else "manifest-columns=[empty]")
    for field in ("family", "instrument", "source", "dataset"):
        counts = Counter(row.get(field, "") for row in rows if row.get(field, ""))
        if counts:
            print(f"manifest-{field}=" + compact_counts(counts))
    print(f"manifest-rows={len(rows)}")
    print("manifest-examples:")
    for row in rows[:5]:
        print("  " + " | ".join(f"{key}={value}" for key, value in row.items()))

    print("candidate-external-sets:")
    build_root = ROOT.parent
    for name in CANDIDATE_ROOTS:
        candidate = build_root / name
        if not candidate.is_dir():
            print(f"  {name}=missing")
            continue
        candidate_files = [path for path in candidate.rglob("*") if path.is_file()]
        candidate_audio = [path for path in candidate_files if path.suffix.lower() in AUDIO_SUFFIXES]
        metadata = [path for path in candidate_files if path.suffix.lower() in {".csv", ".json", ".tsv"}]
        print(f"  {name}=audio:{len(candidate_audio)} metadata:{len(metadata)} external:{candidate.is_symlink()}")
        for path in sorted(metadata)[:2]:
            print(f"    metadata={path.relative_to(candidate)}")
            try:
                print(f"    {manifest_preview(path)}")
            except (OSError, UnicodeDecodeError, csv.Error) as error:
                print(f"    preview-error={error}")


if __name__ == "__main__":
    main()
