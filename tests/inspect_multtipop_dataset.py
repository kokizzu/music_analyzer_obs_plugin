#!/usr/bin/env python3
import json
import os
import struct
import sys


AUDIO_EXTENSIONS = (".wav", ".wave", ".flac", ".mp3", ".m4a", ".ogg")
MULTTIPOP_CHILD_NAMES = (
    "MulTTiPop",
    "multtipop",
    "gclef-cmu-multtipop",
    "gclef-cmu_multtipop",
    os.path.join("gclef-cmu", "multtipop"),
)


def truthy(name):
    value = os.environ.get(name, "")
    return value and value not in ("0", "false", "FALSE")


def positive_int_env(name, fallback):
    value = os.environ.get(name, "")
    if not value:
        return fallback
    try:
        parsed = int(value)
    except ValueError:
        return fallback
    return parsed if parsed > 0 else fallback


def join_path(lhs, rhs):
    return os.path.join(lhs, rhs)


def resolve_root():
    root = os.environ.get("MUSIC_ANALYZER_MULTTIPOP_ROOT") or os.environ.get("MULTTIPOP_PATH")
    if root:
        return root

    dataset_root = os.environ.get("MUSIC_ANALYZER_DATASET_ROOT")
    if not dataset_root:
        return ""

    for child in MULTTIPOP_CHILD_NAMES:
        candidate = join_path(dataset_root, child)
        if os.path.isdir(candidate):
            return candidate
    return ""


def range_summary(values, label):
    if not values:
        return f"{label} min/avg/max 0/0.00/0"
    return f"{label} min/avg/max {min(values)}/{sum(values) / len(values):.2f}/{max(values)}"


def read_vlq(data, pos, end):
    value = 0
    for _ in range(4):
        if pos >= end:
            raise ValueError("truncated variable-length quantity")
        byte = data[pos]
        pos += 1
        value = (value << 7) | (byte & 0x7F)
        if byte < 0x80:
            return value, pos
    raise ValueError("invalid variable-length quantity")


def read_u16(data, pos):
    if pos + 2 > len(data):
        raise ValueError("truncated uint16")
    return struct.unpack(">H", data[pos:pos + 2])[0]


def read_u32(data, pos):
    if pos + 4 > len(data):
        raise ValueError("truncated uint32")
    return struct.unpack(">I", data[pos:pos + 4])[0]


def midi_event_data_length(status):
    event_type = status & 0xF0
    if event_type in (0xC0, 0xD0):
        return 1
    if event_type in (0x80, 0x90, 0xA0, 0xB0, 0xE0):
        return 2
    raise ValueError(f"unsupported MIDI status 0x{status:02x}")


def inspect_midi(path):
    with open(path, "rb") as midi_file:
        data = midi_file.read()
    if len(data) < 14 or data[:4] != b"MThd":
        raise ValueError("not a MIDI file")

    header_len = read_u32(data, 4)
    if header_len < 6 or 8 + header_len > len(data):
        raise ValueError("invalid MIDI header")
    midi_format = read_u16(data, 8)
    declared_tracks = read_u16(data, 10)

    pos = 8 + header_len
    note_count = 0
    note_tracks = set()
    note_channels = set()
    pitch_classes = set()
    parsed_tracks = 0

    while pos + 8 <= len(data):
        chunk_id = data[pos:pos + 4]
        chunk_len = read_u32(data, pos + 4)
        pos += 8
        chunk_end = pos + chunk_len
        if chunk_end > len(data):
            raise ValueError("truncated MIDI track chunk")
        if chunk_id != b"MTrk":
            pos = chunk_end
            continue

        parsed_tracks += 1
        track_index = parsed_tracks - 1
        running_status = 0
        while pos < chunk_end:
            _delta, pos = read_vlq(data, pos, chunk_end)
            if pos >= chunk_end:
                raise ValueError("truncated MIDI event")

            status = data[pos]
            if status >= 0x80:
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
                pos += 1
                length, pos = read_vlq(data, pos, chunk_end)
                pos += length
                if pos > chunk_end:
                    raise ValueError("truncated MIDI meta payload")
                continue

            if status in (0xF0, 0xF7):
                length, pos = read_vlq(data, pos, chunk_end)
                pos += length
                if pos > chunk_end:
                    raise ValueError("truncated MIDI sysex payload")
                continue

            data_len = midi_event_data_length(status)
            if pos + data_len > chunk_end:
                raise ValueError("truncated MIDI channel event")
            payload = data[pos:pos + data_len]
            pos += data_len

            if (status & 0xF0) == 0x90 and payload[1] > 0:
                note_count += 1
                note_tracks.add(track_index)
                note_channels.add(status & 0x0F)
                pitch_classes.add(payload[0] % 12)

        pos = chunk_end

    if parsed_tracks == 0:
        raise ValueError("no MIDI track chunks")

    return {
        "format": midi_format,
        "declared_tracks": declared_tracks,
        "parsed_tracks": parsed_tracks,
        "note_count": note_count,
        "note_parts": max(len(note_tracks), len(note_channels)),
        "pitch_classes": len(pitch_classes),
    }


def valid_youtube_metadata(meta):
    youtube = meta.get("youtube", {})
    if not isinstance(youtube, dict):
        return False
    video_id = youtube.get("id") or youtube.get("ytid")
    start = youtube.get("start")
    end = youtube.get("end")
    return bool(video_id) and isinstance(start, (int, float)) and isinstance(end, (int, float)) and end > start


def segment_id_from_meta(path, meta):
    return str(meta.get("id") or os.path.basename(os.path.dirname(path)))


