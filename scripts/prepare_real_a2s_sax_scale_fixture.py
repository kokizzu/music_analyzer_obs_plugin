#!/usr/bin/env python3
"""Create silent per-note probes from a timed Real A2S tenor sax scale score."""

from __future__ import annotations

import argparse
import csv
import re
import shutil
import subprocess
from pathlib import Path


TOKEN_RE = re.compile(r"^(?P<duration>\d+)(?P<pitch>[A-Ga-g]+)(?P<accidental>[#-]*)(?:[LJ]+)?$")
BASE_MIDI = {"c": 60, "d": 62, "e": 64, "f": 65, "g": 67, "a": 69, "b": 71}
NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def parse_kern_token(token: str) -> tuple[float, int]:
    match = TOKEN_RE.match(token)
    if not match:
        raise ValueError(f"unsupported **kern note token: {token}")
    duration = 4.0 / int(match.group("duration"))
    pitch = match.group("pitch")
    letter = pitch[0]
    repeated = len(pitch)
    if letter.islower():
        midi = BASE_MIDI[letter] + 12 * (repeated - 1)
    else:
        midi = BASE_MIDI[letter.lower()] - 12 * repeated
    accidental = match.group("accidental")
    midi += accidental.count("#") - accidental.count("-")
    return duration, midi


def score_events(path: Path) -> list[tuple[float, int]]:
    events: list[tuple[float, int]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        token = line.strip()
        if not token or token.startswith(("!", "*", "=")) or "r" in token:
            continue
        if TOKEN_RE.match(token):
            events.append(parse_kern_token(token))
    if not events:
        raise ValueError(f"no parseable **kern notes in {path}")
    return events


def note_name(midi: int) -> str:
    return f"{NOTE_NAMES[midi % 12]}{midi // 12 - 1}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--wav", required=True, type=Path)
    parser.add_argument("--kern", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--ffmpeg", default="ffmpeg")
    parser.add_argument("--lead-in-seconds", type=float, default=0.5)
    parser.add_argument("--tempo", type=float, required=True)
    parser.add_argument("--midi-offset", type=int, default=0)
    parser.add_argument("--tail-seconds", type=float, default=0.08)
    args = parser.parse_args()

    if args.tempo <= 0.0 or args.lead_in_seconds < 0.0 or args.tail_seconds < 0.0:
        raise SystemExit("tempo, lead-in, and tail must be non-negative (tempo positive)")
    if not args.wav.is_file() or not args.kern.is_file():
        raise SystemExit("both --wav and --kern must exist")
    if shutil.which(args.ffmpeg) is None:
        raise SystemExit(f"ffmpeg not found: {args.ffmpeg}")

    output = args.output
    audio = output / "audio"
    audio.mkdir(parents=True, exist_ok=True)
    events = score_events(args.kern)
    seconds_per_beat = 60.0 / args.tempo
    start = args.lead_in_seconds
    rows: list[dict[str, str]] = []
    for index, (beats, written_midi) in enumerate(events):
        duration = beats * seconds_per_beat
        midi = written_midi + args.midi_offset
        relative = Path("audio") / f"{index:02d}_{note_name(midi)}.wav"
        destination = output / relative
        command = [
            args.ffmpeg,
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-ss",
            f"{start:.6f}",
            "-t",
            f"{duration + args.tail_seconds:.6f}",
            "-i",
            str(args.wav),
            "-ac",
            "1",
            "-ar",
            "44100",
            str(destination),
        ]
        subprocess.run(command, check=True)
        rows.append(
            {
                "id": f"real-a2s-tenor-{args.kern.stem}-{index:02d}",
                "family": "other",
                "nsynth_family": "reed",
                "source": "real-a2s-tenor-score-probe",
                "midi": str(midi),
                "note": note_name(midi),
                "path": str(relative),
            }
        )
        start += duration

    with (output / "manifest.tsv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"prepared {len(rows)} timed score probes: {output / 'manifest.tsv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
