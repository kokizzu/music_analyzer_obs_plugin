#!/usr/bin/env python3
"""Inspect MIR-1K pitch-label semantics before extracting vocal fixtures."""

from __future__ import annotations

import collections
import pathlib
import statistics
import wave


ROOT = pathlib.Path("build/mir1k_vocal_fixtures/source/MIR-1K")


def main() -> int:
    labels = sorted((ROOT / "PitchLabel").glob("*.pv"))
    wavs = sorted((ROOT / "Wavfile").glob("*.wav"))
    lyrics_wavs = sorted((ROOT / "LyricsWav").glob("*.wav"))
    print(f"labels: {len(labels)}")
    print(f"Wavfile WAVs: {len(wavs)}")
    print(f"LyricsWav WAVs: {len(lyrics_wavs)}")

    value_counts: collections.Counter[float] = collections.Counter()
    voiced_values: list[float] = []
    per_label: list[tuple[pathlib.Path, int, int, float, float]] = []
    for label in labels:
        values: list[float] = []
        for raw in label.read_text(encoding="utf-8", errors="replace").splitlines():
            raw = raw.strip()
            if not raw:
                continue
            try:
                values.append(float(raw.split()[0]))
            except ValueError:
                continue
        value_counts.update(values)
        voiced = [value for value in values if value > 0.0]
        voiced_values.extend(voiced)
        if voiced:
            per_label.append((label, len(values), len(voiced), min(voiced), max(voiced)))

    print(f"total pitch frames: {sum(value_counts.values())}")
    print(f"voiced pitch frames: {len(voiced_values)}")
    if voiced_values:
        print("voiced pitch Hz: "
              f"min={min(voiced_values):.3f} "
              f"p50={statistics.median(voiced_values):.3f} "
              f"mean={statistics.fmean(voiced_values):.3f} "
              f"max={max(voiced_values):.3f}")
    print("first non-silent labels:")
    for label, total, voiced, minimum, maximum in per_label[:12]:
        stem = label.stem
        candidates = [
            ROOT / "Wavfile" / f"{stem}.wav",
            ROOT / "LyricsWav" / f"{stem.rsplit('_', 1)[0]}_lyrics.wav",
        ]
        descriptions = []
        for path in candidates:
            if not path.exists():
                continue
            with wave.open(str(path), "rb") as audio:
                duration = audio.getnframes() / audio.getframerate()
                descriptions.append(
                    f"{path.relative_to(ROOT)} {audio.getnchannels()}ch "
                    f"{audio.getframerate()}Hz {duration:.2f}s")
        existing = ", ".join(descriptions)
        print(f"{label.relative_to(ROOT)} frames={total} voiced={voiced} "
              f"Hz={minimum:.2f}-{maximum:.2f} audio={existing or '<none>'}")
    print("most common pitch values:")
    for value, count in value_counts.most_common(12):
        print(f"MIDI {value:.6g}\t{count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
