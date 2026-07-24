#!/usr/bin/env python3
"""Probe analyzer-window tuning levels for a single WAV note sample."""

from __future__ import annotations

import argparse
import math
import struct
import wave


CENT_OFFSETS = (-18.0, -9.0, 0.0, 9.0, 18.0)
BUFFER_OFFSETS_SECONDS = (0.025, 0.080, 0.180, 0.320, 0.520, 0.820, 1.200)


def midi_frequency(midi: int) -> float:
    return 440.0 * (2.0 ** ((midi - 69) / 12.0))


def load_wav(path: str) -> tuple[int, list[float]]:
    with wave.open(path, "rb") as wav:
        channels = wav.getnchannels()
        sample_width = wav.getsampwidth()
        sample_rate = wav.getframerate()
        frame_count = wav.getnframes()
        raw = wav.readframes(frame_count)

    if sample_width != 2:
        raise ValueError(f"unsupported sample width {sample_width}; expected 16-bit PCM")

    values = struct.unpack("<" + "h" * (len(raw) // 2), raw)
    samples: list[float] = []
    for frame in range(frame_count):
        total = 0.0
        for channel in range(channels):
            total += values[frame * channels + channel] / 32768.0
        samples.append(total / max(channels, 1))
    return sample_rate, samples


def first_audible_sample(samples: list[float], peak: float) -> int:
    threshold = max(peak * 0.020, 0.0008)
    for index, sample in enumerate(samples):
        if abs(sample) >= threshold:
            return index
    return 0


def goertzel_level(samples: list[float], sample_rate: int, frequency: float) -> float:
    if len(samples) < 2 or sample_rate <= 0 or frequency <= 0.0:
        return 0.0

    mean = sum(samples) / len(samples)
    coeff = 2.0 * math.cos(2.0 * math.pi * frequency / sample_rate)
    s1 = 0.0
    s2 = 0.0
    last = len(samples) - 1
    for index, sample in enumerate(samples):
        phase = 2.0 * math.pi * index / last
        window = 0.5 - 0.5 * math.cos(phase)
        value = (sample - mean) * window
        s0 = value + coeff * s1 - s2
        s2 = s1
        s1 = s0
    return math.sqrt(max(0.0, s1 * s1 + s2 * s2 - coeff * s1 * s2))


def interpolated_cents(scores: list[float], best: int) -> float:
    cents = CENT_OFFSETS[best]
    if 0 < best < len(scores) - 1:
        previous = scores[best - 1]
        current = scores[best]
        next_score = scores[best + 1]
        denominator = previous - 2.0 * current + next_score
        if abs(denominator) > 1.0e-9:
            step = CENT_OFFSETS[best] - CENT_OFFSETS[best - 1]
            cents += 0.5 * (previous - next_score) / denominator * step
    return max(CENT_OFFSETS[0], min(CENT_OFFSETS[-1], cents))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("wav")
    parser.add_argument("midi", type=int)
    parser.add_argument("--window-ms", type=float, default=100.0)
    parser.add_argument("--target-peak", type=float, default=0.62)
    args = parser.parse_args()

    sample_rate, samples = load_wav(args.wav)
    peak = max((abs(sample) for sample in samples), default=0.0)
    if peak < 1.0e-5:
        raise ValueError("silent sample")

    onset = first_audible_sample(samples, peak)
    window_count = max(1, round(sample_rate * args.window_ms / 1000.0))
    center_frequency = midi_frequency(args.midi)

    for buffer_index, offset_seconds in enumerate(BUFFER_OFFSETS_SECONDS):
        start = min(len(samples) - 1, onset + int(sample_rate * offset_seconds))
        fixture_count = min(8192, len(samples) - start)
        window_peak = max((abs(samples[start + i]) for i in range(fixture_count)), default=0.0)
        if window_peak < 1.0e-5:
            continue
        gain = min(24.0, args.target_peak / window_peak)
        window = [
            max(-1.0, min(1.0, samples[start + i] * gain))
            if start + i < len(samples) else 0.0
            for i in range(window_count)
        ]

        scores = [
            goertzel_level(window, sample_rate, center_frequency * (2.0 ** (cents / 1200.0)))
            for cents in CENT_OFFSETS
        ]
        best = max(range(len(scores)), key=scores.__getitem__)
        local = [
            (goertzel_level(window, sample_rate, midi_frequency(midi)), midi)
            for midi in range(max(21, args.midi - 12), min(108, args.midi + 12) + 1)
        ]
        local.sort(reverse=True)
        print(
            f"buffer={buffer_index} start={start} best_cents={CENT_OFFSETS[best]:.0f} "
            f"interp_cents={interpolated_cents(scores, best):.3f} "
            f"scores={','.join(f'{score:.4f}' for score in scores)} "
            f"local={','.join(f'{midi}:{score:.4f}' for score, midi in local[:8])}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
