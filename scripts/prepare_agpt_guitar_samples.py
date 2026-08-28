#!/usr/bin/env python3
"""Prepare bounded, labelled AG-PT monophonic notes for real-note evaluation."""

from __future__ import annotations

import argparse
import csv
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import sys
from collections import defaultdict, deque


MANIFEST_HEADER = ["id", "family", "nsynth_family", "source", "midi", "note", "path", "signature"]
GUITAR_RANGE = (40, 88)
FIXTURE_VERSION = "agpt-guitar-v1"


def note_name(midi: int) -> str:
    names = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")
    return f"{names[midi % 12]}{midi // 12 - 1}"


def sanitize(value: str) -> str:
    return "".join(char if char.isalnum() else "_" for char in value).strip("_") or "unknown"


def parse_midi(value: str) -> int | None:
    try:
        midi = int(round(float(value)))
    except (TypeError, ValueError):
        return None
    return midi if GUITAR_RANGE[0] <= midi <= GUITAR_RANGE[1] else None


def locate_metadata(source_root: Path, filename: str) -> Path:
    matches = sorted(source_root.rglob(filename))
    if len(matches) != 1:
        raise ValueError(f"expected exactly one {filename} beneath {source_root}, found {matches}")
    return matches[0]


def source_signature(note_labels: Path, args: argparse.Namespace) -> str:
    stat = note_labels.stat()
    payload = "|".join((
        FIXTURE_VERSION,
        f"{note_labels}:{stat.st_size}:{int(stat.st_mtime)}",
        f"limit={args.limit}",
        f"clip={args.clip_seconds:.3f}",
        f"attack={args.attack_margin:.3f}",
        f"gap={args.next_note_gap:.3f}",
    ))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def manifest_complete(path: Path, signature: str, minimum: int) -> bool:
    if not path.is_file():
        return False
    rows = 0
    with path.open(encoding="utf-8", newline="") as source:
        reader = csv.reader(source, delimiter="\t")
        if next(reader, None) != MANIFEST_HEADER:
            return False
        for fields in reader:
            if len(fields) != len(MANIFEST_HEADER) or fields[-1] != signature:
                return False
            if not (path.parent / fields[6]).is_file():
                return False
            rows += 1
    return rows >= minimum


def resolve_audio(data_root: Path, source_root: Path, label: str) -> Path | None:
    relative = Path(label.lstrip("./"))
    for candidate in (
        data_root / relative,
        source_root / relative,
        data_root / "audio" / relative.name,
        data_root / "data" / "audio" / relative.name,
    ):
        if candidate.is_file():
            return candidate
    return None


def collect_candidates(source_root: Path, args: argparse.Namespace) -> tuple[list[dict[str, object]], dict[str, int], Path]:
    note_labels = locate_metadata(source_root, "note_labels.csv")
    data_root = note_labels.parent.parent
    skipped: dict[str, int] = defaultdict(int)
    grouped: dict[Path, list[dict[str, object]]] = defaultdict(list)
    with note_labels.open(encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source)
        required = {"onset_label_seconds", "audio_file_path", "pitch_midi", "expressive_technique_id"}
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise ValueError("AG-PT note_labels.csv lacks required onset/audio/pitch/technique columns")
        for index, row in enumerate(reader, start=1):
            midi = parse_midi(row.get("pitch_midi", ""))
            if midi is None:
                skipped["unpitched_or_outside_range"] += 1
                continue
            try:
                onset = float(row["onset_label_seconds"])
            except (TypeError, ValueError):
                skipped["invalid_onset"] += 1
                continue
            audio = resolve_audio(data_root, source_root, row.get("audio_file_path", ""))
            if audio is None:
                skipped["missing_audio"] += 1
                continue
            technique = sanitize(row.get("expressive_technique_id", "unknown"))
            grouped[audio].append({"index": index, "midi": midi, "onset": onset, "audio": audio, "technique": technique})

    candidates: list[dict[str, object]] = []
    for audio, notes in grouped.items():
        notes.sort(key=lambda row: float(row["onset"]))
        for position, row in enumerate(notes):
            start = max(0.0, float(row["onset"]) + args.attack_margin)
            duration = args.clip_seconds
            if position + 1 < len(notes):
                duration = min(duration, float(notes[position + 1]["onset"]) - start - args.next_note_gap)
            if duration <= 0.06:
                skipped["too_close_to_next_note"] += 1
                continue
            midi = int(row["midi"])
            technique = str(row["technique"])
            row_id = sanitize(f"agpt_guitar_{technique}_{audio.stem}_{int(row['index']):05d}_{note_name(midi)}")
            candidates.append({
                **row,
                "id": row_id,
                "source": f"agpt-guitar-{technique}",
                "note": note_name(midi),
                "path": Path("audio") / f"{row_id}.wav",
                "start": start,
                "duration": duration,
            })
    candidates.sort(key=lambda row: (int(row["midi"]), str(row["technique"]), str(row["audio"]), int(row["index"])))
    return candidates, dict(skipped), note_labels


