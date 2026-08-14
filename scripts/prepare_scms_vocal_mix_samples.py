#!/usr/bin/env python3
"""Prepare stable, labelled SCMS vocal-plus-accompaniment probe clips."""

from __future__ import annotations

import argparse
import csv
import math
import subprocess
import sys
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


def first_stable_run(path: Path, minimum_frames: int, clip_seconds: float) -> tuple[float, float, int] | None:
    """Return the first long-enough voiced MIDI run without loading a whole CSV.

    SCMS pitch CSVs collectively occupy nearly a gigabyte.  A labelled probe
    only needs one stable half-second from each recording, so streaming to the
    first qualifying run keeps sample-limit expansion practical while retaining
    deterministic, annotation-only ground truth selection.
    """
    current: int | None = None
    start_time = 0.0
    frames = 0
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
            midi = midi_from_hz(frequency)
            if midi != current:
                current = midi
                start_time = timestamp
                frames = 1
            else:
                frames += 1
            if current is not None and frames >= minimum_frames and timestamp - start_time >= clip_seconds:
                return start_time, timestamp, current
    return None


def clip_wav(source_path: Path, destination_path: Path, start_seconds: float, duration_seconds: float, ffmpeg: str) -> bool:
    """Clip SCMS WAVE audio without playing it, normalising IEEE-float input to PCM."""
    destination_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination_path.with_name(destination_path.name + ".tmp.wav")
    try:
        subprocess.run(
            [
                ffmpeg, "-nostdin", "-hide_banner", "-loglevel", "error", "-y",
                "-ss", f"{start_seconds:.6f}", "-t", f"{duration_seconds:.6f}",
                "-i", str(source_path), "-acodec", "pcm_s16le", str(temporary),
            ],
            check=True,
        )
    except (OSError, subprocess.CalledProcessError) as error:
        temporary.unlink(missing_ok=True)
        print(f"prepare_scms_vocal_mix_samples: skipped {source_path}: {error}", file=sys.stderr)
        return False
    temporary.replace(destination_path)
    return valid_analyzer_wav(destination_path)


def valid_analyzer_wav(path: Path) -> bool:
    """Match the lightweight RIFF/fmt/data requirements of analyzer_real_note_samples."""
    try:
        size = path.stat().st_size
        with path.open("rb") as source:
            if size < 20 or source.read(4) != b"RIFF":
                return False
            source.read(4)
            if source.read(4) != b"WAVE":
                return False
            fmt_ok = False
            data_ok = False
            offset = 12
            while offset + 8 <= size:
                source.seek(offset)
                chunk_id = source.read(4)
                chunk_size_data = source.read(4)
                if len(chunk_size_data) != 4:
                    return False
                chunk_size = int.from_bytes(chunk_size_data, "little")
                data_offset = offset + 8
                if data_offset + chunk_size > size:
                    return False
                if chunk_id == b"fmt " and chunk_size >= 16:
                    source.seek(data_offset)
                    fields = source.read(16)
                    audio_format = int.from_bytes(fields[0:2], "little")
                    channels = int.from_bytes(fields[2:4], "little")
                    sample_rate = int.from_bytes(fields[4:8], "little")
                    block_align = int.from_bytes(fields[12:14], "little")
                    bits_per_sample = int.from_bytes(fields[14:16], "little")
                    fmt_ok = audio_format in (1, 3) and channels > 0 and sample_rate > 0 and block_align > 0 and bits_per_sample > 0
                elif chunk_id == b"data" and chunk_size > 0:
                    data_ok = True
                offset = data_offset + chunk_size + (chunk_size & 1)
            return fmt_ok and data_ok
    except OSError:
        return False


def audio_by_track(root: Path) -> dict[str, Path]:
    result: dict[str, Path] = {}
    for path in sorted(root.rglob("*.wav")):
        key = path.stem.casefold()
        if key in result:
            raise ValueError(f"duplicate SCMS audio track identifier: {path.stem}")
        result[key] = path
    return result


def candidates(root: Path, minimum_frames: int, clip_seconds: float, limit: int) -> list[dict[str, object]]:
    audio = audio_by_track(root)
    result: list[dict[str, object]] = []
    for pitch_path in sorted(root.rglob("*.csv")):
        track = pitch_path.stem
        source_path = audio.get(track.casefold())
        if source_path is None:
            continue
        run = first_stable_run(pitch_path, minimum_frames, clip_seconds)
        if run is None:
            continue
        first_time, last_time, midi = run
        duration = min(clip_seconds, max(0.001, last_time - first_time))
        center = (first_time + last_time) / 2.0
        clip_start = max(0.0, center - duration / 2.0)
        result.append({
            "id": f"scms_{track}_{note_name(midi)}",
            "track": track,
            "midi": midi,
            "source_path": source_path,
            "start": clip_start,
            "duration": duration,
            "frames": minimum_frames,
        })
        if limit > 0 and len(result) >= limit:
            break
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


def prepare(root: Path, output: Path, minimum_frames: int, clip_seconds: float, limit: int, minimum_samples: int,
            ffmpeg: str) -> int:
    selected = balanced_limit(candidates(root, minimum_frames, clip_seconds, limit), limit)
    if len(selected) < minimum_samples:
        raise ValueError(f"expected at least {minimum_samples} stable SCMS clips, found {len(selected)}")
    output.mkdir(parents=True, exist_ok=True)
    rows = ["id\tfamily\tnsynth_family\tsource\tmidi\tnote\tpath\tqualities"]
    for row in selected:
        relative = Path("audio") / f"{row['id']}.wav"
        destination = output / relative
        if not valid_analyzer_wav(destination) and not clip_wav(row["source_path"], destination, float(row["start"]), float(row["duration"]), ffmpeg):
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
    parser.add_argument("--ffmpeg", default="ffmpeg")
    args = parser.parse_args(argv)
    try:
        prepare(args.root, args.output, args.minimum_stable_frames, args.clip_seconds, args.limit, args.minimum_samples, args.ffmpeg)
    except (OSError, ValueError, subprocess.CalledProcessError, wave.Error) as error:
        parser.error(str(error))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
