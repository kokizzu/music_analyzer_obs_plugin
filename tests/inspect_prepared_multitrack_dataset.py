#!/usr/bin/env python3
import csv
import json
import math
import os
import struct
import sys
import wave


PREPARED_CHILD_NAMES = (
    "prepared-multitrack",
    "prepared_multitrack",
    "PreparedMultitrack",
    "eep-prepared",
    "direct-fit-small-prepared",
)


def positive_int_env(name, fallback):
    value = os.environ.get(name, "")
    if not value:
        return fallback
    try:
        parsed = int(value)
    except ValueError:
        return fallback
    return parsed if parsed > 0 else fallback


def positive_float_env(name, fallback):
    value = os.environ.get(name, "")
    if not value:
        return fallback
    try:
        parsed = float(value)
    except ValueError:
        return fallback
    return parsed if parsed > 0.0 else fallback


def join_path(lhs, *children):
    path = lhs
    for child in children:
        path = os.path.join(path, child)
    return path


def resolve_root():
    root = os.environ.get("MUSIC_ANALYZER_PREPARED_MULTITRACK_ROOT") or os.environ.get(
        "PREPARED_MULTITRACK_PATH"
    )
    if root:
        return root

    dataset_root = os.environ.get("MUSIC_ANALYZER_DATASET_ROOT", "")
    if not dataset_root:
        return ""
    for child in PREPARED_CHILD_NAMES:
        candidate = join_path(dataset_root, child)
        if os.path.isdir(candidate):
            return candidate
    return ""


def resolve_path(root, base, path):
    if not path:
        return ""
    if os.path.isabs(path):
        return path
    for candidate in (join_path(base, path), join_path(root, path)):
        if os.path.exists(candidate):
            return candidate
    return join_path(base, path)


def manifest_path(root):
    for name in ("manifest.json", "prepared_multitrack_manifest.json", "mtracks_info.json"):
        candidate = join_path(root, name)
        if os.path.isfile(candidate):
            return candidate
    return ""


def load_manifest(root):
    path = manifest_path(root)
    if not path:
        return "", []
    with open(path, "r", encoding="utf-8") as manifest_file:
        data = json.load(manifest_file)
    pieces = data.get("pieces", []) if isinstance(data, dict) else []
    return path, pieces if isinstance(pieces, list) else []


def wav_summary(path):
    try:
        with wave.open(path, "rb") as audio:
            rate = audio.getframerate()
            frames = audio.getnframes()
            channels = audio.getnchannels()
            if rate <= 0 or frames <= 0 or channels <= 0:
                return None
            return {"duration": frames / float(rate), "channels": channels, "sample_rate": rate}
    except (OSError, EOFError, wave.Error):
        pass
    try:
        with open(path, "rb") as audio:
            if audio.read(4) != b"RIFF":
                return None
            audio.read(4)
            if audio.read(4) != b"WAVE":
                return None
            channels = rate = block_align = frames = 0
            while True:
                chunk = audio.read(8)
                if len(chunk) != 8:
                    break
                kind, size = struct.unpack("<4sI", chunk)
                data = audio.read(size)
                if size % 2:
                    audio.read(1)
                if kind == b"fmt " and len(data) >= 16:
                    _, channels, rate, _, block_align, _ = struct.unpack("<HHIIHH", data[:16])
                elif kind == b"data" and block_align:
                    frames = size // block_align
                    break
            if rate > 0 and frames > 0 and channels > 0:
                return {"duration": frames / float(rate), "channels": channels, "sample_rate": rate}
    except OSError:
        pass
    return None


def read_note_rows(path):
    rows = []
    with open(path, newline="", encoding="utf-8") as note_file:
        reader = csv.DictReader(note_file)
        for row in reader:
            try:
                start = float(row.get("start", row.get("start_time", "")))
                end = float(row.get("end", row.get("end_time", "")))
                note = int(float(row.get("note", row.get("midi", ""))))
            except (TypeError, ValueError):
                continue
            if end > start and 21 <= note <= 108:
                rows.append((start, end, note))
    return rows


