#!/usr/bin/env python3
import csv
import json
import os
import shutil
import sys

import inspect_prepared_multitrack_dataset as inspector
from prepare_slakh_musicnet_fixture import prepare_summed_stem_audio, write_labels


def read_notes(path, default_instrument):
    notes = []
    with open(path, newline="", encoding="utf-8") as note_file:
        reader = csv.DictReader(note_file)
        for row in reader:
            try:
                start = float(row.get("start", row.get("start_time", "")))
                end = float(row.get("end", row.get("end_time", "")))
                midi = int(float(row.get("note", row.get("midi", ""))))
                instrument = int(float(row.get("instrument", default_instrument)))
            except (TypeError, ValueError):
                continue
            if end - start >= 0.035 and 21 <= midi <= 108:
                notes.append((start, end, instrument, midi))
    return notes


def prepare_piece(root, manifest_dir, piece, output_root, output_id, ffmpeg):
    if not isinstance(piece, dict):
        return False, "invalid manifest entry"
    sources = piece.get("sources", [])
    if not isinstance(sources, list) or not sources:
        return False, "missing source entries"

    audio_paths = []
    notes = []
    for index, source in enumerate(sources, start=1):
        if not isinstance(source, dict):
            continue
        audio_path = inspector.resolve_path(root, manifest_dir, str(source.get("audio", "")))
        notes_path = inspector.resolve_path(root, manifest_dir, str(source.get("notes", "")))
        if os.path.isfile(audio_path):
            audio_paths.append(audio_path)
        if os.path.isfile(notes_path):
            default_instrument = int(source.get("instrument", index * 16))
            notes.extend(read_notes(notes_path, default_instrument))

    if len(audio_paths) < 2:
        return False, "not enough source audio tracks"
    if not notes:
        return False, "no usable note rows"

    audio_out = os.path.join(output_root, "train_data", f"{output_id}.wav")
    label_out = os.path.join(output_root, "train_labels", f"{output_id}.csv")
    sample_rate = prepare_summed_stem_audio(audio_paths, audio_out, ffmpeg)
    write_labels(label_out, notes, sample_rate)
    return True, ""


def main(argv):
    if len(argv) != 2:
        print("usage: prepare_prepared_multitrack_musicnet_fixture.py OUT_DIR", file=sys.stderr)
        return 2

    root = inspector.resolve_root()
    if not root:
        print(
            "prepare_prepared_multitrack_musicnet_fixture: set MUSIC_ANALYZER_PREPARED_MULTITRACK_ROOT, "
            "PREPARED_MULTITRACK_PATH, or MUSIC_ANALYZER_DATASET_ROOT",
            file=sys.stderr,
        )
        return 1
    if not os.path.isdir(root):
        print(f"prepare_prepared_multitrack_musicnet_fixture: `{root}` is not a directory", file=sys.stderr)
        return 1

    output_root = argv[1]
    required_pieces = inspector.positive_int_env("MUSIC_ANALYZER_PREPARED_MULTITRACK_REQUIRED_PIECES", 20)
    prepare_pieces = inspector.positive_int_env(
        "MUSIC_ANALYZER_PREPARED_MULTITRACK_PREPARE_PIECES", required_pieces
    )
    min_sources = inspector.positive_int_env("MUSIC_ANALYZER_PREPARED_MULTITRACK_MIN_SOURCES", 4)
    min_seconds = inspector.positive_float_env("MUSIC_ANALYZER_PREPARED_MULTITRACK_MIN_AUDIO_SECONDS", 1.0)
    min_note_rows = inspector.positive_int_env("MUSIC_ANALYZER_PREPARED_MULTITRACK_MIN_NOTE_ROWS", 4)
    min_pitch_classes = inspector.positive_int_env("MUSIC_ANALYZER_PREPARED_MULTITRACK_MIN_PITCH_CLASSES", 3)
    ffmpeg = os.environ.get("FFMPEG") or os.environ.get("MUSIC_ANALYZER_PREPARED_MULTITRACK_FFMPEG") or "ffmpeg"

    try:
        manifest_path, inspected = inspector.complete_entries(
            root, min_sources, min_seconds, min_note_rows, min_pitch_classes
        )
        _, pieces = inspector.load_manifest(root)
    except (OSError, csv.Error, json.JSONDecodeError, UnicodeDecodeError) as exc:
        print(f"prepare_prepared_multitrack_musicnet_fixture: {exc}", file=sys.stderr)
        return 1

    if not manifest_path:
        print(f"prepare_prepared_multitrack_musicnet_fixture: no manifest found under `{root}`", file=sys.stderr)
        return 1

    complete_pieces = [piece for piece, entry in zip(pieces, inspected) if entry["complete"]]
    if len(complete_pieces) < required_pieces:
        print(
            f"prepare_prepared_multitrack_musicnet_fixture: expected at least {required_pieces} complete "
            f"prepared multitrack pieces, got {len(complete_pieces)}",
            file=sys.stderr,
        )
        return 1

    shutil.rmtree(output_root, ignore_errors=True)
    manifest_dir = os.path.dirname(manifest_path)
    prepared = 0
    failures = []
    for piece in complete_pieces:
        if prepared >= prepare_pieces:
            break
        ok, error = prepare_piece(root, manifest_dir, piece, output_root, prepared + 1, ffmpeg)
        if ok:
            prepared += 1
        else:
            failures.append(f"{piece.get('id', '')}: {error}")

    if prepared < required_pieces:
        print(
            f"prepare_prepared_multitrack_musicnet_fixture: expected to prepare {required_pieces} "
            f"prepared multitrack pieces, prepared {prepared}",
            file=sys.stderr,
        )
        for failure in failures[:10]:
            print(f"prepare_prepared_multitrack_musicnet_fixture: {failure}", file=sys.stderr)
        return 1

    print(
        f"prepare_prepared_multitrack_musicnet_fixture: wrote {prepared} MusicNet-shaped "
        f"summed-source prepared multitrack recordings to {output_root}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
