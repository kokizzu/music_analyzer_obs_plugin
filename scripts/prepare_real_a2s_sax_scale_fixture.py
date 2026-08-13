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
    parser.add_argument("--wav", type=Path)
    parser.add_argument("--kern", type=Path)
    parser.add_argument(
        "--input",
        action="append",
        nargs=4,
        metavar=("WAV", "KERN", "TEMPO", "LEAD_IN_SECONDS"),
        help="repeatable score/audio/tempo/lead-in tuple; replaces --wav/--kern/--tempo",
    )
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--ffmpeg", default="ffmpeg")
    parser.add_argument("--lead-in-seconds", type=float, default=0.5)
    parser.add_argument("--tempo", type=float)
    parser.add_argument("--midi-offset", type=int, default=0)
    parser.add_argument("--tail-seconds", type=float, default=0.08)
    args = parser.parse_args()

    inputs: list[tuple[Path, Path, float, float]] = []
    if args.input:
        for wav_text, kern_text, tempo_text, lead_in_text in args.input:
            inputs.append((Path(wav_text), Path(kern_text), float(tempo_text), float(lead_in_text)))
    elif args.wav is not None and args.kern is not None and args.tempo is not None:
        inputs.append((args.wav, args.kern, args.tempo, args.lead_in_seconds))
    else:
        raise SystemExit("provide either --input WAV KERN TEMPO or --wav --kern --tempo")
    if args.tail_seconds < 0.0 or any(tempo <= 0.0 or lead_in < 0.0 for _, _, tempo, lead_in in inputs):
        raise SystemExit("tempo, lead-in, and tail must be non-negative (tempo positive)")
    if any(not wav.is_file() or not kern.is_file() for wav, kern, _, _ in inputs):
        raise SystemExit("every WAV and **kern input must exist")
    if shutil.which(args.ffmpeg) is None:
        raise SystemExit(f"ffmpeg not found: {args.ffmpeg}")

    output = args.output
    audio = output / "audio"
    audio.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, str]] = []
    for wav, kern, tempo, lead_in_seconds in inputs:
        events = score_events(kern)
        seconds_per_beat = 60.0 / tempo
        start = lead_in_seconds
        for index, (beats, written_midi) in enumerate(events):
            duration = beats * seconds_per_beat
            midi = written_midi + args.midi_offset
            relative = Path("audio") / f"{kern.stem}_{index:02d}_{note_name(midi)}.wav"
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
                str(wav),
                "-ac",
                "1",
                "-ar",
                "44100",
                str(destination),
            ]
            subprocess.run(command, check=True)
            rows.append(
                {
                    "id": f"real-a2s-tenor-{kern.stem}-{index:02d}",
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
