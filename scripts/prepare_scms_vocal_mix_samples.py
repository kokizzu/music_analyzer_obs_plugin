#!/usr/bin/env python3
"""Prepare stable, labelled SCMS vocal-plus-accompaniment probe clips."""

from __future__ import annotations

import argparse
import csv
import math
import statistics
import wave
from pathlib import Path


FIXTURE_VERSION = "scms-v1"


def note_name(midi: int) -> str:
    names = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")
    return f"{names[midi % 12]}{midi // 12 - 1}"


def midi_from_hz(value: float) -> int | None:
    if not math.isfinite(value) or value <= 0.0:
        return None
    return int(round(69.0 + 12.0 * math.log2(value / 440.0)))


def pitch_points(path: Path) -> list[tuple[float, float]]:
    points: list[tuple[float, float]] = []
    with path.open(newline="", encoding="utf-8", errors="replace") as source:
        for number, row in enumerate(csv.reader(source), start=1):
            if len(row) < 2:
                raise ValueError(f"{path}:{number}: expected timestamp,Hz")
            try:
                timestamp, frequency = float(row[0]), float(row[1])
            except ValueError as error:
                raise ValueError(f"{path}:{number}: invalid timestamp or Hz") from error
            if not math.isfinite(timestamp) or not math.isfinite(frequency) or timestamp < 0.0:
                raise ValueError(f"{path}:{number}: invalid timestamp or Hz")
            points.append((timestamp, frequency))
    return points


def longest_stable_run(points: list[tuple[float, float]], minimum_frames: int) -> tuple[int, int, int] | None:
    """Find the longest contiguous voiced run with a single rounded MIDI note."""
    best: tuple[int, int, int] | None = None
    start = 0
    current: int | None = None
    for index, (_, frequency) in enumerate(points + [(0.0, 0.0)]):
        midi = midi_from_hz(frequency)
        if midi == current:
            continue
        if current is not None and index - start >= minimum_frames:
            candidate = (start, index, current)
            if best is None or candidate[1] - candidate[0] > best[1] - best[0]:
                best = candidate
        start = index
        current = midi
    return best


def clip_wav(source_path: Path, destination_path: Path, start_seconds: float, duration_seconds: float) -> bool:
    with wave.open(str(source_path), "rb") as source:
        start_frame = max(0, int(round(start_seconds * source.getframerate())))
        frames = max(1, int(round(duration_seconds * source.getframerate())))
        if start_frame >= source.getnframes():
            return False
        source.setpos(start_frame)
        audio = source.readframes(min(frames, source.getnframes() - start_frame))
        params = source.getparams()
    destination_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination_path.with_suffix(destination_path.suffix + ".tmp")
    with wave.open(str(temporary), "wb") as destination:
        destination.setparams(params)
        destination.writeframes(audio)
    temporary.replace(destination_path)
    return True


def audio_by_track(root: Path) -> dict[str, Path]:
    result: dict[str, Path] = {}
    for path in sorted(root.rglob("*.wav")):
        key = path.stem.casefold()
        if key in result:
            raise ValueError(f"duplicate SCMS audio track identifier: {path.stem}")
        result[key] = path
    return result


def candidates(root: Path, minimum_frames: int, clip_seconds: float) -> list[dict[str, object]]:
    audio = audio_by_track(root)
    result: list[dict[str, object]] = []
    for pitch_path in sorted(root.rglob("*.csv")):
        track = pitch_path.stem
        source_path = audio.get(track.casefold())
        if source_path is None:
            continue
        points = pitch_points(pitch_path)
        run = longest_stable_run(points, minimum_frames)
        if run is None:
            continue
        start, end, midi = run
        first_time = points[start][0]
        last_time = points[end - 1][0]
        available = max(0.001, last_time - first_time)
        duration = min(clip_seconds, available)
        center = (first_time + last_time) / 2.0
        clip_start = max(0.0, center - duration / 2.0)
        frequencies = [frequency for _, frequency in points[start:end] if frequency > 0.0]
        median_midi = midi_from_hz(statistics.median(frequencies))
        if median_midi is None:
            continue
        result.append({
            "id": f"scms_{track}_{note_name(median_midi)}",
            "track": track,
            "midi": median_midi,
            "source_path": source_path,
            "start": clip_start,
            "duration": duration,
            "frames": end - start,
        })
    return result


def balanced_limit(rows: list[dict[str, object]], limit: int) -> list[dict[str, object]]:
    buckets: dict[int, list[dict[str, object]]] = {}
    for row in rows:
        buckets.setdefault(int(row["midi"]), []).append(row)
    for bucket in buckets.values():
        bucket.sort(key=lambda row: str(row["track"]))
    selected: list[dict[str, object]] = []
    while any(buckets.values()) and (limit <= 0 or len(selected) < limit):
        for midi in sorted(buckets):
            if buckets[midi]:
                selected.append(buckets[midi].pop(0))
                if limit > 0 and len(selected) >= limit:
                    break
    return sorted(selected, key=lambda row: str(row["track"]))


def prepare(root: Path, output: Path, minimum_frames: int, clip_seconds: float, limit: int, minimum_samples: int) -> int:
    selected = balanced_limit(candidates(root, minimum_frames, clip_seconds), limit)
    if len(selected) < minimum_samples:
        raise ValueError(f"expected at least {minimum_samples} stable SCMS clips, found {len(selected)}")
    output.mkdir(parents=True, exist_ok=True)
    rows = ["id\tfamily\tnsynth_family\tsource\tmidi\tnote\tpath\tqualities"]
    for row in selected:
        relative = Path("audio") / f"{row['id']}.wav"
        destination = output / relative
        if not destination.is_file() and not clip_wav(row["source_path"], destination, float(row["start"]), float(row["duration"])):
            continue
        rows.append("\t".join((
            str(row["id"]), "vocals", "vocal", "scms", str(row["midi"]), note_name(int(row["midi"])),
            relative.as_posix(),
            f"{FIXTURE_VERSION},track={row['track']},stable_frames={row['frames']},start={row['start']:.3f}",
        )))
    if len(rows) - 1 < minimum_samples:
        raise ValueError(f"only {len(rows) - 1} SCMS clips could be written")
    manifest = output / "manifest.tsv"
    temporary = manifest.with_suffix(".partial")
    temporary.write_text("\n".join(rows) + "\n", encoding="utf-8")
    temporary.replace(manifest)
    print(f"prepare_scms_vocal_mix_samples: wrote {len(rows) - 1} clips to {manifest}")
    return len(rows) - 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--minimum-stable-frames", type=int, default=8)
    parser.add_argument("--clip-seconds", type=float, default=0.50)
    parser.add_argument("--limit", type=int, default=300)
    parser.add_argument("--minimum-samples", type=int, default=250)
    args = parser.parse_args(argv)
    try:
        prepare(args.root, args.output, args.minimum_stable_frames, args.clip_seconds, args.limit, args.minimum_samples)
    except (OSError, ValueError, wave.Error) as error:
        parser.error(str(error))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
