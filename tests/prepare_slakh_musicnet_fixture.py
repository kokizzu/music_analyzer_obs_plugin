#!/usr/bin/env python3
import csv
import os
import shutil
import subprocess
import sys

import inspect_slakh_dataset


def read_be_u16(data, offset):
    return (data[offset] << 8) | data[offset + 1]


def read_be_u32(data, offset):
    return (data[offset] << 24) | (data[offset + 1] << 16) | (data[offset + 2] << 8) | data[offset + 3]


def read_var_len(data, pos, end):
    value = 0
    for _ in range(4):
        if pos >= end:
            raise ValueError("truncated MIDI variable-length value")
        byte = data[pos]
        pos += 1
        value = (value << 7) | (byte & 0x7F)
        if byte & 0x80 == 0:
            return value, pos
    raise ValueError("invalid MIDI variable-length value")


def midi_event_data_length(status):
    event_type = status & 0xF0
    if event_type in (0xC0, 0xD0):
        return 1
    if event_type in (0x80, 0x90, 0xA0, 0xB0, 0xE0):
        return 2
    return -1


def build_tempo_points(tempo_events, division):
    tempo_events = sorted(tempo_events)
    points = [(0, 0.0, 500000)]
    current_tick = 0
    current_seconds = 0.0
    current_tempo = 500000
    for tick, tempo in tempo_events:
        if tick < current_tick:
            continue
        current_seconds += (tick - current_tick) * current_tempo / (division * 1000000.0)
        current_tick = tick
        current_tempo = tempo
        if points[-1][0] == current_tick:
            points[-1] = (current_tick, current_seconds, current_tempo)
        else:
            points.append((current_tick, current_seconds, current_tempo))
    return points


def tick_to_seconds(points, tick, division):
    point = points[0]
    for candidate in points:
        if candidate[0] > tick:
            break
        point = candidate
    point_tick, point_seconds, tempo = point
    return point_seconds + (tick - point_tick) * tempo / (division * 1000000.0)


def parse_midi_notes(path, instrument):
    with open(path, "rb") as midi:
        data = midi.read()
    if len(data) < 14 or data[:4] != b"MThd":
        raise ValueError("not a MIDI file")
    header_len = read_be_u32(data, 4)
    if header_len < 6 or 8 + header_len > len(data):
        raise ValueError("invalid MIDI header")
    track_count = read_be_u16(data, 10)
    division = read_be_u16(data, 12)
    if division & 0x8000:
        raise ValueError("SMPTE MIDI timing is not supported")
    if division <= 0:
        raise ValueError("invalid MIDI division")

    pos = 8 + header_len
    raw_notes = []
    tempo_events = []
    parsed_tracks = 0

    while pos + 8 <= len(data) and parsed_tracks < track_count:
        is_track = data[pos : pos + 4] == b"MTrk"
        chunk_len = read_be_u32(data, pos + 4)
        pos += 8
        if pos + chunk_len > len(data):
            raise ValueError("truncated MIDI chunk")
        chunk_end = pos + chunk_len
        if not is_track:
            pos = chunk_end
            continue

        parsed_tracks += 1
        tick = 0
        running_status = 0
        active_notes = {}

        while pos < chunk_end:
            delta, pos = read_var_len(data, pos, chunk_end)
            tick += delta
            if pos >= chunk_end:
                raise ValueError("truncated MIDI event")

            status = data[pos]
            if status & 0x80:
                pos += 1
                if status < 0xF0:
                    running_status = status
            else:
                if not running_status:
                    raise ValueError("MIDI running status without previous status")
                status = running_status

            if status == 0xFF:
                if pos >= chunk_end:
                    raise ValueError("truncated MIDI meta event")
                meta_type = data[pos]
                pos += 1
                length, pos = read_var_len(data, pos, chunk_end)
                if pos + length > chunk_end:
                    raise ValueError("truncated MIDI meta payload")
                if meta_type == 0x51 and length == 3:
                    tempo = (data[pos] << 16) | (data[pos + 1] << 8) | data[pos + 2]
                    tempo_events.append((tick, tempo))
                pos += length
                continue

            if status in (0xF0, 0xF7):
                length, pos = read_var_len(data, pos, chunk_end)
                if pos + length > chunk_end:
                    raise ValueError("truncated MIDI sysex payload")
                pos += length
                continue

            data_len = midi_event_data_length(status)
            if data_len < 0 or pos + data_len > chunk_end:
                raise ValueError("truncated or unsupported MIDI channel event")
            first = data[pos]
            second = data[pos + 1] if data_len > 1 else 0
            pos += data_len

            channel = status & 0x0F
            key = channel * 128 + first
            event_type = status & 0xF0
            if event_type == 0x90 and second > 0:
                active_notes[key] = tick
            elif event_type == 0x80 or (event_type == 0x90 and second == 0):
                start_tick = active_notes.pop(key, None)
                if start_tick is not None and tick > start_tick:
                    raw_notes.append((start_tick, tick, first, instrument + channel))
        pos = chunk_end

    if not raw_notes:
        return []

    points = build_tempo_points(tempo_events, division)
    notes = []
    for start_tick, end_tick, midi, note_instrument in raw_notes:
        if midi < 21 or midi > 108:
            continue
        start = tick_to_seconds(points, start_tick, division)
        end = tick_to_seconds(points, end_tick, division)
        if end - start < 0.035:
            continue
        notes.append((start, end, note_instrument, midi))
    return notes


def positive_int_env(name, fallback):
    value = os.environ.get(name, "")
    if not value:
        return fallback
    try:
        parsed = int(value)
    except ValueError:
        return fallback
    return parsed if parsed > 0 else fallback


def lower_name(path):
    return os.path.basename(path).lower()


