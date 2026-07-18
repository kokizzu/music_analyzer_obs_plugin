#!/usr/bin/env python3

import argparse
import math
from pathlib import Path
import struct


FIRST_MIDI = 21
LAST_MIDI = 108
SAMPLE_RATE = 48000
WINDOW_MS = 100
HARMONIC_INTERVALS = (12, 19, 24, 28, 31)
TUNING_PROBE_CENTS = (-18.0, -9.0, 0.0, 9.0, 18.0)
BASS_MIN_MIDI = 23
BASS_MAX_MIDI = 67
ISOLATED_BASS_PERIODICITY_FLOOR = 0.34
ISOLATED_BASS_PERIODICITY_SPECTRAL_RATIO = 0.62
ISOLATED_BASS_STRONG_HARMONIC_MAX_MIDI = 40
CHROMATIC_TUNE_MIN_MIDI = 40
CHROMATIC_TUNE_TOLERANCE_CENTS = 9.0
CHROMATIC_CENTER_ADJACENT_RATIO = 0.985
CHROMATIC_CENTER_EDGE_RATIO = 0.78
ISOLATED_COMPLEX_TUNING_FALLBACK_SCALE = 0.78


def note_name(midi):
    names = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")
    return f"{names[midi % 12]}{midi // 12 - 1}"


def midi_frequency(midi):
    return 440.0 * (2.0 ** ((midi - 69.0) / 12.0))


def read_wav_mono(path):
    data = Path(path).read_bytes()
    if len(data) < 12 or data[:4] != b"RIFF" or data[8:12] != b"WAVE":
        raise SystemExit("not a RIFF/WAVE file")

    audio_format = 0
    channels = 0
    sample_rate = 0
    bits_per_sample = 0
    frames = b""
    offset = 12
    while offset + 8 <= len(data):
        chunk_id = data[offset:offset + 4]
        chunk_size = struct.unpack_from("<I", data, offset + 4)[0]
        chunk_start = offset + 8
        chunk_end = min(len(data), chunk_start + chunk_size)
        if chunk_id == b"fmt ":
            if chunk_size < 16:
                raise SystemExit("invalid fmt chunk")
            audio_format, channels, sample_rate, _, _, bits_per_sample = struct.unpack_from(
                "<HHIIHH", data, chunk_start
            )
        elif chunk_id == b"data":
            frames = data[chunk_start:chunk_end]
        offset = chunk_end + (chunk_size & 1)

    if channels <= 0 or sample_rate <= 0 or bits_per_sample <= 0 or not frames:
        raise SystemExit("missing fmt or data chunk")
    sample_width = bits_per_sample // 8
    if sample_width <= 0:
        raise SystemExit(f"unsupported sample width {sample_width}")

    values = []
    for offset in range(0, len(frames), sample_width * channels):
        total = 0.0
        for channel in range(channels):
            start = offset + channel * sample_width
            if audio_format == 3 and sample_width == 4:
                sample = struct.unpack_from("<f", frames, start)[0]
            elif audio_format == 1 and sample_width == 2:
                sample = struct.unpack_from("<h", frames, start)[0] / 32768.0
            elif audio_format == 1 and sample_width == 3:
                raw = int.from_bytes(frames[start:start + 3], "little", signed=False)
                if raw & 0x800000:
                    raw -= 0x1000000
                sample = raw / 8388608.0
            elif audio_format == 1 and sample_width == 4:
                sample = struct.unpack_from("<i", frames, start)[0] / 2147483648.0
            else:
                raise SystemExit(f"unsupported wav format {audio_format} width {sample_width}")
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


