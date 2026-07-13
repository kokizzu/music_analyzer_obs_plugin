#!/usr/bin/env python3
import os
import shutil
import sys

import inspect_cocochorales_dataset
from prepare_slakh_musicnet_fixture import parse_midi_notes, prepare_summed_stem_audio, write_labels


def prepare_piece(piece, output_root, output_id, ffmpeg):
    stem_audio = piece["stem_audio"]
    if len(stem_audio) < 2:
        return False, "missing stem audio"

    try:
        notes = parse_midi_notes(piece["score_midi"], 64, track_stride=16)
    except ValueError as exc:
        return False, f"{piece['score_midi']}: {exc}"
    if not notes:
        return False, "no usable score MIDI notes"

    audio_out = inspect_cocochorales_dataset.join_path(output_root, "train_data", f"{output_id}.wav")
    label_out = inspect_cocochorales_dataset.join_path(output_root, "train_labels", f"{output_id}.csv")
    sample_rate = prepare_summed_stem_audio(stem_audio, audio_out, ffmpeg)
    write_labels(label_out, notes, sample_rate)
    return True, ""


def main(argv):
    if len(argv) != 2:
        print("usage: prepare_cocochorales_musicnet_fixture.py OUT_DIR", file=sys.stderr)
        return 2

    root = inspect_cocochorales_dataset.resolve_root()
    if not root:
        print(
            "prepare_cocochorales_musicnet_fixture: set MUSIC_ANALYZER_COCOCHORALES_ROOT, "
            "COCOCHORALES_PATH, or MUSIC_ANALYZER_DATASET_ROOT",
            file=sys.stderr,
        )
        return 1
    if not os.path.isdir(root):
        print(f"prepare_cocochorales_musicnet_fixture: `{root}` is not a directory", file=sys.stderr)
        return 1

    output_root = argv[1]
    required_pieces = inspect_cocochorales_dataset.positive_int_env(
        "MUSIC_ANALYZER_COCOCHORALES_REQUIRED_PIECES", 20
    )
    prepare_pieces = inspect_cocochorales_dataset.positive_int_env(
        "MUSIC_ANALYZER_COCOCHORALES_PREPARE_PIECES", required_pieces
    )
    min_stems = inspect_cocochorales_dataset.positive_int_env("MUSIC_ANALYZER_COCOCHORALES_MIN_STEMS", 4)
    min_audio_seconds = inspect_cocochorales_dataset.positive_float_env(
        "MUSIC_ANALYZER_COCOCHORALES_MIN_AUDIO_SECONDS", 1.0
    )
    max_depth = inspect_cocochorales_dataset.positive_int_env("MUSIC_ANALYZER_COCOCHORALES_MAX_DEPTH", 7)
    ffmpeg = os.environ.get("FFMPEG") or os.environ.get("MUSIC_ANALYZER_COCOCHORALES_FFMPEG") or "ffmpeg"

    inspected = [
        inspect_cocochorales_dataset.inspect_piece_dir(path, min_stems, min_audio_seconds)
        for path in inspect_cocochorales_dataset.candidate_piece_dirs(root, max_depth=max_depth)
    ]
    complete = [piece for piece in inspected if piece["complete"]]
    if len(complete) < required_pieces:
        print(
            f"prepare_cocochorales_musicnet_fixture: expected at least {required_pieces} complete "
            f"CocoChorales pieces, got {len(complete)}",
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
            f"prepare_cocochorales_musicnet_fixture: expected to prepare {required_pieces} "
            f"CocoChorales pieces, prepared {prepared}",
            file=sys.stderr,
        )
        for failure in failures[:10]:
            print(f"prepare_cocochorales_musicnet_fixture: {failure}", file=sys.stderr)
        return 1

    print(
        f"prepare_cocochorales_musicnet_fixture: wrote {prepared} MusicNet-shaped "
        f"summed-stem CocoChorales recordings to {output_root}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
