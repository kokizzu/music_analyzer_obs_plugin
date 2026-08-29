#!/usr/bin/env python3
"""Prepare deterministic, external-only single-note fixtures from URMP stems."""

from __future__ import annotations

import argparse
import math
import os
from pathlib import Path
import re
import wave


ROOT = Path(__file__).resolve().parents[1]
CORPUS_LINK = ROOT / "build" / "urmp_multitrack_samples"
CORPUS_ROOT = CORPUS_LINK / "urmp_yourmt3_16k"
CASE_LINK = ROOT / "build" / "urmp_analyzer_cases"
CASE_CACHE = CORPUS_LINK.resolve().parents[2] / "urmp_analyzer_cases"
WINDOW_SECONDS = 0.60
MIN_DURATION_SECONDS = 0.72
MAX_CASES_PER_STEM = 12
FAMILY_BY_INSTRUMENT = {
    "db": "bass",
}


def note_label(midi: int) -> str:
    names = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")
    return f"{names[midi % 12]}{midi // 12 - 1}"


def parse_notes(path: Path) -> list[tuple[float, int, float]]:
    rows: list[tuple[float, int, float]] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        parts = [part.strip() for part in raw.split()]
        if len(parts) < 3:
            continue
        try:
            start, frequency, duration = (float(parts[0]), float(parts[1]), float(parts[2]))
        except ValueError:
            continue
        if frequency <= 0.0 or duration < MIN_DURATION_SECONDS:
            continue
        midi = int(round(69.0 + 12.0 * math.log2(frequency / 440.0)))
        if not 24 <= midi <= 108:
            continue
        rows.append((start, midi, duration))
    return rows


def track_details(path: Path) -> tuple[int, str, str]:
    match = re.match(r"Notes_(\d+)_([^_]+)_(.+)\.txt$", path.name)
    if not match:
        raise ValueError(f"unsupported annotation name: {path.name}")
    return int(match.group(1)), match.group(2), match.group(3)


def selected_cases() -> list[dict[str, object]]:
    cases: list[dict[str, object]] = []
    for note_path in sorted(CORPUS_ROOT.glob("*/Notes_*.txt")):
        track, instrument, piece = track_details(note_path)
        stem_name = f"AuSep_{track}_{instrument}_{piece}.wav"
        stem_path = note_path.with_name(stem_name)
        if not stem_path.is_file():
            continue
        chosen = 0
        last_end = -1.0
        for start, midi, duration in parse_notes(note_path):
            window_start = start + min(0.12, duration * 0.18)
            if window_start < last_end:
                continue
            stem_id = f"{note_path.parent.name}_{track}_{instrument}_{midi}_{chosen:02d}"
            cases.append({
                "id": stem_id,
                "family": FAMILY_BY_INSTRUMENT.get(instrument, "other"),
                "instrument": instrument,
                "midi": midi,
                "note": note_label(midi),
                "stem": stem_path,
                "start": window_start,
                "duration": WINDOW_SECONDS,
            })
            chosen += 1
            last_end = window_start + WINDOW_SECONDS
            if chosen == MAX_CASES_PER_STEM:
                break
    return cases


def print_plan(cases: list[dict[str, object]]) -> None:
    families: dict[str, int] = {}
    instruments: dict[str, int] = {}
    for case in cases:
        families[str(case["family"])] = families.get(str(case["family"]), 0) + 1
        instruments[str(case["instrument"])] = instruments.get(str(case["instrument"]), 0) + 1
    print("dataset=URMP real-instrument stem fixtures")
    print(f"source-root={CORPUS_ROOT}")
    print(f"external-cache={CASE_CACHE}")
    print(f"repository-link={CASE_LINK}")
    print(f"window-seconds={WINDOW_SECONDS:.2f}")
    print(f"minimum-annotation-duration={MIN_DURATION_SECONDS:.2f}")
    print(f"cases={len(cases)}")
    print("families=" + ",".join(f"{name}={count}" for name, count in sorted(families.items())))
    print("instruments=" + ",".join(f"{name}={count}" for name, count in sorted(instruments.items())))
    print("storage=external-only; Git stores neither source audio nor cropped fixtures")


def copy_window(case: dict[str, object], destination: Path) -> None:
    source = Path(str(case["stem"]))
    with wave.open(str(source), "rb") as reader:
        sample_rate = reader.getframerate()
        channels = reader.getnchannels()
        sample_width = reader.getsampwidth()
        frames = reader.getnframes()
        start_frame = min(frames, max(0, int(float(case["start"]) * sample_rate)))
        desired_frames = int(float(case["duration"]) * sample_rate)
        reader.setpos(start_frame)
        payload = reader.readframes(desired_frames)
        if len(payload) < desired_frames * channels * sample_width:
            payload += bytes(desired_frames * channels * sample_width - len(payload))
        temporary = destination.with_suffix(".tmp.wav")
        with wave.open(str(temporary), "wb") as writer:
            writer.setparams(reader.getparams())
            writer.writeframes(payload)
        os.replace(temporary, destination)


def apply(cases: list[dict[str, object]]) -> None:
    audio_root = CASE_CACHE / "audio"
    audio_root.mkdir(parents=True, exist_ok=True)
    manifest_lines = ["id\tfamily\tnsynth_family\tsource\tmidi\tnote\tpath"]
    for case in cases:
        relative_path = Path("audio") / f"{case['id']}.wav"
        copy_window(case, CASE_CACHE / relative_path)
        manifest_lines.append("\t".join((
            str(case["id"]), str(case["family"]), "acoustic", f"urmp-{case['instrument']}",
            str(case["midi"]), str(case["note"]), str(relative_path),
        )))
    temporary_manifest = CASE_CACHE / "manifest.tmp.tsv"
    temporary_manifest.write_text("\n".join(manifest_lines) + "\n", encoding="utf-8")
    os.replace(temporary_manifest, CASE_CACHE / "manifest.tsv")
    if CASE_LINK.is_symlink() or CASE_LINK.exists():
        if CASE_LINK.resolve(strict=False) != CASE_CACHE:
            raise SystemExit(f"refusing to replace unexpected case link: {CASE_LINK}")
    else:
        CASE_LINK.symlink_to(CASE_CACHE)
    print(f"status=ready cases={len(cases)} link={CASE_LINK}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("plan", "apply"))
    arguments = parser.parse_args()
    if not CORPUS_ROOT.is_dir():
        raise SystemExit("missing URMP corpus; run make apply-urmp-multitrack-fixtures first")
    cases = selected_cases()
    print_plan(cases)
    if arguments.mode == "apply":
        apply(cases)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
