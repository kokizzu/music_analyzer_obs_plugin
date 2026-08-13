#!/usr/bin/env python3
"""Print silent timing and score traits for one Real A2S sax scale recording."""

from __future__ import annotations

import argparse
import re
import wave
from pathlib import Path


def parse_kern_notes(path: Path) -> list[str]:
    notes: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        token = line.strip()
        if not token or token.startswith(("!", "*", "=")) or "r" in token:
            continue
        if re.match(r"^\d+[A-Ga-g][#-]*[A-Ga-g#-]*[LJ]*$", token):
            notes.append(token)
    if not notes:
        raise ValueError(f"no **kern notes in {path}")
    return notes


def decode_frame(frame: bytes, width: int, channels: int) -> float:
    values: list[float] = []
    for channel in range(channels):
        offset = channel * width
        sample = frame[offset : offset + width]
        if width == 2:
            value = int.from_bytes(sample, "little", signed=True) / 32768.0
        elif width == 3:
            raw = int.from_bytes(sample + (b"\xff" if sample[2] & 0x80 else b"\x00"), "little", signed=True)
            value = raw / 8388608.0
        elif width == 4:
            value = int.from_bytes(sample, "little", signed=True) / 2147483648.0
        else:
            raise ValueError(f"unsupported PCM sample width: {width}")
        values.append(value)
    return sum(values) / len(values)


def rms_windows(path: Path, seconds: float = 0.02) -> tuple[int, float, list[float]]:
    with wave.open(str(path), "rb") as source:
        if source.getcomptype() != "NONE":
            raise ValueError(f"compressed WAV is not supported: {path}")
        rate = source.getframerate()
        frames = source.getnframes()
        channels = source.getnchannels()
        width = source.getsampwidth()
        samples_per_window = max(1, round(rate * seconds))
        values: list[float] = []
        while True:
            payload = source.readframes(samples_per_window)
            if not payload:
                break
            frame_width = width * channels
            count = len(payload) // frame_width
            if not count:
                continue
            squared = 0.0
            for index in range(count):
                value = decode_frame(payload[index * frame_width : (index + 1) * frame_width], width, channels)
                squared += value * value
            values.append((squared / count) ** 0.5)
    return rate, frames / rate, values


def onset_times(levels: list[float], window_seconds: float = 0.02) -> tuple[float, list[float]]:
    initial = sorted(levels[: max(1, min(50, len(levels)))])
    noise = initial[len(initial) // 4]
    peak = max(levels, default=0.0)
    threshold = max(0.003, noise * 4.0, peak * 0.12)
    hits: list[float] = []
    armed = True
    for index, level in enumerate(levels):
        if armed and level >= threshold:
            hits.append(index * window_seconds)
            armed = False
        elif not armed and level < threshold * 0.55:
            armed = True
    return threshold, hits


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--wav", required=True, type=Path)
    parser.add_argument("--kern", required=True, type=Path)
    args = parser.parse_args()

    notes = parse_kern_notes(args.kern)
    rate, duration, levels = rms_windows(args.wav)
    threshold, onsets = onset_times(levels)
    print(f"score_notes={len(notes)} tokens={' '.join(notes)}")
    print(f"audio_rate_hz={rate} duration_seconds={duration:.3f} rms_windows={len(levels)}")
    print(f"onset_threshold={threshold:.5f} onset_count={len(onsets)} onset_seconds={' '.join(f'{value:.3f}' for value in onsets)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
