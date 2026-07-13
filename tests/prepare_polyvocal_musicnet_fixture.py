#!/usr/bin/env python3
import csv
import json
import math
import os
import shutil
import subprocess
import struct
import sys
import tempfile
import wave

import inspect_polyvocal_dataset
from prepare_slakh_musicnet_fixture import write_labels


DEFAULT_OUTPUT_SAMPLE_RATE = 44100


def median(values, fallback):
    if not values:
        return fallback
    ordered = sorted(values)
    middle = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[middle]
    return (ordered[middle - 1] + ordered[middle]) / 2.0


def hz_to_midi(freq):
    if freq <= 0.0:
        return -1
    midi = int(round(69.0 + 12.0 * math.log(freq / 440.0, 2.0)))
    return midi if 21 <= midi <= 108 else -1


def value_frequency(value):
    if isinstance(value, dict):
        for key in ("frequency", "freq", "f0", "hz", "pitch", "value"):
            raw = value.get(key)
            if isinstance(raw, (int, float)):
                return float(raw)
    if isinstance(value, (int, float)):
        return float(value)
    return 0.0


def read_json_f0_points(path):
    with open(path, "r", encoding="utf-8") as annotation_file:
        document = json.load(annotation_file)
    annotations = document.get("annotations", []) if isinstance(document, dict) else []
    points = []
    for annotation in annotations:
        data = annotation.get("data", []) if isinstance(annotation, dict) else []
        for item in data:
            if not isinstance(item, dict):
                continue
            time_value = item.get("time")
            if not isinstance(time_value, (int, float)) or time_value < 0.0:
                continue
            freq = value_frequency(item.get("value"))
            if freq > 0.0:
                points.append((float(time_value), freq))
    return points


def numeric_csv_columns(header):
    if not header:
        return 0, 1
    lowered = [item.strip().lower() for item in header]
    time_index = 0
    freq_index = 1
    for name in ("time", "timestamp", "seconds", "sec"):
        if name in lowered:
            time_index = lowered.index(name)
            break
    for name in ("frequency", "freq", "f0", "hz", "pitch"):
        if name in lowered:
            freq_index = lowered.index(name)
            break
    return time_index, freq_index


def read_csv_f0_points(path):
    points = []
    header = None
    time_index = 0
    freq_index = 1
    with open(path, newline="", encoding="utf-8") as annotation_file:
        reader = csv.reader(annotation_file)
        for row in reader:
            if not row:
                continue
            stripped = [cell.strip() for cell in row]
            try:
                time_value = float(stripped[time_index])
                freq_value = float(stripped[freq_index])
            except (IndexError, ValueError):
                if header is None:
                    header = stripped
                    time_index, freq_index = numeric_csv_columns(header)
                continue
            if time_value >= 0.0 and freq_value > 0.0:
                points.append((time_value, freq_value))
    return points


def read_f0_points(path):
    if inspect_polyvocal_dataset.lower_name(path).endswith((".jams", ".json")):
        return read_json_f0_points(path)
    return read_csv_f0_points(path)


def points_to_notes(points, instrument, min_duration=0.08, max_gap=0.12):
    ordered = sorted((time, hz_to_midi(freq)) for time, freq in points)
    ordered = [(time, midi) for time, midi in ordered if midi > 0]
    if not ordered:
        return []

    deltas = [
        ordered[index + 1][0] - ordered[index][0]
        for index in range(len(ordered) - 1)
        if 0.0 < ordered[index + 1][0] - ordered[index][0] <= 0.25
    ]
    frame_step = min(0.10, max(0.01, median(deltas, 0.05)))

    notes = []
    current_midi = ordered[0][1]
    start = ordered[0][0]
    previous_time = ordered[0][0]

    for time_value, midi in ordered[1:]:
        gap = time_value - previous_time
        if midi != current_midi or gap > max_gap:
            end = previous_time + frame_step
            if end - start >= min_duration:
                notes.append((start, end, instrument, current_midi))
            start = time_value
            current_midi = midi
        previous_time = time_value

    end = previous_time + frame_step
    if end - start >= min_duration:
        notes.append((start, end, instrument, current_midi))
    return notes


