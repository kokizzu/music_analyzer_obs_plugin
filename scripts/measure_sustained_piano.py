#!/usr/bin/env python3
"""Score note-duration and foreign-row evidence against real aligned piano MIDI."""
import array
import csv
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import wave

from midi_sustain_reference import read_intervals
from measure_sustained_analyzer import summarize

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def score(rows, intervals, rate):
    hop_seconds = int(rate * .05 + .5) / rate
    totals = dict(frames=len(rows), held_note_seconds=0., missing_any_row_note_seconds=0.,
                  missing_keyboard_note_seconds=0., unsupported_pitch_note_seconds=0.,
                  foreign_guitar_frame_seconds=0., foreign_voice_frame_seconds=0.)
    for row in rows:
        end = int(row["end_sample"]) / rate
        start = max(0., end - .1)
        held = {note["midi"] for note in intervals if note["channel"] != 9 and note["start"] <= start and note["key_end"] >= end}
        # Pedal/release grace prevents immediately declaring a decaying note
        # wrong. MIDI support still does not prove its acoustic audibility.
        allowed = {note["midi"] for note in intervals if note["channel"] != 9 and note["start"] <= end and note["end"] + .3 >= start}
        grids = {key: {int(v) for v in row[key].split(",") if v} for key in ("bass", "guitar", "keys", "voice", "other")}
        predicted = set().union(*grids.values())
        totals["held_note_seconds"] += len(held) * hop_seconds
        totals["missing_any_row_note_seconds"] += len(held - predicted) * hop_seconds
        totals["missing_keyboard_note_seconds"] += len(held - grids["keys"]) * hop_seconds
        totals["unsupported_pitch_note_seconds"] += len(predicted - allowed) * hop_seconds
        totals["foreign_guitar_frame_seconds"] += bool(grids["guitar"]) * hop_seconds
        totals["foreign_voice_frame_seconds"] += bool(grids["voice"]) * hop_seconds
    return totals


def main():
    fixture = ROOT / "build/maps_piano_samples"
    manifest = fixture / "maestro-v3.0.0.csv"
    with manifest.open() as stream:
        row = next(csv.DictReader(stream))
    wav, midi = fixture / row["audio_filename"], fixture / row["midi_filename"]
    paths = [wav, midi, manifest, ROOT / "src/analyzer.cpp", ROOT / "src/analyzer.hpp",
             ROOT / "build/analyzer_sustained", Path(__file__),
             ROOT / "scripts/midi_sustain_reference.py", ROOT / "scripts/measure_sustained_analyzer.py"]
    signatures = {str(p.relative_to(ROOT)): digest(p) for p in paths}
    key = hashlib.sha256(json.dumps(signatures, sort_keys=True).encode()).hexdigest()[:12]
    directory = ROOT / "build/sustained_piano" / key
    directory.mkdir(parents=True, exist_ok=True)
    raw = directory / "prefix.f32"
    with wave.open(str(wav), "rb") as audio:
        assert audio.getsampwidth() == 2 and audio.getcomptype() == "NONE"
        rate, channels = audio.getframerate(), audio.getnchannels()
        samples = audio.readframes(min(audio.getnframes(), rate * 30))
    values = array.array("h", samples)
    if sys.byteorder != "little":
        values.byteswap()
    mono = array.array("f", (sum(values[i:i + channels]) / (32768 * channels) for i in range(0, len(values), channels)))
    if sys.byteorder != "little":
        mono.byteswap()
    raw.write_bytes(mono.tobytes())
    output = directory / "frames.tsv"
    capability = subprocess.run([str(ROOT / "build/analyzer_sustained"), "--capabilities"], text=True,
                                capture_output=True, check=True).stdout.strip()
    mode = "corrected" if capability == "pcm-correction" else "native"
    subprocess.run([str(ROOT / "build/analyzer_sustained"), str(raw), str(rate), str(output), "throughput", mode],
                   check=True, timeout=600)
    with output.open() as stream:
        frames = list(csv.DictReader(stream, delimiter="\t"))
    assert len(frames) == len(values) // channels // int(rate * .05 + .5)
    intervals = read_intervals(midi.read_bytes())
    report = dict(signatures=signatures, mode=mode, frames_sha256=digest(output), timing=summarize(frames, rate),
                  duration_metrics=score(frames, intervals, rate),
                  scope="First 30 seconds of the first aligned MAPS solo-piano recording; native engine; held-key recall and pedal/grace annotation support, not acoustic false-note ground truth")
    assert all(digest(ROOT / p) == checksum for p, checksum in signatures.items())
    (directory / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report["duration_metrics"], indent=2))
    print(directory.relative_to(ROOT) / "report.json")


if __name__ == "__main__":
    main()