def analyzer_bass_score(levels, midi, include_harmonics=True, isolated_harmonic_support=True):
    score = levels.get(midi, 0.0)
    if not include_harmonics:
        return score
    if isolated_harmonic_support and midi <= ISOLATED_BASS_STRONG_HARMONIC_MAX_MIDI:
        score += levels.get(midi + 12, 0.0) * 0.54
        score += levels.get(midi + 19, 0.0) * 0.96
        score += levels.get(midi + 24, 0.0) * 0.68
        score += levels.get(midi + 28, 0.0) * 0.20
        score += levels.get(midi + 31, 0.0) * 0.16
    else:
        score += levels.get(midi + 12, 0.0) * 0.38
        score += levels.get(midi + 19, 0.0) * 0.22
        score += levels.get(midi + 24, 0.0) * 0.12
    return score


def has_complex_harmonic_support(levels, midi):
    fundamental = levels.get(midi, 0.0)
    if fundamental <= 1.0e-6:
        return False
    strongest_partial = 0.0
    partial_sum = 0.0
    partial_count = 0
    for interval in HARMONIC_INTERVALS:
        partial = levels.get(midi + interval, 0.0)
        strongest_partial = max(strongest_partial, partial)
        partial_sum += partial
        if partial >= fundamental * 0.045:
            partial_count += 1
    return strongest_partial >= fundamental * 0.07 or partial_sum >= fundamental * 0.13 or partial_count >= 2


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


def chromatic_tuning_match(samples, midi, sample_rate, tolerance_cents, allow_ratio_rescue=False):
    cents, center_score, best_score = tuning_estimate(samples, midi, sample_rate)
    if abs(cents) <= tolerance_cents:
        return True
    if not allow_ratio_rescue:
        return False
    if abs(cents) <= TUNING_PROBE_CENTS[-1] and best_score > 1.0e-6 and center_score >= best_score * CHROMATIC_CENTER_ADJACENT_RATIO:
        return True
    return best_score > 1.0e-6 and abs(cents) >= TUNING_PROBE_CENTS[-1] and center_score >= best_score * CHROMATIC_CENTER_EDGE_RATIO


def analyzer_detection_levels(samples, levels, sample_rate):
    detection_levels = dict(levels)
    strongest = max(levels.values(), default=0.0)
    strict_matches = {}
    strict_count = 0
    for midi in range(FIRST_MIDI, LAST_MIDI + 1):
        if midi < CHROMATIC_TUNE_MIN_MIDI:
            continue
        match = chromatic_tuning_match(samples, midi, sample_rate, CHROMATIC_TUNE_TOLERANCE_CENTS, False)
        strict_matches[midi] = match
        if match and levels.get(midi, 0.0) >= strongest * 0.14:
            strict_count += 1
    for midi in range(FIRST_MIDI, LAST_MIDI + 1):
        if midi < CHROMATIC_TUNE_MIN_MIDI or strict_matches.get(midi, False):
            continue
        raw_level = levels.get(midi, 0.0)
        adjacent_level = max(levels.get(midi - 1, 0.0), levels.get(midi + 1, 0.0))
        local_peak = adjacent_level <= 1.0e-6 or raw_level >= adjacent_level * 0.72
        strong_polyphonic = raw_level >= strongest * 0.30 and local_peak
        isolated_polyphonic_context = strict_count >= 2
        complex_support = has_complex_harmonic_support(levels, midi)
        strong_complex = raw_level >= strongest * 0.30 and local_peak
        fallback_scale = 0.0
        if complex_support and strong_complex:
            fallback_scale = ISOLATED_COMPLEX_TUNING_FALLBACK_SCALE
        elif isolated_polyphonic_context and strong_polyphonic:
            fallback_scale = ISOLATED_COMPLEX_TUNING_FALLBACK_SCALE
        detection_levels[midi] = raw_level * fallback_scale
    return detection_levels


