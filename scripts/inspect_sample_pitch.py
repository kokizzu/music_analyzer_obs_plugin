#!/usr/bin/env python3

import argparse
import math
import struct
import wave


FIRST_MIDI = 21
LAST_MIDI = 108
SAMPLE_RATE = 48000
WINDOW_MS = 100
HARMONIC_INTERVALS = (12, 19, 24, 28, 31)
TUNING_PROBE_CENTS = (-18.0, -9.0, 0.0, 9.0, 18.0)


def note_name(midi):
    names = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")
    return f"{names[midi % 12]}{midi // 12 - 1}"


def midi_frequency(midi):
    return 440.0 * (2.0 ** ((midi - 69.0) / 12.0))


def read_wav_mono(path):
    with wave.open(path, "rb") as wav:
        channels = wav.getnchannels()
        sample_width = wav.getsampwidth()
        sample_rate = wav.getframerate()
        frames = wav.readframes(wav.getnframes())
    if sample_width != 2:
        raise SystemExit(f"unsupported sample width {sample_width}")

    values = []
    for offset in range(0, len(frames), sample_width * channels):
        total = 0.0
        for channel in range(channels):
            start = offset + channel * sample_width
            sample = struct.unpack_from("<h", frames, start)[0] / 32768.0
            total += sample
        values.append(total / channels)
    return sample_rate, values


def make_analysis_window(samples, sample_rate, target_peak):
    peak = max((abs(sample) for sample in samples), default=0.0)
    if peak <= 1.0e-6:
        return []
    threshold = max(peak * 0.020, 0.0008)
    onset = 0
    for index, sample in enumerate(samples):
        if abs(sample) >= threshold:
            onset = index
            break
    start = min(len(samples) - 1, onset + int(sample_rate * 0.080))
    count = min(int(sample_rate * WINDOW_MS / 1000), len(samples) - start)
    window = samples[start:start + count]
    window_peak = max((abs(sample) for sample in window), default=0.0)
    if window_peak <= 1.0e-6:
        return []
    gain = min(24.0, target_peak / window_peak)
    return [max(-1.0, min(1.0, sample * gain)) for sample in window]


def goertzel(samples, freq, sample_rate):
    count = len(samples)
    if count == 0:
        return 0.0
    mean = sum(samples) / count
    coeff = 2.0 * math.cos(2.0 * math.pi * freq / sample_rate)
    s1 = 0.0
    s2 = 0.0
    if count == 1:
        windows = (1.0,)
    else:
        windows = (0.5 - 0.5 * math.cos(2.0 * math.pi * i / (count - 1)) for i in range(count))
    for sample, weight in zip(samples, windows):
        x = (sample - mean) * weight
        s0 = x + coeff * s1 - s2
        s2 = s1
        s1 = s0
    return max(0.0, s1 * s1 + s2 * s2 - coeff * s1 * s2)


def level(samples, midi, sample_rate):
    if midi < FIRST_MIDI or midi > LAST_MIDI:
        return 0.0
    return math.sqrt(goertzel(samples, midi_frequency(midi), sample_rate))


def harmonic_score(levels, midi):
    score = levels.get(midi, 0.0)
    score += levels.get(midi + 12, 0.0) * 0.72
    score += levels.get(midi + 19, 0.0) * 0.62
    score += levels.get(midi + 24, 0.0) * 0.48
    score += levels.get(midi + 28, 0.0) * 0.34
    score += levels.get(midi + 31, 0.0) * 0.26
    score += levels.get(midi + 36, 0.0) * 0.18
    score += levels.get(midi + 40, 0.0) * 0.12
    score += levels.get(midi + 43, 0.0) * 0.10
    return score


def tuning_estimate(samples, midi, sample_rate):
    scores = []
    center = midi_frequency(midi)
    for cents in TUNING_PROBE_CENTS:
        freq = center * (2.0 ** (cents / 1200.0))
        scores.append(math.sqrt(goertzel(samples, freq, sample_rate)))
    best = max(range(len(scores)), key=scores.__getitem__)
    cents = TUNING_PROBE_CENTS[best]
    if 0 < best < len(scores) - 1:
        previous = scores[best - 1]
        current = scores[best]
        next_score = scores[best + 1]
        denominator = previous - 2.0 * current + next_score
        if abs(denominator) > 1.0e-9:
            step = TUNING_PROBE_CENTS[best] - TUNING_PROBE_CENTS[best - 1]
            cents += 0.5 * (previous - next_score) / denominator * step
    cents = max(TUNING_PROBE_CENTS[0], min(TUNING_PROBE_CENTS[-1], cents))
    return cents, scores[2], max(scores)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("wav")
    parser.add_argument("--expected-midi", type=int, required=True)
    parser.add_argument("--min-midi", type=int, default=FIRST_MIDI)
    parser.add_argument("--max-midi", type=int, default=LAST_MIDI)
    parser.add_argument("--target-peak", type=float, default=0.62)
    args = parser.parse_args()

    sample_rate, samples = read_wav_mono(args.wav)
    window = make_analysis_window(samples, sample_rate, args.target_peak)
    if not window:
        raise SystemExit("silent analysis window")

    levels = {midi: level(window, midi, sample_rate) for midi in range(FIRST_MIDI, LAST_MIDI + 1)}
    ranked_raw = sorted(range(args.min_midi, args.max_midi + 1), key=lambda midi: levels[midi], reverse=True)
    ranked_harmonic = sorted(
        range(args.min_midi, args.max_midi + 1),
        key=lambda midi: harmonic_score(levels, midi),
        reverse=True,
    )

    expected_cents, expected_center, expected_best = tuning_estimate(window, args.expected_midi, sample_rate)
    print(f"{args.wav}")
    print(
        f"expected {note_name(args.expected_midi)} midi {args.expected_midi}: "
        f"raw={levels[args.expected_midi]:.5f} harmonic={harmonic_score(levels, args.expected_midi):.5f} "
        f"tuning={expected_cents:+.1f}c center/best={expected_center:.5f}/{expected_best:.5f}"
    )
    print("top raw:")
    for midi in ranked_raw[:12]:
        cents, center, best = tuning_estimate(window, midi, sample_rate)
        print(
            f"  {note_name(midi):4s} {midi:3d} raw={levels[midi]:.5f} "
            f"harmonic={harmonic_score(levels, midi):.5f} tuning={cents:+.1f}c "
            f"center/best={center:.5f}/{best:.5f}"
        )
    print("top harmonic:")
    for midi in ranked_harmonic[:12]:
        cents, center, best = tuning_estimate(window, midi, sample_rate)
        print(
            f"  {note_name(midi):4s} {midi:3d} raw={levels[midi]:.5f} "
            f"harmonic={harmonic_score(levels, midi):.5f} tuning={cents:+.1f}c "
            f"center/best={center:.5f}/{best:.5f}"
        )


if __name__ == "__main__":
    main()
