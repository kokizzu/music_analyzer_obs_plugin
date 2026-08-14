#!/usr/bin/env python3
"""Prepare stable, labelled MIR-1K vocal-plus-accompaniment probe clips."""

from __future__ import annotations

import argparse
import math
import shutil
import wave
from pathlib import Path


FIXTURE_VERSION = "mir1k-v1"
FRAME_SECONDS = 0.020


def note_name(midi: int) -> str:
    names = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")
    return f"{names[midi % 12]}{midi // 12 - 1}"


def pitch_values(path: Path) -> list[float]:
    values: list[float] = []
    for number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1):
        try:
            values.append(float(line.strip() or "0"))
        except ValueError as error:
            raise ValueError(f"{path}:{number}: invalid pitch value") from error
    return values


def longest_stable_run(values: list[float], minimum_frames: int) -> tuple[int, int, int] | None:
    best: tuple[int, int, int] | None = None
    start = 0
    current: int | None = None
    for index, value in enumerate(values + [0.0]):
        midi = int(round(value)) if value > 0.0 and math.isfinite(value) else None
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
        frames = min(frames, source.getnframes() - start_frame)
        audio = source.readframes(frames)
        params = source.getparams()
    destination_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination_path.with_suffix(destination_path.suffix + ".tmp")
    with wave.open(str(temporary), "wb") as destination:
        destination.setparams(params)
        destination.writeframes(audio)
    temporary.replace(destination_path)
    return True


def candidates(root: Path, minimum_frames: int, clip_seconds: float) -> list[dict[str, object]]:
    dataset = root / "mir1k_yourmt3_16k"
    wav_dir = dataset / "Wavfile"
    pitch_dir = dataset / "PitchLabel"
    result: list[dict[str, object]] = []
    for pitch_path in sorted(pitch_dir.glob("*.pv")):
        track = pitch_path.stem
        source_path = wav_dir / f"{track}.wav"
        if not source_path.is_file():
            continue
        run = longest_stable_run(pitch_values(pitch_path), minimum_frames)
        if run is None:
            continue
        start, end, midi = run
        available = (end - start) * FRAME_SECONDS
        duration = min(clip_seconds, available)
        center = (start + end) * FRAME_SECONDS / 2.0
        clip_start = max(0.0, center - duration / 2.0)
        result.append({
            "id": f"mir1k_{track}_{note_name(midi)}",
            "track": track,
            "midi": midi,
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
        raise ValueError(f"expected at least {minimum_samples} stable MIR-1K clips, found {len(selected)}")
    output.mkdir(parents=True, exist_ok=True)
    manifest = output / "manifest.tsv"
    rows: list[str] = ["id\tfamily\tnsynth_family\tsource\tmidi\tnote\tpath\tqualities"]
    for row in selected:
        relative = Path("audio") / f"{row['id']}.wav"
        destination = output / relative
        if not destination.is_file() and not clip_wav(row["source_path"], destination, float(row["start"]), float(row["duration"])):
            continue
        rows.append("\t".join((
            str(row["id"]), "vocals", "vocal", "mir1k", str(row["midi"]), note_name(int(row["midi"])),
            relative.as_posix(),
            f"{FIXTURE_VERSION},track={row['track']},stable_frames={row['frames']},start={row['start']:.3f}",
        )))
    if len(rows) - 1 < minimum_samples:
        raise ValueError(f"only {len(rows) - 1} MIR-1K clips could be written")
    temporary = manifest.with_suffix(".partial")
    temporary.write_text("\n".join(rows) + "\n", encoding="utf-8")
    temporary.replace(manifest)
    print(f"prepare_mir1k_vocal_mix_samples: wrote {len(rows) - 1} clips to {manifest}")
    return len(rows) - 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--minimum-stable-frames", type=int, default=20)
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