def dominant_analyzer_bass(levels, min_midi=BASS_MIN_MIDI, max_midi=BASS_MAX_MIDI):
    best_midi = -1
    best_score = 0.0
    second_score = 0.0
    total = 0.0
    for midi in range(max(min_midi, FIRST_MIDI), min(max_midi, LAST_MIDI) + 1):
        score = analyzer_bass_score(levels, midi, True, True)
        total += max(score, 0.0)
        if score > best_score:
            second_score = best_score
            best_score = score
            best_midi = midi
        else:
            second_score = max(second_score, score)
    if best_score > 1.0e-6:
        while best_midi - 12 >= min_midi:
            lower = best_midi - 12
            lower_fundamental = levels.get(lower, 0.0)
            current_fundamental = levels.get(best_midi, 0.0)
            lower_score = analyzer_bass_score(levels, lower, True, True)
            if lower_fundamental < current_fundamental * 0.14 or lower_score < best_score * 0.55:
                break
            best_midi = lower
            best_score = lower_score
    best_midi, best_score, second_score = correct_upper_partial_alias(
        levels, best_midi, best_score, second_score, max_midi
    )
    total_conf = best_score / total if total > 1.0e-6 else 0.0
    runner_conf = best_score / (best_score + second_score) if best_score + second_score > 1.0e-6 else 0.0
    return best_midi, min(1.0, max(total_conf, runner_conf * 0.55)), best_score


def correct_upper_partial_alias(levels, midi, score, second_score, max_midi):
    if midi < FIRST_MIDI or midi > ISOLATED_BASS_STRONG_HARMONIC_MAX_MIDI or score <= 1.0e-6:
        return midi, score, second_score
    upper_midi = midi + 19
    if upper_midi > max_midi or upper_midi > LAST_MIDI:
        return midi, score, second_score
    lower_fundamental = levels.get(midi, 0.0)
    upper_fundamental = levels.get(upper_midi, 0.0)
    octave_support = max(levels.get(midi + 12, 0.0), levels.get(midi + 24, 0.0) * 0.80)
    upper_score = analyzer_bass_score(levels, upper_midi, True, False)
    weak_same_pitch_chain = octave_support < max(lower_fundamental * 1.45, upper_fundamental * 0.42)
    upper_dominant = upper_fundamental >= lower_fundamental * 2.30 and upper_fundamental >= octave_support * 2.20
    upper_competitive = upper_score >= score * 0.88 or upper_fundamental >= score * 0.82
    if not weak_same_pitch_chain or not upper_dominant or not upper_competitive:
        return midi, score, second_score
    return upper_midi, upper_score, max(second_score, score)


def normalized_autocorrelation(samples, sample_rate, midi):
    freq = midi_frequency(midi)
    if freq <= 0.0:
        return 0.0
    lag = max(1, int(round(sample_rate / freq)))
    if lag >= len(samples):
        return 0.0
    mean = sum(samples) / len(samples)
    numerator = 0.0
    left = 0.0
    right = 0.0
    for index in range(0, len(samples) - lag):
        a = max(-4.0, min(4.0, samples[index])) - mean
        b = max(-4.0, min(4.0, samples[index + lag])) - mean
        numerator += a * b
        left += a * a
        right += b * b
    if left <= 1.0e-12 or right <= 1.0e-12:
        return 0.0
    return max(0.0, min(1.0, numerator / math.sqrt(left * right)))


