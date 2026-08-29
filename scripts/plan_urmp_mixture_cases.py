#!/usr/bin/env python3
"""Plan time-aligned, polyphonic URMP mixture windows for analyzer tests."""

from __future__ import annotations

from collections import Counter
import argparse
import math
import os
from pathlib import Path
import re
import wave


ROOT = Path(__file__).resolve().parents[1]
CORPUS_ROOT = ROOT / "build" / "urmp_multitrack_samples" / "urmp_yourmt3_16k"
WINDOW_SECONDS = 0.60
CENTER_OFFSET_SECONDS = WINDOW_SECONDS / 2.0
MIN_NOTE_DURATION_SECONDS = 0.72
MAX_WINDOWS_PER_PIECE = 12
WINDOW_GAP_SECONDS = 0.70
CASE_LINK = ROOT / "build" / "urmp_mixture_cases"
CASE_CACHE = CORPUS_ROOT.resolve().parents[3] / "urmp_mixture_cases"


def midi_from_frequency(frequency: float) -> int:
    return int(round(69.0 + 12.0 * math.log2(frequency / 440.0)))


def read_events(path: Path) -> list[tuple[float, float, int, str]]:
    match = re.match(r"Notes_\d+_([^_]+)_", path.name)
    if not match:
        return []
    instrument = match.group(1)
    result: list[tuple[float, float, int, str]] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        parts = raw.split()
        if len(parts) < 3:
            continue
        try:
            start, frequency, duration = map(float, parts[:3])
        except ValueError:
            continue
        if frequency <= 0.0 or duration < MIN_NOTE_DURATION_SECONDS:
            continue
        midi = midi_from_frequency(frequency)
        if 24 <= midi <= 108:
            result.append((start, start + duration, midi, instrument))
    return result


def planned_windows(events: list[tuple[float, float, int, str]]) -> list[tuple[float, list[tuple[float, float, int, str]]]]:
    choices: list[tuple[float, list[tuple[float, float, int, str]]]] = []
    last_start = -WINDOW_GAP_SECONDS
    for event_start, event_end, _, _ in events:
        center = event_start + min(0.25, (event_end - event_start) * 0.35)
        window_start = max(0.0, center - CENTER_OFFSET_SECONDS)
        if window_start - last_start < WINDOW_GAP_SECONDS:
            continue
        active = [event for event in events if event[0] <= center <= event[1]]
        if len({instrument for _, _, _, instrument in active}) < 2:
            continue
        choices.append((window_start, active))
        last_start = window_start
        if len(choices) >= MAX_WINDOWS_PER_PIECE:
            break
    return choices


def note_label(midi: int) -> str:
    names = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")
    return f"{names[midi % 12]}{midi // 12 - 1}"


def copy_window(source: Path, destination: Path, start: float) -> None:
    with wave.open(str(source), "rb") as reader:
        frames = reader.getnframes()
        rate = reader.getframerate()
        channels = reader.getnchannels()
        width = reader.getsampwidth()
        reader.setpos(min(frames, max(0, int(start * rate))))
        desired = int(WINDOW_SECONDS * rate)
        payload = reader.readframes(desired)
        if len(payload) < desired * channels * width:
            payload += bytes(desired * channels * width - len(payload))
        temporary = destination.with_suffix(".tmp.wav")
        with wave.open(str(temporary), "wb") as writer:
            writer.setparams(reader.getparams())
            writer.writeframes(payload)
        os.replace(temporary, destination)


def apply() -> int:
    audio_root = CASE_CACHE / "audio"
    audio_root.mkdir(parents=True, exist_ok=True)
    manifest = ["id\tfamily\tnsynth_family\tsource\tmidi\tnote\tpath"]
    chunk_count = 0
    note_count = 0
    for piece in sorted(path for path in CORPUS_ROOT.iterdir() if path.is_dir()):
        mix_files = list(piece.glob("AuMix_*.wav"))
        if len(mix_files) != 1:
            continue
        events = [event for path in piece.glob("Notes_*.txt") for event in read_events(path)]
        for window_index, (start, active) in enumerate(planned_windows(events)):
            chunk_id = f"{piece.name}_{window_index:02d}"
            relative = Path("audio") / f"{chunk_id}.wav"
            copy_window(mix_files[0], CASE_CACHE / relative, start)
            for event_index, (_, _, midi, instrument) in enumerate(active):
                manifest.append("\t".join((
                    f"{chunk_id}_{event_index:02d}", "bass" if instrument == "db" else "other",
                    "acoustic", f"urmpmix-{instrument}", str(midi), note_label(midi), str(relative),
                )))
                note_count += 1
            chunk_count += 1
    temporary = CASE_CACHE / "manifest.tmp.tsv"
    temporary.write_text("\n".join(manifest) + "\n", encoding="utf-8")
    os.replace(temporary, CASE_CACHE / "manifest.tsv")
    if CASE_LINK.is_symlink() or CASE_LINK.exists():
        if CASE_LINK.resolve(strict=False) != CASE_CACHE:
            raise SystemExit(f"refusing to replace unexpected mixture link: {CASE_LINK}")
    else:
        CASE_LINK.symlink_to(CASE_CACHE)
    print(f"status=ready mixture-windows={chunk_count} annotated-note-expectations={note_count} link={CASE_LINK}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", nargs="?", choices=("plan", "apply"), default="plan")
    arguments = parser.parse_args()
    if not CORPUS_ROOT.is_dir():
        raise SystemExit("missing URMP corpus; run make apply-urmp-multitrack-fixtures first")
    total_windows = 0
    total_notes = 0
    by_instrument: Counter[str] = Counter()
    by_piece: list[tuple[str, int, int]] = []
    for piece in sorted(path for path in CORPUS_ROOT.iterdir() if path.is_dir()):
        events = [event for path in piece.glob("Notes_*.txt") for event in read_events(path)]
        windows = planned_windows(events)
        total_windows += len(windows)
        note_count = sum(len(active) for _, active in windows)
        total_notes += note_count
        by_piece.append((piece.name, len(windows), note_count))
        for _, active in windows:
            by_instrument.update(instrument for _, _, _, instrument in active)
    print("dataset=URMP polyphonic real-instrument mixtures")
    print(f"source-root={CORPUS_ROOT}")
    print(f"window-seconds={WINDOW_SECONDS:.2f}")
    print(f"minimum-annotation-duration={MIN_NOTE_DURATION_SECONDS:.2f}")
    print(f"mixture-windows={total_windows}")
    print(f"annotated-note-expectations={total_notes}")
    print("instruments=" + ",".join(f"{name}={count}" for name, count in sorted(by_instrument.items())))
    print("piece-windows=" + ",".join(f"{name}={windows}/{notes}" for name, windows, notes in by_piece))
    print("storage=external-only; this is a no-write planning report")
    if arguments.mode == "apply":
        return apply()
    return 0


if __name__ == "__main__":
    main()
