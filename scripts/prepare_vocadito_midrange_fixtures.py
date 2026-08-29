#!/usr/bin/env python3
"""Prepare external, note-centred vocadito clips for vocal detection evaluation."""

from __future__ import annotations

import argparse
import csv
import math
import os
import shutil
import subprocess
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
EXPANSION_LINK = REPO_ROOT / "build" / "real_instrument_expansion_samples"
OUTPUT_LINK = REPO_ROOT / "build" / "vocadito_midrange_samples"
VOCADITO_DIRECTORY = "vocadito"
OUTPUT_DIRECTORY = "vocadito_midrange_samples"
HEADER = ("id", "family", "nsynth_family", "source", "midi", "note", "path", "qualities")


@dataclass(frozen=True)
class Candidate:
    identifier: str
    recording: int
    onset: float
    duration: float
    frequency: float
    midi: int

    @property
    def output_name(self) -> str:
        return f"audio/{self.identifier}.wav"


def note_name(midi: int) -> str:
    names = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")
    return f"{names[midi % 12]}{midi // 12 - 1}"


def midi_from_hertz(frequency: float) -> int:
    return int(round(69 + 12 * math.log2(frequency / 440.0)))


def sample_root() -> Path:
    if not EXPANSION_LINK.exists():
        raise RuntimeError(f"missing external fixture link: {EXPANSION_LINK}")
    return EXPANSION_LINK.resolve()


def output_root(root: Path) -> Path:
    return root.parent / OUTPUT_DIRECTORY


def parse_recording(path: Path) -> int:
    stem = path.stem
    marker = "vocadito_"
    if not stem.startswith(marker):
        raise ValueError(path.name)
    return int(stem[len(marker) :].split("_", 1)[0])


def candidates(root: Path, minimum_duration: float, limit_per_midi: int) -> list[Candidate]:
    notes_directory = root / VOCADITO_DIRECTORY / "Annotations" / "Notes"
    audio_directory = root / VOCADITO_DIRECTORY / "Audio"
    if not notes_directory.is_dir() or not audio_directory.is_dir():
        raise RuntimeError("vocadito audio or note annotations are missing; run make apply-vocadito-fixtures")

    all_candidates: list[Candidate] = []
    for notes_path in sorted(notes_directory.glob("vocadito_*_notesA1.csv")):
        recording = parse_recording(notes_path)
        if not (audio_directory / f"vocadito_{recording}.wav").is_file():
            continue
        with notes_path.open(newline="", encoding="utf-8") as annotation:
            for index, row in enumerate(csv.reader(annotation)):
                if len(row) < 3:
                    continue
                try:
                    onset, frequency, duration = map(float, row[:3])
                except ValueError:
                    continue
                if frequency <= 0.0 or duration < minimum_duration:
                    continue
                midi = midi_from_hertz(frequency)
                if midi < 50 or midi > 54:
                    continue
                identifier = f"vocadito_{recording:02d}_{index:04d}_{note_name(midi)}"
                all_candidates.append(Candidate(identifier, recording, onset, duration, frequency, midi))

    selected: list[Candidate] = []
    selected_per_midi: Counter[int] = Counter()
    selected_per_recording_midi: Counter[tuple[int, int]] = Counter()
    for candidate in sorted(all_candidates, key=lambda item: (item.midi, item.recording, item.onset)):
        key = (candidate.recording, candidate.midi)
        if selected_per_midi[candidate.midi] >= limit_per_midi or selected_per_recording_midi[key] >= 2:
            continue
        selected.append(candidate)
        selected_per_midi[candidate.midi] += 1
        selected_per_recording_midi[key] += 1
    return selected


def manifest_text(items: list[Candidate]) -> str:
    rows = ["\t".join(HEADER)]
    for item in items:
        qualities = (
            f"recording={item.recording},onset={item.onset:.6f},duration={item.duration:.6f},"
            f"annotated_hz={item.frequency:.3f},annotator=A1,vocadito-v1"
        )
        rows.append(
            "\t".join(
                (item.identifier, "vocals", "vocal", "vocadito", str(item.midi), note_name(item.midi),
                 item.output_name, qualities)
            )
        )
    return "\n".join(rows) + "\n"