def balanced_limit(rows: list[dict[str, object]], limit: int) -> list[dict[str, object]]:
    if limit <= 0 or len(rows) <= limit:
        return rows
    buckets: dict[tuple[str, int], deque[dict[str, object]]] = defaultdict(deque)
    for row in rows:
        buckets[(str(row["technique"]), int(row["midi"]))].append(row)
    selected: list[dict[str, object]] = []
    keys = sorted(buckets)
    while len(selected) < limit:
        made_progress = False
        for key in keys:
            if buckets[key]:
                selected.append(buckets[key].popleft())
                made_progress = True
                if len(selected) >= limit:
                    break
        if not made_progress:
            break
    return selected


def convert_clip(ffmpeg: str, source: Path, destination: Path, start: float, duration: float) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [ffmpeg, "-nostdin", "-v", "error", "-y", "-ss", f"{start:.6f}", "-t", f"{duration:.6f}", "-i", str(source), "-ac", "1", "-ar", "48000", str(destination)],
        check=True,
    )


def write_manifest(path: Path, rows: list[dict[str, object]], signature: str) -> None:
    with path.open("w", encoding="utf-8", newline="") as output:
        writer = csv.writer(output, delimiter="\t", lineterminator="\n")
        writer.writerow(MANIFEST_HEADER)
        for row in rows:
            writer.writerow((row["id"], "guitar", "agpt_acoustic_guitar", row["source"], row["midi"], row["note"], row["path"], signature))


def prepare(args: argparse.Namespace) -> None:
    source_root = Path(args.source)
    output = Path(args.output)
    candidates, skipped, note_labels = collect_candidates(source_root, args)
    signature = source_signature(note_labels, args)
    manifest = output / "manifest.tsv"
    if not args.refresh and manifest_complete(manifest, signature, args.min_samples):
        print(f"prepare_agpt_guitar_samples: keeping existing {manifest}")
        return
    ffmpeg = shutil.which(args.ffmpeg)
    if not ffmpeg:
        raise SystemExit(f"prepare_agpt_guitar_samples: cannot find ffmpeg command {args.ffmpeg}")
    selected = balanced_limit(candidates, args.limit)
    rows: list[dict[str, object]] = []
    failures: list[str] = []
    for row in selected:
        try:
            convert_clip(ffmpeg, Path(row["audio"]), output / Path(row["path"]), float(row["start"]), float(row["duration"]))
        except (OSError, subprocess.CalledProcessError) as exc:
            failures.append(f"{row['id']}: {exc}")
            continue
        rows.append(row)
    if len(rows) < args.min_samples:
        partial = manifest.with_suffix(".tsv.partial")
        output.mkdir(parents=True, exist_ok=True)
        write_manifest(partial, rows, signature)
        raise SystemExit(f"prepare_agpt_guitar_samples: expected {args.min_samples} rows, prepared {len(rows)}; partial={partial}")
    output.mkdir(parents=True, exist_ok=True)
    write_manifest(manifest, rows, signature)
    print(f"prepare_agpt_guitar_samples: wrote {len(rows)} rows (candidates={len(candidates)} skipped={dict(sorted(skipped.items()))} failures={len(failures)})")
    for failure in failures[:12]:
        print(f"prepare_agpt_guitar_samples: {failure}", file=sys.stderr)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--limit", type=int, default=2000)
    parser.add_argument("--min-samples", type=int, default=1000)
    parser.add_argument("--clip-seconds", type=float, default=0.32)
    parser.add_argument("--attack-margin", type=float, default=0.03)
    parser.add_argument("--next-note-gap", type=float, default=0.02)
    parser.add_argument("--ffmpeg", default=os.environ.get("FFMPEG", "ffmpeg"))
    parser.add_argument("--refresh", action="store_true")
    args = parser.parse_args()
    prepare(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