def read_wav_sample_rate(path):
    try:
        with wave.open(path, "rb") as audio:
            return audio.getframerate()
    except (OSError, EOFError, wave.Error):
        return 0


def read_wav_float_mono(path):
    with wave.open(path, "rb") as audio:
        sample_rate = audio.getframerate()
        channels = audio.getnchannels()
        width = audio.getsampwidth()
        frames = audio.getnframes()
        if sample_rate <= 0 or channels <= 0 or width != 2:
            raise wave.Error("expected 16-bit PCM WAV audio")
        raw = audio.readframes(frames)
    values = struct.unpack("<" + "h" * (len(raw) // 2), raw)
    samples = []
    for index in range(0, len(values), channels):
        frame_values = values[index : index + channels]
        samples.append(sum(frame_values) / float(32767 * max(1, len(frame_values))))
    return sample_rate, samples


def write_wav_float_mono(path, sample_rate, samples):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with wave.open(path, "wb") as audio:
        audio.setnchannels(1)
        audio.setsampwidth(2)
        audio.setframerate(sample_rate)
        frames = bytearray()
        for sample in samples:
            frames.extend(struct.pack("<h", int(max(-0.95, min(0.95, sample)) * 32767.0)))
        audio.writeframes(bytes(frames))


def decode_to_mono_wav(input_path, output_path, ffmpeg):
    command = [
        ffmpeg,
        "-nostdin",
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        "-i",
        input_path,
        "-ac",
        "1",
        "-ar",
        str(DEFAULT_OUTPUT_SAMPLE_RATE),
        output_path,
    ]
    subprocess.check_call(command)


def read_source_track(path, ffmpeg, temp_dir, index):
    try:
        sample_rate, samples = read_wav_float_mono(path)
        if sample_rate == DEFAULT_OUTPUT_SAMPLE_RATE:
            return samples
    except (OSError, EOFError, wave.Error, struct.error):
        pass

    decoded = inspect_polyvocal_dataset.join_path(temp_dir, f"source{index:02d}.wav")
    decode_to_mono_wav(path, decoded, ffmpeg)
    _, samples = read_wav_float_mono(decoded)
    return samples


def prepare_summed_source_audio(source_paths, output_path, ffmpeg):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with tempfile.TemporaryDirectory() as temp_dir:
        tracks = [
            read_source_track(path, ffmpeg, temp_dir, index)
            for index, path in enumerate(source_paths, start=1)
        ]
    if not tracks:
        raise ValueError("no source audio tracks to sum")

    frame_count = max(len(track) for track in tracks)
    gain = 1.0 / math.sqrt(len(tracks))
    mixed = []
    for frame in range(frame_count):
        sample = 0.0
        for track in tracks:
            if frame < len(track):
                sample += track[frame]
        mixed.append(sample * gain)
    write_wav_float_mono(output_path, DEFAULT_OUTPUT_SAMPLE_RATE, mixed)
    return DEFAULT_OUTPUT_SAMPLE_RATE


def prepare_audio(input_path, output_path, ffmpeg):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    if inspect_polyvocal_dataset.lower_name(input_path).endswith((".wav", ".wave")):
        shutil.copyfile(input_path, output_path)
        sample_rate = read_wav_sample_rate(output_path)
        if sample_rate:
            return sample_rate

    command = [
        ffmpeg,
        "-nostdin",
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        "-i",
        input_path,
        "-ac",
        "1",
        "-ar",
        str(DEFAULT_OUTPUT_SAMPLE_RATE),
        output_path,
    ]
    subprocess.check_call(command)
    return DEFAULT_OUTPUT_SAMPLE_RATE


def prepare_entry(entry, output_root, output_id, ffmpeg):
    if not entry["complete"]:
        return False, "incomplete entry"

    notes = []
    for voice_index, annotation in enumerate(entry["annotations"], start=1):
        try:
            points = read_f0_points(annotation)
        except (OSError, csv.Error, json.JSONDecodeError, UnicodeDecodeError) as exc:
            return False, f"{annotation}: {exc}"
        notes.extend(points_to_notes(points, 96 + voice_index))

    if not notes:
        return False, "no usable F0-derived note intervals"

    audio_out = inspect_polyvocal_dataset.join_path(output_root, "train_data", f"{output_id}.wav")
    label_out = inspect_polyvocal_dataset.join_path(output_root, "train_labels", f"{output_id}.csv")
    source_paths = [
        path
        for path in entry.get("source_audio_paths", [])
        if os.path.isfile(path) and inspect_polyvocal_dataset.is_audio(path)
    ]
    if len(source_paths) >= len(entry["annotations"]):
        sample_rate = prepare_summed_source_audio(source_paths, audio_out, ffmpeg)
    else:
        sample_rate = prepare_audio(entry["audio_path"], audio_out, ffmpeg)
    write_labels(label_out, notes, sample_rate)
    return True, ""


def main(argv):
    if len(argv) != 2:
        print("usage: prepare_polyvocal_musicnet_fixture.py OUT_DIR", file=sys.stderr)
        return 2

    root = inspect_polyvocal_dataset.resolve_root()
    if not root:
        print(
            "prepare_polyvocal_musicnet_fixture: set MUSIC_ANALYZER_POLYVOCAL_ROOT, "
            "POLYVOCAL_PATH, or MUSIC_ANALYZER_DATASET_ROOT",
            file=sys.stderr,
        )
        return 1
    if not os.path.isdir(root):
        print(f"prepare_polyvocal_musicnet_fixture: `{root}` is not a directory", file=sys.stderr)
        return 1

    output_root = argv[1]
    required_pieces = inspect_polyvocal_dataset.positive_int_env("MUSIC_ANALYZER_POLYVOCAL_REQUIRED_PIECES", 20)
    prepare_pieces = inspect_polyvocal_dataset.positive_int_env(
        "MUSIC_ANALYZER_POLYVOCAL_PREPARE_PIECES", required_pieces
    )
    min_voices = inspect_polyvocal_dataset.positive_int_env("MUSIC_ANALYZER_POLYVOCAL_MIN_VOICES", 4)
    min_audio_seconds = inspect_polyvocal_dataset.positive_float_env(
        "MUSIC_ANALYZER_POLYVOCAL_MIN_AUDIO_SECONDS", 1.0
    )
    min_f0_points = inspect_polyvocal_dataset.positive_int_env("MUSIC_ANALYZER_POLYVOCAL_MIN_F0_POINTS", 4)
    ffmpeg = os.environ.get("FFMPEG") or os.environ.get("MUSIC_ANALYZER_POLYVOCAL_FFMPEG") or "ffmpeg"

    try:
        _, inspected = inspect_polyvocal_dataset.complete_entries(root, min_voices, min_audio_seconds, min_f0_points)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"prepare_polyvocal_musicnet_fixture: {exc}", file=sys.stderr)
        return 1
    complete = [entry for entry in inspected if entry["complete"]]

    if len(complete) < required_pieces:
        print(
            f"prepare_polyvocal_musicnet_fixture: expected at least {required_pieces} complete "
            f"vocal ensemble mixes, got {len(complete)}",
            file=sys.stderr,
        )
        return 1

    shutil.rmtree(output_root, ignore_errors=True)
    prepared = 0
    failures = []
    for entry in complete:
        if prepared >= prepare_pieces:
            break
        ok, error = prepare_entry(entry, output_root, prepared + 1, ffmpeg)
        if ok:
            prepared += 1
        else:
            failures.append(f"{entry['audio_name']}: {error}")

    if prepared < required_pieces:
        print(
            f"prepare_polyvocal_musicnet_fixture: expected to prepare {required_pieces} "
            f"vocal ensemble mixes, prepared {prepared}",
            file=sys.stderr,
        )
        for failure in failures[:10]:
            print(f"prepare_polyvocal_musicnet_fixture: {failure}", file=sys.stderr)
        return 1

    print(
        f"prepare_polyvocal_musicnet_fixture: wrote {prepared} MusicNet-shaped "
        f"real vocal-F0 recordings to {output_root}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
