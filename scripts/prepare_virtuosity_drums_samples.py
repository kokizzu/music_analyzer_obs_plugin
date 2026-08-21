#!/usr/bin/env python3
"""Create a bounded labelled acoustic Tom/Ride/Rim fixture from Virtuosity Drums.

The upstream CC0 library ships each articulation through several microphone
channels.  This fixture uses the named overhead channel only, so different
microphones of one performed hit never inflate accuracy evidence.
"""
from __future__ import annotations

import argparse
import csv
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path


EXPECTED_COMMIT = "9f04cf9a734527edfbb0a4eee1f674e45bbf71bc"
CATEGORIES = ("rim", "tom", "ride")


@dataclass(frozen=True)
class Candidate:
    category: str
    source: Path


def classify(path: Path) -> str | None:
    """Return the declared articulation category for one overhead FLAC."""
    parts = path.parts
    if len(parts) < 3 or parts[-3] != "oh" or path.suffix.lower() != ".flac":
        return None
    name = path.name.lower()
    instrument = path.parent.name.lower()
    if instrument == "snare" and ("_rimshot_" in name or "_crossstick_" in name):
        return "rim"
    if instrument in {"htom", "ltom"} and ("_center_" in name or "_offcenter_" in name):
        return "tom"
    if instrument == "ride" and ("_ride_" in name or "_bell_" in name):
        return "ride"
    return None


def discover(source: Path, limit_per_category: int) -> list[Candidate]:
    candidates = {category: [] for category in CATEGORIES}
    overhead = source / "Samples" / "oh"
    for path in sorted(overhead.rglob("*.flac")):
        category = classify(path.relative_to(source))
        if category is not None:
            candidates[category].append(Candidate(category, path))
    selected: list[Candidate] = []
    for category in CATEGORIES:
        rows = candidates[category]
        if limit_per_category > 0:
            rows = rows[:limit_per_category]
        selected.extend(rows)
    return selected


def source_commit(source: Path) -> str:
    result = subprocess.run(
        ["git", "-C", str(source), "rev-parse", "HEAD"],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return result.stdout.strip()


def existing_counts(output: Path, expected_commit: str) -> dict[str, int] | None:
    manifest = output / "manifest.tsv"
    if not manifest.is_file():
        return None
    rows = list(csv.DictReader(manifest.open(encoding="utf-8"), delimiter="\t"))
    if not rows or any(row.get("source_commit") != expected_commit for row in rows):
        return None
    counts = {category: 0 for category in CATEGORIES}
    for row in rows:
        category = row.get("category", "")
        path = output / row.get("path", "")
        if category not in counts or not path.is_file():
            return None
        counts[category] += 1
    return counts


def convert(ffmpeg: str, source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [ffmpeg, "-nostdin", "-hide_banner", "-loglevel", "error", "-y", "-i", str(source),
         "-ac", "1", "-ar", "48000", "-c:a", "pcm_s16le", str(destination)],
        check=True,
    )


def prepare(source: Path, output: Path, ffmpeg: str, limit_per_category: int,
            min_per_category: int) -> dict[str, int]:
    commit = source_commit(source)
    if commit != EXPECTED_COMMIT:
        raise ValueError(f"{source}: expected pinned commit {EXPECTED_COMMIT}, got {commit}")
    if not (source / "LICENSE").read_text(encoding="utf-8").startswith("Creative Commons Legal Code\n\nCC0 1.0 Universal"):
        raise ValueError(f"{source}: missing expected CC0-1.0 licence")
    previous = existing_counts(output, commit)
    if previous is not None and all(previous[category] >= min_per_category for category in CATEGORIES):
        return previous
    if output.exists() and any(output.iterdir()):
        raise ValueError(f"{output}: refuses to replace an incomplete or mismatched generated fixture")

    selected = discover(source, limit_per_category)
    counts = {category: 0 for category in CATEGORIES}
    for row in selected:
        counts[row.category] += 1
    missing = [f"{category}={counts[category]}" for category in CATEGORIES if counts[category] < min_per_category]
    if missing:
        raise ValueError("insufficient declared Virtuosity articulations: " + ", ".join(missing))

    output.mkdir(parents=True, exist_ok=True)
    manifest_rows: list[dict[str, str]] = []
    per_category = {category: 0 for category in CATEGORIES}
    for candidate in selected:
        per_category[candidate.category] += 1
        relative = Path(candidate.category) / f"{per_category[candidate.category]:03d}_{candidate.source.stem}.wav"
        convert(ffmpeg, candidate.source, output / relative)
        manifest_rows.append({
            "category": candidate.category,
            "path": str(relative),
            "source": str(candidate.source.relative_to(source)),
            "source_commit": commit,
        })
    manifest = output / "manifest.tsv"
    with manifest.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=("category", "path", "source", "source_commit"), delimiter="\t")
        writer.writeheader()
        writer.writerows(manifest_rows)
    return counts


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--ffmpeg", default="ffmpeg")
    parser.add_argument("--limit-per-category", type=int, default=48)
    parser.add_argument("--min-per-category", type=int, default=20)
    args = parser.parse_args()
    counts = prepare(args.source, args.output, args.ffmpeg, args.limit_per_category, args.min_per_category)
    summary = " ".join(f"{category}={counts[category]}" for category in CATEGORIES)
    print(f"prepare_virtuosity_drums_samples: {args.output}/manifest.tsv ({summary})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