def audio_file_candidates(segment_dir, segment_id, split):
    audio_root = os.environ.get("MUSIC_ANALYZER_MULTTIPOP_AUDIO_ROOT", "")
    roots = [segment_dir]
    if audio_root:
        roots.extend([
            audio_root,
            join_path(audio_root, segment_id),
            join_path(join_path(audio_root, split), segment_id),
        ])

    candidates = []
    for root in roots:
        for stem in ("audio", "segment", segment_id):
            for extension in AUDIO_EXTENSIONS:
                candidates.append(join_path(root, stem + extension))
    return candidates


def has_audio_segment(segment_dir, segment_id, split):
    return any(os.path.isfile(path) for path in audio_file_candidates(segment_dir, segment_id, split))


def collect_segment_dirs(root):
    segment_dirs = []
    for split in ("dev", "test"):
        split_dir = join_path(root, split)
        if not os.path.isdir(split_dir):
            continue
        for name in sorted(os.listdir(split_dir)):
            segment_dir = join_path(split_dir, name)
            if os.path.isdir(segment_dir):
                segment_dirs.append((split, segment_dir))
    return segment_dirs


def inspect_segment(split, segment_dir):
    midi_path = join_path(segment_dir, "aligned.mid")
    meta_path = join_path(segment_dir, "meta.json")
    if not os.path.isfile(midi_path) or not os.path.isfile(meta_path):
        return {"complete": False, "reason": "missing aligned.mid or meta.json"}

    with open(meta_path, "r", encoding="utf-8") as meta_file:
        meta = json.load(meta_file)
    if not valid_youtube_metadata(meta):
        return {"complete": False, "reason": "invalid YouTube timing metadata"}

    midi = inspect_midi(midi_path)
    segment_id = segment_id_from_meta(meta_path, meta)
    return {
        "complete": True,
        "split": split,
        "id": segment_id,
        "midi": midi,
        "has_audio": has_audio_segment(segment_dir, segment_id, split),
    }


def main():
    root = resolve_root()
    if not root:
        print(
            "inspect_multtipop_dataset: set MUSIC_ANALYZER_MULTTIPOP_ROOT, MULTTIPOP_PATH, "
            "or MUSIC_ANALYZER_DATASET_ROOT",
            file=sys.stderr,
        )
        return 1
    if not os.path.isdir(root):
        print(f"inspect_multtipop_dataset: `{root}` is not a directory", file=sys.stderr)
        return 1

    required_segments = positive_int_env("MUSIC_ANALYZER_MULTTIPOP_REQUIRED_SEGMENTS", 20)
    min_note_parts = positive_int_env("MUSIC_ANALYZER_MULTTIPOP_MIN_NOTE_PARTS", 2)
    min_pitch_classes = positive_int_env("MUSIC_ANALYZER_MULTTIPOP_MIN_PITCH_CLASSES", 2)
    require_audio = truthy("MUSIC_ANALYZER_MULTTIPOP_REQUIRE_AUDIO")

    inspected = []
    failures = []
    for split, segment_dir in collect_segment_dirs(root):
        try:
            result = inspect_segment(split, segment_dir)
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            failures.append(f"{segment_dir}: {exc}")
            continue
        if result["complete"]:
            midi = result["midi"]
            if midi["note_parts"] < min_note_parts:
                failures.append(f"{segment_dir}: expected {min_note_parts}+ note-bearing MIDI parts")
                continue
            if midi["pitch_classes"] < min_pitch_classes:
                failures.append(f"{segment_dir}: expected {min_pitch_classes}+ pitch classes")
                continue
        inspected.append(result)

    complete = [segment for segment in inspected if segment["complete"]]
    audio_segments = [segment for segment in complete if segment["has_audio"]]
    if require_audio:
        complete = audio_segments

    split_counts = {}
    for segment in complete:
        split_counts[segment["split"]] = split_counts.get(segment["split"], 0) + 1
    split_summary = ",".join(f"{split}:{split_counts.get(split, 0)}" for split in ("dev", "test"))

    note_parts = [segment["midi"]["note_parts"] for segment in complete]
    note_counts = [segment["midi"]["note_count"] for segment in complete]
    pitch_classes = [segment["midi"]["pitch_classes"] for segment in complete]

    print(
        "inspect_multtipop_dataset: "
        f"root={root} discovered_segments={len(inspected)} complete_segments={len(complete)} "
        f"audio_segments={len(audio_segments)} splits={split_summary} "
        f"{range_summary(note_parts, 'midi note parts')} "
        f"{range_summary(note_counts, 'midi notes')} "
        f"{range_summary(pitch_classes, 'pitch classes')}"
    )

    if len(complete) < required_segments:
        audio_suffix = " with local audio files" if require_audio else ""
        print(
            f"inspect_multtipop_dataset: expected at least {required_segments} complete segments"
            f"{audio_suffix}, got {len(complete)}",
            file=sys.stderr,
        )
        for failure in failures[:5]:
            print(f"inspect_multtipop_dataset: {failure}", file=sys.stderr)
        return 1

    if require_audio:
        print(
            "inspect_multtipop_dataset: local audio segments are present; run "
            "make test-real-multtipop-20 for audio-backed real-pop note/chord evaluation"
        )
    else:
        print(
            "inspect_multtipop_dataset: note this is a multitrack-MIDI metadata preflight; "
            "MulTTiPop references commercial audio by YouTube ID/timestamps, so local audio "
            "segments are optional and it does not replace the URMP same-song stem gate"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