def wav_audio(path):
    return lower_name(path).endswith((".wav", ".wave"))


def collect_midi_sources(track_dir):
    midi_dir = inspect_slakh_dataset.join_path(track_dir, "MIDI")
    if os.path.isdir(midi_dir):
        midi_files = sorted(item for item in inspect_slakh_dataset.walk_files(midi_dir) if inspect_slakh_dataset.is_midi(item))
        if midi_files:
            return midi_files

    all_src = inspect_slakh_dataset.join_path(track_dir, "all_src.mid")
    if os.path.isfile(all_src):
        return [all_src]

    return sorted(item for item in inspect_slakh_dataset.find_midi_files(track_dir) if os.path.basename(item) != "all_src.mid")


def prepare_audio(input_path, output_path, ffmpeg):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    if wav_audio(input_path):
        shutil.copyfile(input_path, output_path)
        return
    subprocess.check_call([ffmpeg, "-nostdin", "-hide_banner", "-loglevel", "error", "-y", "-i", input_path, output_path])


def write_labels(path, notes, sample_rate):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    rows = []
    for start, end, instrument, midi in notes:
        rows.append(
            {
                "start_time": max(0, int(round(start * sample_rate))),
                "end_time": max(0, int(round(end * sample_rate))),
                "instrument": instrument,
                "note": midi,
                "start_beat": 0.0,
                "end_beat": 0.0,
                "note_value": 0.0,
            }
        )
    rows.sort(key=lambda row: (row["start_time"], row["instrument"], row["note"]))
    with open(path, "w", newline="", encoding="utf-8") as label_file:
        writer = csv.DictWriter(
            label_file,
            fieldnames=["start_time", "end_time", "instrument", "note", "start_beat", "end_beat", "note_value"],
        )
        writer.writeheader()
        writer.writerows(rows)


def prepare_track(track, output_root, output_id, ffmpeg):
    audio_files = inspect_slakh_dataset.find_audio_files(track["path"])
    mix_audio = inspect_slakh_dataset.find_mix_audio(audio_files)
    if not mix_audio:
        return False, "missing mix audio"
    summary = inspect_slakh_dataset.audio_summary(mix_audio)
    if not summary:
        return False, "unreadable mix audio"

    midi_sources = collect_midi_sources(track["path"])
    if not midi_sources:
        return False, "missing MIDI sources"

    notes = []
    for index, midi_path in enumerate(midi_sources, start=1):
        try:
            notes.extend(parse_midi_notes(midi_path, index * 16))
        except ValueError as exc:
            return False, f"{midi_path}: {exc}"
    if not notes:
        return False, "no usable MIDI notes"

    audio_out = inspect_slakh_dataset.join_path(output_root, "train_data", f"{output_id}.wav")
    label_out = inspect_slakh_dataset.join_path(output_root, "train_labels", f"{output_id}.csv")
    prepare_audio(mix_audio, audio_out, ffmpeg)
    write_labels(label_out, notes, summary["sample_rate"])
    return True, ""


def main(argv):
    if len(argv) != 2:
        print("usage: prepare_slakh_musicnet_fixture.py OUT_DIR", file=sys.stderr)
        return 2

    root = inspect_slakh_dataset.resolve_root()
    if not root:
        print(
            "prepare_slakh_musicnet_fixture: set MUSIC_ANALYZER_SLAKH_ROOT, SLAKH_PATH, "
            "or MUSIC_ANALYZER_DATASET_ROOT",
            file=sys.stderr,
        )
        return 1
    if not os.path.isdir(root):
        print(f"prepare_slakh_musicnet_fixture: `{root}` is not a directory", file=sys.stderr)
        return 1

    output_root = argv[1]
    required_tracks = positive_int_env("MUSIC_ANALYZER_SLAKH_REQUIRED_TRACKS", 20)
    prepare_tracks = positive_int_env("MUSIC_ANALYZER_SLAKH_PREPARE_TRACKS", required_tracks)
    min_stems = positive_int_env("MUSIC_ANALYZER_SLAKH_MIN_STEMS", 4)
    min_audio_seconds = inspect_slakh_dataset.positive_float_env("MUSIC_ANALYZER_SLAKH_MIN_AUDIO_SECONDS", 1.0)
    ffmpeg = os.environ.get("FFMPEG") or os.environ.get("MUSIC_ANALYZER_SLAKH_FFMPEG") or "ffmpeg"

    required = inspect_slakh_dataset.required_classes()
    track_dirs = inspect_slakh_dataset.candidate_track_dirs(root)
    inspected = [
        inspect_slakh_dataset.inspect_track_dir(path, min_stems, min_audio_seconds, required)
        for path in track_dirs
    ]
    complete = [track for track in inspected if track["complete"]]

    if len(complete) < required_tracks:
        print(
            f"prepare_slakh_musicnet_fixture: expected at least {required_tracks} complete Slakh tracks, "
            f"got {len(complete)}",
            file=sys.stderr,
        )
        return 1

    shutil.rmtree(output_root, ignore_errors=True)
    prepared = 0
    failures = []
    for track in complete:
        if prepared >= prepare_tracks:
            break
        ok, error = prepare_track(track, output_root, prepared + 1, ffmpeg)
        if ok:
            prepared += 1
        else:
            failures.append(f"{track['path']}: {error}")

    if prepared < required_tracks:
        print(
            f"prepare_slakh_musicnet_fixture: expected to prepare {required_tracks} Slakh tracks, "
            f"prepared {prepared}",
            file=sys.stderr,
        )
        for failure in failures[:10]:
            print(f"prepare_slakh_musicnet_fixture: {failure}", file=sys.stderr)
        return 1

    print(
        f"prepare_slakh_musicnet_fixture: wrote {prepared} MusicNet-shaped Slakh recordings to {output_root}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
