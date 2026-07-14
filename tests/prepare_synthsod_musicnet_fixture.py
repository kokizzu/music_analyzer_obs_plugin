#!/usr/bin/env python3
import os
import shutil
import sys

import inspect_synthsod_dataset
from prepare_slakh_musicnet_fixture import prepare_summed_stem_audio, write_labels


def prepare_piece(piece, output_root, output_id, ffmpeg):
    source_audio = inspect_synthsod_dataset.source_audio_files(piece["path"])
    if len(source_audio) < 2:
        return False, "not enough source audio tracks"
    notes = inspect_synthsod_dataset.read_score_notes(piece["score_path"])
    if not notes:
        return False, "no usable aligned score notes"

    audio_out = inspect_synthsod_dataset.join_path(output_root, "train_data", f"{output_id}.wav")
    label_out = inspect_synthsod_dataset.join_path(output_root, "train_labels", f"{output_id}.csv")
    sample_rate = prepare_summed_stem_audio(source_audio, audio_out, ffmpeg)
    write_labels(label_out, notes, sample_rate)
    return True, ""


def main(argv):
    if len(argv) != 2:
        print("usage: prepare_synthsod_musicnet_fixture.py OUT_DIR", file=sys.stderr)
        return 2

    audio_root = inspect_synthsod_dataset.resolve_audio_root()
    if not audio_root:
        print(
            "prepare_synthsod_musicnet_fixture: set MUSIC_ANALYZER_SYNTHSOD_ROOT, SYNTHSOD_PATH, "
            "or MUSIC_ANALYZER_DATASET_ROOT",
            file=sys.stderr,
        )
        return 1
    scores_root = inspect_synthsod_dataset.resolve_scores_root(audio_root)
    if not scores_root:
        print(
            "prepare_synthsod_musicnet_fixture: set MUSIC_ANALYZER_SYNTHSOD_SCORES_ROOT, "
            "SYNTHSOD_SCORES_PATH, or place SynthSOD aligned scores near the audio root",
            file=sys.stderr,
        )
        return 1

    output_root = argv[1]
    required_pieces = inspect_synthsod_dataset.positive_int_env("MUSIC_ANALYZER_SYNTHSOD_REQUIRED_PIECES", 20)
    prepare_pieces = inspect_synthsod_dataset.positive_int_env(
        "MUSIC_ANALYZER_SYNTHSOD_PREPARE_PIECES", required_pieces
    )
    min_sources = inspect_synthsod_dataset.positive_int_env("MUSIC_ANALYZER_SYNTHSOD_MIN_SOURCES", 4)
    min_audio_seconds = inspect_synthsod_dataset.positive_float_env("MUSIC_ANALYZER_SYNTHSOD_MIN_AUDIO_SECONDS", 1.0)
    min_note_rows = inspect_synthsod_dataset.positive_int_env("MUSIC_ANALYZER_SYNTHSOD_MIN_NOTE_ROWS", 4)
    min_pitch_classes = inspect_synthsod_dataset.positive_int_env("MUSIC_ANALYZER_SYNTHSOD_MIN_PITCH_CLASSES", 3)
    ffmpeg = os.environ.get("FFMPEG") or os.environ.get("MUSIC_ANALYZER_SYNTHSOD_FFMPEG") or "ffmpeg"

    try:
        inspected = inspect_synthsod_dataset.inspected_pieces(
            audio_root, scores_root, min_sources, min_audio_seconds, min_note_rows, min_pitch_classes
        )
    except (OSError, UnicodeDecodeError) as exc:
        print(f"prepare_synthsod_musicnet_fixture: {exc}", file=sys.stderr)
        return 1

    complete = [piece for piece in inspected if piece["complete"]]
    if len(complete) < required_pieces:
        print(
            f"prepare_synthsod_musicnet_fixture: expected at least {required_pieces} complete "
            f"SynthSOD pieces, got {len(complete)}",
            file=sys.stderr,
        )
        return 1

    shutil.rmtree(output_root, ignore_errors=True)
    prepared = 0
    failures = []
    for piece in complete:
        if prepared >= prepare_pieces:
            break
        ok, error = prepare_piece(piece, output_root, prepared + 1, ffmpeg)
        if ok:
            prepared += 1
        else:
            failures.append(f"{piece['path']}: {error}")

    if prepared < required_pieces:
        print(
            f"prepare_synthsod_musicnet_fixture: expected to prepare {required_pieces} "
            f"SynthSOD pieces, prepared {prepared}",
            file=sys.stderr,
        )
        for failure in failures[:10]:
            print(f"prepare_synthsod_musicnet_fixture: {failure}", file=sys.stderr)
        return 1

    print(
        f"prepare_synthsod_musicnet_fixture: wrote {prepared} MusicNet-shaped "
        f"summed-stem SynthSOD recordings to {output_root}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