def inspect_piece(root, manifest_dir, piece, min_sources, min_seconds, min_note_rows, min_pitch_classes):
    if not isinstance(piece, dict):
        piece = {}
    sources = piece.get("sources", [])
    if not isinstance(sources, list):
        sources = []

    readable_sources = 0
    note_sources = 0
    note_rows = 0
    pitch_classes = set()
    durations = []
    for source in sources:
        if not isinstance(source, dict):
            continue
        audio_path = resolve_path(root, manifest_dir, str(source.get("audio", "")))
        notes_path = resolve_path(root, manifest_dir, str(source.get("notes", "")))
        summary = wav_summary(audio_path)
        if summary and summary["duration"] >= min_seconds:
            readable_sources += 1
            durations.append(summary["duration"])
        if os.path.isfile(notes_path):
            rows = read_note_rows(notes_path)
            if rows:
                note_sources += 1
            note_rows += len(rows)
            for _, _, note in rows:
                pitch_classes.add(note % 12)

    complete = (
        readable_sources >= min_sources
        and note_sources >= min_sources
        and note_rows >= min_note_rows
        and len(pitch_classes) >= min_pitch_classes
    )
    return {
        "id": str(piece.get("id", "")),
        "complete": complete,
        "sources": readable_sources,
        "note_sources": note_sources,
        "note_rows": note_rows,
        "pitch_classes": len(pitch_classes),
        "duration": min(durations) if durations else 0.0,
    }


def range_summary(values, label):
    if not values:
        return f"{label} min/avg/max 0/0.00/0"
    return f"{label} min/avg/max {min(values)}/{sum(values) / len(values):.2f}/{max(values)}"


def float_range_summary(values, label):
    if not values:
        return f"{label} min/avg/max 0.00/0.00/0.00"
    return f"{label} min/avg/max {min(values):.2f}/{sum(values) / len(values):.2f}/{max(values):.2f}"


def complete_entries(root, min_sources, min_seconds, min_note_rows, min_pitch_classes):
    path, pieces = load_manifest(root)
    if not path:
        return "", []
    base = os.path.dirname(path)
    inspected = [
        inspect_piece(root, base, piece, min_sources, min_seconds, min_note_rows, min_pitch_classes)
        for piece in pieces
    ]
    return path, inspected


def main():
    root = resolve_root()
    if not root:
        print(
            "inspect_prepared_multitrack_dataset: set MUSIC_ANALYZER_PREPARED_MULTITRACK_ROOT, "
            "PREPARED_MULTITRACK_PATH, or MUSIC_ANALYZER_DATASET_ROOT",
            file=sys.stderr,
        )
        return 1
    if not os.path.isdir(root):
        print(f"inspect_prepared_multitrack_dataset: `{root}` is not a directory", file=sys.stderr)
        return 1

    required_pieces = positive_int_env("MUSIC_ANALYZER_PREPARED_MULTITRACK_REQUIRED_PIECES", 20)
    min_sources = positive_int_env("MUSIC_ANALYZER_PREPARED_MULTITRACK_MIN_SOURCES", 4)
    min_seconds = positive_float_env("MUSIC_ANALYZER_PREPARED_MULTITRACK_MIN_AUDIO_SECONDS", 1.0)
    min_note_rows = positive_int_env("MUSIC_ANALYZER_PREPARED_MULTITRACK_MIN_NOTE_ROWS", 4)
    min_pitch_classes = positive_int_env("MUSIC_ANALYZER_PREPARED_MULTITRACK_MIN_PITCH_CLASSES", 3)

    try:
        path, inspected = complete_entries(root, min_sources, min_seconds, min_note_rows, min_pitch_classes)
    except (OSError, csv.Error, json.JSONDecodeError, UnicodeDecodeError) as exc:
        print(f"inspect_prepared_multitrack_dataset: {exc}", file=sys.stderr)
        return 1

    if not path:
        print(f"inspect_prepared_multitrack_dataset: no manifest found under `{root}`", file=sys.stderr)
        return 1

    complete = [entry for entry in inspected if entry["complete"]]
    if len(complete) < required_pieces:
        print(
            f"inspect_prepared_multitrack_dataset: expected at least {required_pieces} complete "
            f"prepared multitrack pieces, got {len(complete)} from {len(inspected)} entries in {path}",
            file=sys.stderr,
        )
        return 1

    print(
        "inspect_prepared_multitrack_dataset: "
        f"complete={len(complete)}/{len(inspected)} manifest={path}, "
        f"{range_summary([entry['sources'] for entry in complete], 'source audio tracks per piece')}, "
        f"{range_summary([entry['note_sources'] for entry in complete], 'note-bearing sources per piece')}, "
        f"{range_summary([entry['note_rows'] for entry in complete], 'note rows per piece')}, "
        f"{range_summary([entry['pitch_classes'] for entry in complete], 'pitch classes per piece')}, "
        f"{float_range_summary([entry['duration'] for entry in complete], 'audio seconds')}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