def describe(items: list[Candidate], root: Path) -> None:
    counts = Counter(item.midi for item in items)
    print(f"source-root={root / VOCADITO_DIRECTORY}")
    print(f"selected-clips={len(items)}")
    print("selected-by-midi=" + " ".join(f"{note_name(midi)}={counts[midi]}" for midi in sorted(counts)))
    print("selection-preview=")
    for item in items[:20]:
        print(
            f"{item.identifier}\t{note_name(item.midi)}\t{item.onset:.3f}s\t"
            f"{item.duration:.3f}s\t{item.frequency:.2f}Hz"
        )


def ensure_output_link(destination: Path) -> None:
    if OUTPUT_LINK.exists() or OUTPUT_LINK.is_symlink():
        if not OUTPUT_LINK.is_symlink() or OUTPUT_LINK.resolve() != destination:
            raise RuntimeError(f"fixture link already points elsewhere: {OUTPUT_LINK}")
        return
    OUTPUT_LINK.symlink_to(destination)


def extract_clip(source: Path, destination: Path, onset: float, duration: float, ffmpeg: str) -> None:
    stable_margin = min(0.05, duration * 0.20)
    stable_onset = onset + stable_margin
    stable_duration = duration - stable_margin * 2.0
    if stable_duration < 0.10:
        raise RuntimeError(f"annotation is too short after margin: {source.name} at {onset:.3f}s")
    temporary = destination.with_suffix(".tmp.wav")
    command = [
        ffmpeg,
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        "-ss",
        f"{stable_onset:.6f}",
        "-i",
        str(source),
        "-t",
        f"{stable_duration:.6f}",
        "-ac",
        "1",
        "-ar",
        "44100",
        "-c:a",
        "pcm_s16le",
        str(temporary),
    ]
    subprocess.run(command, check=True)
    temporary.replace(destination)


def command_apply(items: list[Candidate], root: Path, ffmpeg: str) -> int:
    if shutil.which(ffmpeg) is None:
        raise RuntimeError(f"ffmpeg is required but was not found: {ffmpeg}")
    destination = output_root(root)
    audio_destination = destination / "audio"
    audio_source = root / VOCADITO_DIRECTORY / "Audio"
    destination.mkdir(parents=True, exist_ok=True)
    audio_destination.mkdir(exist_ok=True)
    ensure_output_link(destination)
    for item in items:
        target = destination / item.output_name
        if target.is_file():
            continue
        extract_clip(audio_source / f"vocadito_{item.recording}.wav", target, item.onset, item.duration, ffmpeg)
    manifest = destination / "manifest.tsv"
    temporary_manifest = manifest.with_suffix(".tmp")
    temporary_manifest.write_text(manifest_text(items), encoding="utf-8")
    temporary_manifest.replace(manifest)
    print(f"manifest={manifest}")
    print(f"link={OUTPUT_LINK} -> {destination}")
    describe(items, root)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("plan", "apply"))
    parser.add_argument("--minimum-duration", type=float, default=0.20)
    parser.add_argument("--limit-per-midi", type=int, default=40)
    parser.add_argument("--ffmpeg", default=os.environ.get("FFMPEG", "ffmpeg"))
    args = parser.parse_args()
    if args.minimum_duration <= 0.0 or args.limit_per_midi <= 0:
        raise SystemExit("minimum duration and per-MIDI limit must be positive")
    root = sample_root()
    items = candidates(root, args.minimum_duration, args.limit_per_midi)
    if not items:
        raise RuntimeError("no annotated D3-F#3 clips matched the selection")
    if args.command == "plan":
        describe(items, root)
        print(f"planned-output={output_root(root)}")
        return 0
    return command_apply(items, root, args.ffmpeg)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(1)