def periodic_analyzer_bass(samples, raw_levels, detection_levels, sample_rate,
                           min_midi=BASS_MIN_MIDI, max_midi=BASS_MAX_MIDI):
    strongest = max(
        analyzer_bass_score(raw_levels, midi, True, True)
        for midi in range(max(min_midi, FIRST_MIDI), min(max_midi, LAST_MIDI) + 1)
    )
    if strongest <= 1.0e-6:
        return -1, 0.0, 0.0
    best_midi = -1
    best_score = 0.0
    second_score = 0.0
    best_periodicity = 0.0
    for midi in range(max(min_midi, FIRST_MIDI), min(max_midi, LAST_MIDI) + 1):
        periodicity = normalized_autocorrelation(samples, sample_rate, midi)
        if periodicity < ISOLATED_BASS_PERIODICITY_FLOOR:
            continue
        spectral_score = analyzer_bass_score(raw_levels, midi, True, True)
        spectral_ratio = spectral_score / strongest
        if spectral_ratio < ISOLATED_BASS_PERIODICITY_SPECTRAL_RATIO:
            continue
        score = periodicity * (0.35 + spectral_ratio * 0.65)
        if score > best_score:
            second_score = best_score
            best_score = score
            best_midi = midi
            best_periodicity = periodicity
        else:
            second_score = max(second_score, score)
    if best_midi < 0:
        return -1, 0.0, 0.0
    margin = best_score / (best_score + second_score) if best_score + second_score > 1.0e-6 else 1.0
    confidence = min(1.0, max(best_periodicity * 0.85, margin * 0.58))
    spectral_score = analyzer_bass_score(raw_levels, best_midi, True, True)
    best_midi, spectral_score, _ = correct_upper_partial_alias(
        raw_levels, best_midi, spectral_score, 0.0, max_midi
    )
    return best_midi, confidence, analyzer_bass_score(raw_levels, best_midi, True, True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("wav")
    parser.add_argument("--expected-midi", type=int, required=True)
    parser.add_argument("--min-midi", type=int, default=FIRST_MIDI)
    parser.add_argument("--max-midi", type=int, default=LAST_MIDI)
    parser.add_argument("--target-peak", type=float, default=0.62)
    parser.add_argument("--analyzer-bass", action="store_true")
    args = parser.parse_args()

    sample_rate, samples = read_wav_mono(args.wav)
    window = make_analysis_window(samples, sample_rate, args.target_peak)
    if not window:
        raise SystemExit("silent analysis window")

    levels = {midi: level(window, midi, sample_rate) for midi in range(FIRST_MIDI, LAST_MIDI + 1)}
    detection_levels = analyzer_detection_levels(window, levels, sample_rate)
    ranked_raw = sorted(range(args.min_midi, args.max_midi + 1), key=lambda midi: levels[midi], reverse=True)
    ranked_harmonic = sorted(
        range(args.min_midi, args.max_midi + 1),
        key=lambda midi: harmonic_score(levels, midi),
        reverse=True,
    )
    ranked_bass = sorted(
        range(args.min_midi, args.max_midi + 1),
        key=lambda midi: analyzer_bass_score(detection_levels, midi, True, True),
        reverse=True,
    )

    expected_cents, expected_center, expected_best = tuning_estimate(window, args.expected_midi, sample_rate)
    print(f"{args.wav}")
    print(
        f"expected {note_name(args.expected_midi)} midi {args.expected_midi}: "
        f"raw={levels[args.expected_midi]:.5f} harmonic={harmonic_score(levels, args.expected_midi):.5f} "
        f"analyzer_bass={analyzer_bass_score(detection_levels, args.expected_midi, True, True):.5f} "
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
    if args.analyzer_bass:
        spectral_midi, spectral_conf, spectral_score = dominant_analyzer_bass(
            detection_levels, args.min_midi, args.max_midi
        )
        periodic_midi, periodic_conf, periodic_score = periodic_analyzer_bass(
            window, levels, detection_levels, sample_rate, args.min_midi, args.max_midi
        )
        print(
            "analyzer isolated bass: "
            f"spectral={note_name(spectral_midi) if spectral_midi >= 0 else '--'}/"
            f"{spectral_conf:.3f}/{spectral_score:.5f} "
            f"periodic={note_name(periodic_midi) if periodic_midi >= 0 else '--'}/"
            f"{periodic_conf:.3f}/{periodic_score:.5f}"
        )
        print("top analyzer bass:")
        for midi in ranked_bass[:12]:
            cents, center, best = tuning_estimate(window, midi, sample_rate)
            print(
                f"  {note_name(midi):4s} {midi:3d} raw={levels[midi]:.5f} "
                f"detect={detection_levels[midi]:.5f} bass={analyzer_bass_score(detection_levels, midi, True, True):.5f} "
                f"tuning={cents:+.1f}c center/best={center:.5f}/{best:.5f}"
            )


if __name__ == "__main__":
    main()
